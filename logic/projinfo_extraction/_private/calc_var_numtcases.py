from typing import Dict
from .calc_avg_numtcases import avg_proj_numtcases


def var_proj_numtcases(loc_bymodule: Dict[str, int]) -> float:
    """
        Calcola la varianza del numero di test cases, tra ogni modulo,
        di un progetto dato il dizionario contenente il numero di test
        cases per ogni modulo del progetto.
    """
    avg_tcases: float = avg_proj_numtcases(loc_bymodule)
    sum_tcases: float = 0
    i: int = 0
    for _, numtcases in loc_bymodule.items():
        sum_tcases += ((numtcases - avg_tcases ) ** 2)
        i += 1

    return sum_tcases/i