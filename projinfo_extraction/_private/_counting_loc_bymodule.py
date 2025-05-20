from typing import List, Dict
from functools import reduce
from re import search as reg_search
from re import IGNORECASE as REG_IGNORECASE
import io
import os


def calc_modloc(proj_path: str) -> Dict[str, int]:
    """
        Calcola il dizionario di LOCs per ogni modulo di un progetto data
        la sua root path.

        Vengono considerate soltanto le directories che non contengono le stringhe "test"/
        "_test"/"tests"/"_tests" e "examples" (e le sub-directories in esse contenute).
        Le stringhe si considerano tutte e 5 case-insensitive.

        Viene considerato come modulo di progetto ogni file .py (NON SPECIALE) a patto che esso
        non si trovi in una directory contenente un file "__init__.py". In quel caso si considera
        l' intera cartella come modulo di progetto che contiene sotto-moduli in file .py (le quali
        informazioni saranno aggregate nel calcolo delle informazioni del "modulo-cartella")
    """
    result: Dict[str, int] = dict()
    stack: List[str] = [proj_path]

    folder: str = ""
    curr_loc: int = 0
    mod_loc: int = 0
    folder_files: List[str]
    folder_modules: List[str] = []
    next_dirs: List[str] = []

    # Finché tutte le directory di progetto presenti non sono state visitate
    while not (len(stack) == 0):
        # Prendo la prossima directory
        folder = stack.pop()

        # Se non è una directory considerata contenere test cases o esempi
        if not reg_search(r'(_?tests?|examples)', folder, REG_IGNORECASE):
            # Allora prendo la lista dei files contenuti in essa
            folder_files = os.listdir(folder)

            # Verifico se la directory è un modulo singolo (con all' interno sotto-moduli)
            # o un "package" contenente più moduli separati.
            # Dunque verifico se ci sia un file "__init__.py" in questa directory
            is_foldermodule: bool = reduce(
                lambda acc, x:
                    (acc or reg_search(r"^__init__\.py$", x)),
                folder_files,
                False
            )

            # Scorro ogni file della directory, cercando quelli con estensione .py
            # pubblici o privati ma non speciali
            for file in folder_files:
                if reg_search(r'^_?[a-zA-Z0-9_\-{}\[\]]+\.py$', file):
                    folder_modules.append(os.path.join(folder, file))

            # Per ogni file con estensione .py, pubblico o privato, trovato conto il
            # numero di linee da cui è composto
            mod_loc = 0
            for module in folder_modules:
                curr_loc = 0
                with io.open(module, "r", encoding="UTF-8") as fp:
                    fp_lines: List[str] = fp.readlines()
                    for _ in fp_lines:
                        curr_loc += 1
                    del fp_lines

                # Se il file .py era da considerarsi un modulo autonomo
                if not is_foldermodule:
                    # Allora lo aggiungo al dizionario con il suo relativo LOC
                    result[module] = curr_loc
                else:
                    # Sennò cumulo il conto dei LOC finchè non ho terminato tutti
                    # i file .py in questa cartella
                    mod_loc += curr_loc

            # Se l' intera directory era da considerarsi un modulo singolo
            if is_foldermodule:
                # Allora la aggiungo al dizionario con il suo relativo LOC
                result[folder] = mod_loc
            folder_modules = []

        # Calcolo le nuove cartelle da visitare
        subfolders: List[str] = [entity.path for entity in os.scandir(folder) if entity.is_dir()]
        for subfolder in subfolders:
            next_dirs.append(subfolder)
        stack = stack + next_dirs
        next_dirs = []

    return result