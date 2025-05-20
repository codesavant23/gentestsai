from typing import Dict
from ._calc_avg_loc import avg_projloc


def var_projloc(loc_bymodule: Dict[str, int]) -> float:
    """
        Calcola la varianza di LOC di un progetto dato il dizionario
        contenente i LOC per ogni modulo del progetto
    """
    avg_loc: float = avg_projloc(loc_bymodule)
    sum_loc: float = 0
    i: int = 0
    for _, loc in loc_bymodule.items():
        sum_loc += ((loc - avg_loc ) ** 2)
        i += 1

    return sum_loc/i
