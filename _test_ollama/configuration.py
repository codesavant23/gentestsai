from typing import Dict
from base64 import b64encode as b64_encode
from re import search as reg_search
from os import mkdir
from os.path import exists as dir_exists, join as path_join


def configure_ollama(
        api_url: str,
        userpass_pair: str,
        llm_model: str,
        old_config: Dict[str, str]=None
) -> Dict[str, str]:
    """
        <Descrizione>

        Parameters
        ----------
        api_url: str
            Una stringa contenente l' URL (URI:Port) a cui è hostata l' istanza di Ollama con cui si effettueranno le
            interazioni

        userpass_pair: str
            Una stringa contenente la coppia username e password (User:Pass) utilizzati come credenziali di

        llm_model: str
            Una stringa contenente la coppia "modello:implementazione"

        old_config: Dict[str, str]
            Opzionale.
            Un dizionario di stringhe, indicizzato su stringhe, contenente la configurazione
            a cui aggiungere le informazioni senza creare un nuovo dizionario di configurazione.

        Returns
        -------
        Dict[str, str]
            Un dizionario di stringhe, indicizzato su stringhe, contenente (sicuramente):

                - "model": La stringa identificante il modello da utilizzare
                - "api_url": L' URL per l' accesso alla specifica istanza di Ollama hostata
                             utilizzata dallo script.
                - "api_auth": Le credenziali di autorizzazione codificate e utilizzabili
                              per accedere all' API di Ollama (da utilizzarsi come valore
                              dell' header "Authorization")

    """
    model_patt: str = r"^[a-zA-z0-9\.\-_]+(?:\:[a-zA-z0-9\.\-_]+)?$"
    if reg_search(model_patt, llm_model) is None:
        raise ValueError("La coppia modello:tag data è malformata o invalida")

    config: Dict[str, str]
    if old_config is not None:
        config = old_config
    else:
        config = dict()

    config["model"] = llm_model

    config["api_url"] = "http://" + api_url
    config["api_auth"] = f'Basic {b64_encode(userpass_pair.encode()).decode()}'

    return config

    # config["focalmod_path"] = path_join(base_dir, input("Inserire il nome del modulo Python (con estensione .py) di cui generare i tests (Directory base: "+base_dir+") :>  "))
    # chosen_model: str = input("Inserire la coppia modello:tag per selezionare il LLM da utilizzare :>  ")


def configure_dirs(
        prompts_root: str,
        tests_root: str,
        old_config: Dict[str, str]=None
) -> Dict[str, str]:
    """
        <Descrizione>

        Parameters
        ----------
        prompts_root: str
            Una stringa contenente la path della directory dei prompts da utilizzare

        proj_root: str
            Una stringa contenente la path della root directory del progetto in esame

        tests_dir: str
            Una stringa contenente il nome della sotto-directory (di 'proj_root') che conterrà
            i tests generati

        old_config: Dict[str, str]
            Opzionale.
            Un dizionario di stringhe, indicizzato su stringhe, contenente la configurazione
            a cui aggiungere le informazioni senza creare un nuovo dizionario di configurazione.

        Returns
        -------
        Dict[str, str]
            Un dizionario di stringhe, indicizzato su stringhe, contenente (sicuramente):

                - "prompts_dir": La sotto-directory della base che contiene i template dei prompt.
                - "gentests_dir": La sotto-directory della base che conterrà i tests generati.
    """

    config: Dict[str, str]
    if old_config is not None:
        config = old_config
    else:
        config = dict()

    config["prompts_dir"] = prompts_root
    config["gentests_dir"] = tests_root

    if not dir_exists(config["gentests_dir"]):
        mkdir(config["gentests_dir"])

    return config