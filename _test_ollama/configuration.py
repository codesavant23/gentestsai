from typing import Dict
from re import search as reg_search
from os import mkdir
from os.path import exists as dir_exists, join as path_join


def configure_script(base_dir: str, prompts_dir: str = "_prompts", gentests_dir: str = "tests") -> Dict[str, str]:
    """
        TODO: Finish description

        Returns
        -------
        Dict[str, str]
            Un dizionario di stringhe, indicizzato su stringhe, contenente:

                - "base_dir": La directory di partenza (base) utilizzata dallo script.
                - "prompts_dir": La sotto-directory della base che contiene i template dei prompt.
                - "gentests_dir": La sotto-directory della base che conterrà i tests generati.
                - "api_url": L' URL completo per l' accesso alla specifica operazione, dell' API,
                             utilizzata dallo script.
                - "focalmod_path": La path che identifica il modulo di cui generare i tests.
                - "model": La stringa identificante il modello da utilizzare
    """
    config: Dict[str, str] = dict()

    config["base_dir"] = base_dir
    config["prompts_dir"] = path_join(base_dir, prompts_dir)
    config["gentests_dir"] = path_join(base_dir, gentests_dir)

    if not dir_exists(config["gentests_dir"]):
        mkdir(config["gentests_dir"])

    userpass_pair: str = "ollama:3UHn2uyu1sxgAy15"
    base_api: str = "158.110.146.224:1337"
    action: str = "/api/chat"
    config["api_url"] = "http://" + userpass_pair + "@" + base_api + action

    config["focalmod_path"] = path_join(base_dir, input("Inserire il nome del modulo Python (con estensione .py) di cui generare i tests (Directory base: "+base_dir+") :>  "))
    chosen_model: str = input("Inserire la coppia modello:tag per selezionare il LLM da utilizzare :>  ")
    model_patt: str = r"^[a-zA-z0-9\.\-_]+(?:\:[a-zA-z0-9\.\-_]+)?$"
    if reg_search(model_patt, chosen_model) is None:
        raise ValueError("La coppia modello:tag data è malformata o invalida")
    config["model"] = chosen_model

    return config