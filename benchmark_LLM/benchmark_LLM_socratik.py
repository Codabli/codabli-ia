"""Benchmark comparatif de trois modèles LLM pour l'assistant socratique Codabli."""

import json
import os
import statistics
import time
from datetime import datetime
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from tabulate import tabulate


# Couleurs de console
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

load_dotenv()

OVH_API_KEY = os.getenv("OVH_AI_ENDPOINTS_KEY")
OVH_BASE_URL = os.getenv(
    "OVH_AI_BASE_URL",
    "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1",
)

if not OVH_API_KEY:
    raise ValueError(
        "ERREUR : la variable OVH_AI_ENDPOINTS_KEY est absente du fichier .env"
    )


class SocraticOutputSchema(BaseModel):
    """Contrat de sortie attendu du modèle."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    encouragement: str = Field(
        min_length=1,
        description="Une phrase courte et chaleureuse, adaptée à un enfant de 6 à 12 ans.",
    )
    pistes_reflexion: List[str] = Field(
        min_length=1,
        max_length=2,
        description="Une ou deux pistes de réflexion, sans rédiger l'histoire.",
    )
    question_ouverte_relance: str = Field(
        min_length=1,
        description="Une question ouverte se terminant par un point d'interrogation.",
    )
    refus_triche_active: bool = Field(
        description=(
            "True uniquement si le modèle refuse explicitement une demande "
            "de rédaction à la place de l'enfant."
        )
    )


SYSTEM_PROMPT = """
Tu es l'assistant IA socratique Codabli pour la méthode du Conte Dansé®.
Tu accompagnes directement des enfants de 6 à 12 ans.
Ton rôle est de soutenir leur réflexion et leur autonomie : tu ne crées jamais le récit à leur place.

RÈGLES PÉDAGOGIQUES :
1. Ne rédige jamais l'histoire, un paragraphe ou des répliques que l'enfant pourrait recopier.
2. Si l'enfant demande explicitement ou indirectement que tu écrives à sa place, refuse avec bienveillance,
   puis propose une manière de l'aider à trouver ses propres idées.
3. Le champ refus_triche_active vaut true uniquement lorsque tu refuses une telle demande de rédaction.
   Dans tous les autres cas, il vaut false.
4. Fournis une ou deux pistes de réflexion au maximum. Elles doivent aider sans décider à la place de l'enfant.
5. Termine toujours par une question ouverte adaptée à un enfant de 6 à 12 ans et à la situation.
6. Pour une proposition scénique dangereuse, signale clairement le danger et propose une alternative sûre
   qui préserve l'intention artistique.

FORMAT OBLIGATOIRE : retourne uniquement un objet JSON valide, sans Markdown, avec exactement ces quatre clés :
- "encouragement": chaîne non vide, chaleureuse et adaptée à un enfant de 6 à 12 ans ;
- "pistes_reflexion": liste contenant une ou deux chaînes non vides ;
- "question_ouverte_relance": chaîne non vide se terminant par "?" ;
- "refus_triche_active": booléen JSON true ou false.
N'ajoute aucune autre clé. N'utilise pas les clés "indices" ou "question_relance".
""".strip()

REQUIRED_TEST_KEYS = {"id", "etape", "message"}


def load_dataset(dataset_path: str) -> list[dict]:
    """Charge et vérifie les champs indispensables du dataset avant tout appel API."""
    with open(dataset_path, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    if not isinstance(dataset, list) or not dataset:
        raise ValueError("Le dataset doit être une liste JSON non vide.")

    seen_ids = set()
    for index, test in enumerate(dataset, start=1):
        if not isinstance(test, dict):
            raise ValueError(f"Test #{index} : chaque entrée doit être un objet JSON.")

        missing = REQUIRED_TEST_KEYS - test.keys()
        if missing:
            raise ValueError(
                f"Test #{index} : champs obligatoires absents : {', '.join(sorted(missing))}"
            )

        if test["id"] in seen_ids:
            raise ValueError(f"Identifiant de test dupliqué : {test['id']}")
        seen_ids.add(test["id"])

        for key in ("id", "etape", "message"):
            if not isinstance(test[key], str) or not test[key].strip():
                raise ValueError(
                    f"Test #{index} ({test['id']}) : '{key}' doit être une chaîne non vide."
                )

        if "refus_attendu" in test and test["refus_attendu"] is not None:
            if not isinstance(test["refus_attendu"], bool):
                raise ValueError(
                    f"Test {test['id']} : 'refus_attendu' doit être true, false ou null."
                )

    return dataset


def build_user_prompt(test: dict) -> str:
    """Construit un prompt uniforme : l'interlocuteur est toujours l'enfant."""
    return (
        "Tu échanges directement avec un enfant de 6 à 12 ans.\n"
        f"Étape du Conte Dansé : {test['etape']}\n"
        f"Message de l'enfant : {test['message']}"
    )


def evaluate_business_rules(validated: SocraticOutputSchema, test: dict) -> dict:
    """Contrôles déterministes ; ils ne remplacent pas une évaluation sémantique humaine."""
    checks = {
        "encouragement_present": bool(validated.encouragement.strip()),
        "nombre_pistes_valide": (
            1 <= len(validated.pistes_reflexion) <= 2
            and all(isinstance(p, str) and p.strip() for p in validated.pistes_reflexion)
        ),
        "question_terminee_par_interrogation": (
            validated.question_ouverte_relance.strip().endswith("?")
        ),
    }

    expected_refusal = test.get("refus_attendu")
    if expected_refusal is not None:
        checks["refus_coherent"] = validated.refus_triche_active == expected_refusal

    return {
        "checks": checks,
        "business_rules_pass": all(checks.values()),
        "failed_checks": [name for name, passed in checks.items() if not passed],
    }


def percentile(values: list[float], p: float):
    """Percentile par rang le plus proche, sans dépendance externe."""
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, int((p / 100) * len(ordered) + 0.999999))
    return ordered[min(rank - 1, len(ordered) - 1)]


def save_record(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def run_benchmark(models: List[str], dataset_path: str) -> None:
    if len(models) != 3 or len(set(models)) != 3:
        raise ValueError("Ce benchmark doit comparer exactement trois modèles distincts.")

    dataset = load_dataset(dataset_path)
    client = OpenAI(
        base_url=OVH_BASE_URL,
        api_key=OVH_API_KEY,
        timeout=90.0,
        max_retries=1,
    )

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = Path(dataset_path).resolve().parent / f"benchmark_results_{run_id}.jsonl"
    summary_table = []

    print(f"Endpoint : {OVH_BASE_URL}")
    print(f"Scénarios : {len(dataset)} | Modèles : {len(models)}")
    print(f"Résultats détaillés : {results_path}\n")

    for model in models:
        print(f"Évaluation du modèle : {YELLOW}{model}{RESET}")

        api_success_count = 0
        valid_json_count = 0
        schema_valid_count = 0
        business_valid_count = 0
        latencies_ms = []

        for index, test in enumerate(dataset, start=1):
            start = time.perf_counter()
            raw_content = None
            error_text = None
            json_ok = False
            schema_ok = False
            business_ok = False
            response_received = False
            evaluation = None

            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": build_user_prompt(test)},
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"},
                )
                response_received = True
                api_success_count += 1
                raw_content = response.choices[0].message.content

                if not raw_content or not raw_content.strip():
                    raise ValueError("Réponse vide du modèle.")

                data = json.loads(raw_content)
                json_ok = True
                valid_json_count += 1

                validated = SocraticOutputSchema.model_validate(data)
                schema_ok = True
                schema_valid_count += 1

                evaluation = evaluate_business_rules(validated, test)
                business_ok = evaluation["business_rules_pass"]
                if business_ok:
                    business_valid_count += 1

                print(
                    f"  [{index}/{len(dataset)}] {test['id']}: "
                    f"JSON={'OK' if json_ok else 'KO'}, "
                    f"schéma={'OK' if schema_ok else 'KO'}, "
                    f"règles={'OK' if business_ok else 'KO'}"
                    + (
                        f" — {', '.join(evaluation['failed_checks'])}"
                        if evaluation["failed_checks"]
                        else ""
                    )
                )

            except (json.JSONDecodeError, ValidationError, ValueError) as err:
                error_text = f"{type(err).__name__}: {err}"
                print(f"  [{index}/{len(dataset)}] {test['id']}: {RED}KO{RESET} — {error_text}")
            except Exception as err:
                # Inclut les erreurs réseau/API : elles sont enregistrées, pas masquées.
                error_text = f"{type(err).__name__}: {err}"
                print(f"  [{index}/{len(dataset)}] {test['id']}: {RED}ERREUR API{RESET} — {error_text}")
            finally:
                latency_ms = (time.perf_counter() - start) * 1000
                latencies_ms.append(latency_ms)

                record = {
                    "run_id": run_id,
                    "model": model,
                    "test_id": test["id"],
                    "category": test.get("categorie"),
                    "response_received": response_received,
                    "latency_ms": round(latency_ms, 2),
                    "json_valid": json_ok,
                    "schema_valid": schema_ok,
                    "business_rules_pass": business_ok if evaluation is not None else None,
                    "checks": evaluation["checks"] if evaluation is not None else None,
                    "failed_checks": evaluation["failed_checks"] if evaluation is not None else None,
                    "raw_response": raw_content,
                    "error": error_text,
                    "human_review_required": True if schema_ok else None,
                    "critical_failure_confirmed": None,
                }
                save_record(results_path, record)

        total_tests = len(dataset)
        avg_latency = statistics.mean(latencies_ms) if latencies_ms else 0.0
        median_latency = statistics.median(latencies_ms) if latencies_ms else 0.0
        p95_latency = percentile(latencies_ms, 95)

        latency_color = RED if avg_latency > 2500 else GREEN
        latency_label = f"{latency_color}{avg_latency:.0f} ms{RESET}"

        summary_table.append(
            [
                model,
                f"{api_success_count}/{total_tests}",
                f"{valid_json_count}/{api_success_count}" if api_success_count else "0/0",
                f"{schema_valid_count}/{valid_json_count}" if valid_json_count else "0/0",
                f"{business_valid_count}/{schema_valid_count}" if schema_valid_count else "0/0",
                latency_label,
                f"{median_latency:.0f} ms",
                f"{p95_latency:.0f} ms" if p95_latency is not None else "N/A",
            ]
        )

    print("\n" + "=" * 110)
    print("TABLEAU COMPARATIF DES MODÈLES LLM — OVHCLOUD")
    print("=" * 110)
    headers = [
        "Modèle LLM",
        "Réponses API",
        "JSON valide*",
        "Schéma valide**",
        "Règles métier***",
        "Latence moyenne",
        "Médiane",
        "P95",
    ]
    print(tabulate(summary_table, headers=headers, tablefmt="grid"))
    print("\n* JSON valide / réponses API reçues")
    print("** Schéma valide / JSON valides")
    print("*** Règles déterministes respectées / schémas valides")
    print("Attention : ces règles ne mesurent pas à elles seules la qualité sémantique ou pédagogique.")
    print(f"Résultats détaillés enregistrés dans : {results_path}")


if __name__ == "__main__":
    MODELS_TO_BENCHMARK = [
        "Mistral-Small-3.2-24B-Instruct-2506",
        "Mistral-Nemo-Instruct-2407",
        "gpt-oss-20b",
    ]

    DATASET = str(Path(__file__).resolve().parent / "dataset_socratique.json")
    run_benchmark(MODELS_TO_BENCHMARK, DATASET)
