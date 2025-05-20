from typing import Dict


def avg_proj_numtcases(tcases_bymodule: Dict[str, int]) -> float:
    """
        Calcola il numero di test cases medio, in ogni modulo,
        di un progetto dato il dizionario contenente il numero di
        test cases per ogni modulo del progetto
    """
    sum_tcases: float = 0
    i: int = 0
    for _, numtcases in tcases_bymodule.items():
        sum_tcases += numtcases
        i += 1

    return sum_tcases/i