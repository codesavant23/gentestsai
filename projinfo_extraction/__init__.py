"""
    Mini-componente python, sotto-forma di package, che permette il calcolo di alcune informazioni relative a progetti Python.

    Consente principalmente l' estrazione delle informazioni automaticamente tramite la funzione `extract_projsinfo` a cui viene
    fornita la path della directory contenente le cartelle dei progetti.

    Le funzionalità autonome/singole offerte sono:
        - Calcolo del numero di moduli presenti all' interno di un progetto
        - Calcolo del numero totale di test cases presenti all' interno di un progetto
        - Calcolo del LOC per ogni modulo di un progetto
        - Calcolo del numero di test cases per ogni modulo di un progetto
        - Calcolo della media di LOC di un progetto
        - Calcolo della varianza di LOC, tra moduli, di un progetto
        - Calcolo del numero medio di test cases di un progetto
        - Calcolo della varianza del numero di test cases, tra moduli, di un progetto
"""

from projinfo_extraction._private.counting_modules import count_modules
from projinfo_extraction._private.counting_loc_bymodule import calc_modloc
from projinfo_extraction._private.counting_numtcases_bymodule import count_modtcases
from projinfo_extraction._private.calc_avg_loc import avg_projloc
from projinfo_extraction._private.calc_var_loc import var_projloc
from projinfo_extraction._private.calc_tot_numtcases import tot_proj_numtcases
from projinfo_extraction._private.calc_avg_numtcases import avg_proj_numtcases
from projinfo_extraction._private.calc_var_numtcases import var_proj_numtcases
from projinfo_extraction._private.automatic_extraction import extract_projsinfo

# Defining exports for Whole-Package importing
__all__ = [
    "count_modules",
    "calc_modloc",
    "count_modtcases",
    "avg_projloc",
    "var_projloc",
    "tot_proj_numtcases",
    "avg_proj_numtcases",
    "var_proj_numtcases",
    "extract_projsinfo",
]