from typing import List, Tuple, Dict
from os import scandir as os_scandir
from os.path import sep as os_sep
from re import search as reg_search
from pprint import pprint

from .counting_modules import count_modules
from .calc_tot_numtcases import tot_proj_numtcases
from .counting_numtcases_bymodule import count_modtcases
from .counting_loc_bymodule import calc_modloc
from .calc_avg_loc import avg_projloc
from .calc_var_loc import var_projloc
from .calc_avg_numtcases import avg_proj_numtcases
from .calc_var_numtcases import var_proj_numtcases


def extract_projsinfo(projs_root: str) -> Dict[str,Tuple[int,int,float,float,float,float]]:
    """
        Estrae alcune informazioni relative ai progetti contenuti nella directory
        alla path data.

        Le informazioni estratte sono memorizzate in un dizionario indicizzato tramite
        i nomi dei progetti rilevati dal nome di ogni loro directory root.

        Il dizionario contiene, per ognuno, una tupla con le seguenti informazioni
            - [0]: int = Numero di moduli in totale nel progetto
            - [1]: int = Numero di test cases in totale nel progetto
            - [2]: float = Media di LOC del progetto
            - [3]: float = Varianza di LOC, tra moduli, del progetto
            - [4]: float = Numero medio di test cases del progetto
            - [5]: float = Varianza del numero di test cases, tra moduli, del progetto
    """
    projs_info: Dict[
        str, Tuple[
            int,
            int,
            float,
            float,
            float,
            float
        ]
    ] = dict()

    projects: List[str] = [entity.path for entity in os_scandir(projs_root.rstrip(os_sep)) if entity.is_dir()]

    print()
    print(str(len(projects))+" progetti trovati:")
    print()
    pprint(list(projects))
    print("\n")

    for proj_root in projects:
        proj_name: str = reg_search(r"[/\\]([a-zA-Z0-9\-_{}\[\]]+)$", proj_root).group(1)
        print("Estraendo informazioni dal progetto '"+proj_root+"' ...")

        tcases_bymod: Dict[str, int] = count_modtcases(proj_root)
        loc_bymod: Dict[str, int] = calc_modloc(proj_root)

        tot_modules: int = count_modules(proj_root)
        tot_tcases: int = tot_proj_numtcases(tcases_bymod)

        proj_avgloc: float = avg_projloc(loc_bymod)
        proj_varloc: float = var_projloc(loc_bymod)
        proj_avgtcases: float = avg_proj_numtcases(tcases_bymod)
        proj_vartcases: float = var_proj_numtcases(tcases_bymod)

        print("OK! Estrazione delle informazioni di '"+proj_name+"' completata")

        projs_info[proj_name] = (
            tot_modules,
            tot_tcases,
            proj_avgloc,
            proj_varloc,
            proj_avgtcases,
            proj_vartcases
        )

    return projs_info