from typing import Dict


def avg_projloc(loc_bymodule: Dict[str, int]) -> float:
    """
        Calcola il LOC medio di un progetto dato il dizionario
        contenente i LOC per ogni modulo del progetto
    """
    sum_loc: float = 0
    i: int = 0
    for _, loc in loc_bymodule.items():
        sum_loc += loc
        i += 1

    return sum_loc/i