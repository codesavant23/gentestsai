from typing import Dict


def tot_proj_numtcases(tcases_bymodule: Dict[str, int]) -> int:
    """
        Calcola il numero totale di test cases nel progetto dato
        il dizionario contenente il numero di test cases per ogni
        modulo del progetto
    """
    result: int = 0
    for _, numtcases in tcases_bymodule.items():
        result += numtcases

    return result