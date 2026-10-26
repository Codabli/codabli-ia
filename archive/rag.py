from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
import os
from langchain.messages import SystemMessage, HumanMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import PyPDFDirectoryLoader, DirectoryLoader, TextLoader
from langchain_mistralai import ChatMistralAI


load_dotenv()

# Récupérer les variables
directory = os.getenv("DIRECTORY")
OVH_API_KEY = os.getenv("OVH_AI_ENDPOINT_API_KEY")


model = ChatMistralAI(
    model="Mistral-Small-3.2-24B-Instruct-2506",
    api_key=OVH_API_KEY,
    endpoint="https://oai.endpoints.kepler.ai.cloud.ovh.net/v1",
)

# Load Documents
pdf_loader = PyPDFDirectoryLoader(directory)
pdf_docs = pdf_loader.load()

text_loader = DirectoryLoader(directory,glob="**/*.txt", loader_cls=TextLoader)
text_docs = text_loader.load()

docs = pdf_docs + text_docs



# Creating embeddings and vector store
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = InMemoryVectorStore(embeddings)
vector_store.add_documents(docs)

while True:
    user_query = input('Enter your query :')
    retrieved_docs = vector_store.similarity_search(user_query, k=2)

    context = "\n".join(doc.page_content for doc in retrieved_docs)

    system_prompt = f"""
    You are a helpful assistant that answers questions about these documents : {context}
    """

    message = [
        SystemMessage(content=system_prompt)
    ]
    message.append(HumanMessage(content=user_query))
    response = model.invoke(message)
    print(response)