import sys, os, json
from pathlib import Path
from typing import Dict, Any

_config = {
    "config": None
}


def load_config(config_type: str = 'config') -> Dict[str, Any]:
    """
    Load the configuration file and return the configuration for the specified type.

    Parameters:
        config_type (str): The type of configuration to load. Defaults to 'config'.

    Returns:
        Dict[str, Any]: A dictionary containing the configuration values for the specified type.
    """
    global _config

    if _config[config_type] is None:
        if getattr(sys, 'frozen', False):
            application_path = Path(sys.executable).parent.absolute()
        elif __file__:
            application_path = Path(__file__).parent.parent.absolute()
        else:
            raise BaseException("Error getting application path")

        config_path = os.path.join(application_path, "config", f"{config_type}.json")
        
        with open(config_path) as f:
            _config[config_type] = json.load(f)

        for key, value in _config[config_type].items():
            if key.endswith('path'):
                _config[config_type][key] = os.path.join(application_path.absolute(), value)

    return _config[config_type]