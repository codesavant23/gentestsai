from typing import List, Dict
from functools import reduce
from re import search as reg_search
from re import findall as reg_findall
from re import IGNORECASE as REG_IGNORECASE
import io
import os


def count_modtcases(proj_path: str) -> Dict[str, int]:
    """
        Calcola il dizionario di no. test cases per ogni modulo di un progetto data
        la sua root path.

        Vengono considerate soltanto le directories che contengono le stringhe "test"/
        "_test"/"tests"/"_tests" (e le sub-directories in esse contenute).
        Le stringhe si considerano tutte e 4 case-insensitive.

        Viene considerato come modulo di testing ogni file .py (NON SPECIALE) o l' intera directory
        se esse contiene un file "__init__.py".
        Nel secondo caso le informazioni saranno aggregate per l' intero "modulo-cartella" ("package" in Python)
    """
    result: Dict[str, int] = dict()
    stack: List[str] = [proj_path]

    folder: str = ""
    curr_cases: int = 0
    mod_cases: int = 0
    folder_files: List[str]
    folder_modules: List[str] = []
    next_dirs: List[str] = []

    # Finché tutte le directory di progetto presenti non sono state visitate
    while not (len(stack) == 0):
        # Prendo la prossima directory
        folder = stack.pop()

        # Se è una directory considerata contenere test cases
        if reg_search(r'_?tests?', folder, REG_IGNORECASE):
            # Allora prendo la lista dei files contenuti in essa
            folder_files = os.listdir(folder)

            # Verifico se la directory è un modulo singolo (con all' interno sotto-moduli)
            # o un "package" contenente più moduli separati.
            # Dunque verifico se ci sia un file "__init__.py" in questa directory
            is_foldermodule: bool = reduce(
                lambda acc, x:
                    acc or reg_search(r"^__init__\.py$", x),
                folder_files,
                False
            )

            # Scorro ogni file della directory, cercando quelli con estensione .py
            # pubblici o privati ma non speciali
            for file in folder_files:
                if reg_search(r'^_?[a-zA-Z0-9_\-{}\[\]]+\.py$', file):
                    folder_modules.append(os.path.join(folder, file))

            # Per ogni file con estensione .py, pubblico o privato, trovato conto il
            # numero di test cases da cui è composto
            mod_cases = 0
            for module in folder_modules:
                curr_cases = 0

                with io.open(module, "r", encoding="UTF-8") as fp:
                    fp_lines: List[str] = fp.readlines()
                    file_str: str = reduce(
                        lambda acc, x:
                            acc + x,
                        fp_lines,
                        ""
                    )

                    test_case_pattern = r"(?P<function>def\s+(?P<function_name>(?:test[a-zA-Z0-9_-]*|[a-zA-Z0-9_-]*test))\s*\((?P<parameters>(?:.|\n)*?)\)\s*(?:->\s*[a-zA-Z0-9\[\]]+)?:\s*(?:\n[ \t]+.*?)*\n)"
                    test_cases: List[str] = reg_findall(test_case_pattern, file_str, REG_IGNORECASE)
                    curr_cases = len(test_cases)

                    del file_str
                    del fp_lines

                # Se il file .py era da considerarsi un modulo autonomo
                if not is_foldermodule:
                    # Allora lo aggiungo al dizionario con il numero dei test cases che contiene
                    result[module] = curr_cases
                else:
                    # Sennò cumulo il conto dei test cases finchè non ho terminato tutti
                    # i file .py in questa cartella (la quale è un modulo singolo)
                    mod_cases += curr_cases

            # Se l' intera directory era da considerarsi un modulo singolo
            if is_foldermodule:
                # Allora la aggiungo al dizionario con il suo relativo LOC
                result[folder] = mod_cases
            folder_modules = []

        # Calcolo le nuove cartelle da visitare
        subfolders: List[str] = [entity.path for entity in os.scandir(folder) if entity.is_dir()]
        for subfolder in subfolders:
            next_dirs.append(subfolder)
        stack = stack + next_dirs
        next_dirs = []

    return result