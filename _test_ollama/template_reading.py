from typing import Dict, Tuple
from functools import reduce


def read_templ_frompath(templ_path: str) -> str:
    """
        Legge un template per prompt da un file a caratteri

        Returns
        -------
        str
            Una stringa contenente il template del prompt da parsare
            per essere arricchito e creare quindi un prompt completo.
    """
    templ: str
    with open(templ_path, "r") as ftempl:
        templ = reduce(lambda acc, x: acc + x, ftempl.readlines(), "")
    return templ


def extract_templs(
        templs_paths: Tuple[Tuple[str,str],Tuple[str,str]]
) -> Dict[str, str]:
    """
        TODO: Finish description

        Parameters
        ----------
        templs_paths: Tuple[Tuple[str,str],Tuple[str,str]]
            Una tupla di 2 tuple di stringhe contenente in quest' ordine le paths
            dei templates di prompt:
                - [0][0] = Path per il template dell' Informational Prompt per Funzioni
                - [0][1] = Path per il template dell' Task Prompt per Funzioni
                - [1][0] = Path per il template dell' Informational Prompt per Classi
                - [1][1] = Path per il template dell' Task Prompt per Classi

        Returns
        -------
        Dict[str, str]
            Un dizionario di stringhe multi-linea, indicizzato a stringhe, contenente i template
            dei prompt da utilizzare per la generazione dei test:

                - "funcs_infop": Informational Prompt per Funzioni
                - "funcs_taskp": Task Prompt per Funzioni
                - "clss_infop": Informational Prompt per Classi
                - "clss_taskp": Task Prompt per Classi
    """
    prompt_templs: Dict[str, str] = dict()

    infoprompt_funcs_path: str = templs_paths[0][0]
    taskprompt_funcs_path: str = templs_paths[0][1]
    infoprompt_clss_path: str = templs_paths[1][0]
    taskprompt_clss_path: str = templs_paths[1][1]

    # ========== Lettura dei Template di Prompt per Funzioni proprie del Modulo (Informational e Task) ==========
    infoprompt_templ_funcs: str = read_templ_frompath(infoprompt_funcs_path)
    taskprompt_templ_funcs: str = read_templ_frompath(taskprompt_funcs_path)

    # ========== Lettura dei Template di Prompt per Metodi delle Classi (Informational e Task) ==========
    infoprompt_templ_clss: str = read_templ_frompath(infoprompt_clss_path)
    taskprompt_templ_clss: str = read_templ_frompath(taskprompt_clss_path)

    prompt_templs["funcs_infop"] = infoprompt_templ_funcs
    prompt_templs["funcs_taskp"] = taskprompt_templ_funcs
    prompt_templs["clss_infop"] = infoprompt_templ_clss
    prompt_templs["clss_taskp"] = taskprompt_templ_clss

    return prompt_templs