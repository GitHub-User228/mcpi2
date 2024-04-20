import yaml
from pathlib import Path

from mcpi2 import logger



def read_yaml(path_to_yaml: Path, 
              verbose: bool = True) -> dict:
    """
    Reads a yaml file, and returns a ConfigBox object.

    Paramgeters:
        path_to_yaml (Path): Path to the yaml file.
        verbose (bool): Whether to show logger's messages.

    Raises:
        e: If any exception occurs.

    Returns:
        content (dict): The yaml content as a dict.
    """
    try:
        with open(path_to_yaml) as yaml_file:
            content = yaml.safe_load(yaml_file)
            if verbose: logger.info(f"yaml file: {path_to_yaml} loaded successfully")
            return content
    except Exception as e:
        logger.info(f"An exception {e} has occurred")
        raise e
