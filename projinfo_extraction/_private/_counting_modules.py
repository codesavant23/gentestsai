from typing import List, Iterator, Tuple
from functools import reduce
from os import walk, listdir
from re import search as reg_search
from re import IGNORECASE as REG_IGNORECASE


def count_modules(proj_path: str) -> int:
    """
        Conta il numero di moduli di un progetto data la sua root path.
        Vengono considerate soltanto le directories che non contengono le stringhe "test"/
        "_test"/"tests"/"_tests" e "examples" (e le sub-directories in esse contenute).
        Le stringhe si considerano tutte e 5 case-insensitive.

        Viene considerato come modulo di progetto ogni file .py escludendo ogni file .py che inizi con "__".

        La funzione dunque non considera un modulo strutturato con le sue funzionalità
        in più file .py, nella stessa cartella, come un unico modulo di progetto.
    """
    tot_modules: int = 0
    stack: List[str] = [proj_path]

    folder: str
    folder_modules: List[str] = []
    folder_files: List[str]
    next_dirs: List[str] = []

    # Finché tutte le directory di progetto presenti non sono state visitate
    while not (len(stack) == 0):
        # Prendo la prossima directory
        folder = stack.pop()

        # Se non è una directory considerata contenere test cases o esempi
        if not reg_search(r'(_?tests?|examples)', folder, REG_IGNORECASE):
            folder_files = listdir(folder)

            # Verifico se la directory è un modulo singolo (con all' interno sotto-moduli)
            # o un "package" contenente più moduli separati.
            # Dunque verifico se ci sia un file "__init__.py" in questa directory
            is_foldermod: bool = reduce(
                lambda acc, x:
                    (acc or reg_search(r"^__init__\.py$", x)),
                folder_files,
                False
            )

            # Se l' intera directory è un "package di moduli" contenente più moduli separati/autonomi
            if not is_foldermod:
                # Allora scorro ogni file della directory, cercando quelli con estensione .py
                # pubblici o privati ma non speciali
                for file in folder_files:
                    if reg_search(r'^_?[a-zA-Z0-9_\-{}\[\]]+\.py$', file):
                        # E per ognuno trovato lo aggiungo ai moduli della cartella
                        folder_modules.append(file)
            else:
                # Sennò se l' intera directory è modulo singolo allora aggiungo una
                # costante (stringa) speciale alla lista di moduli della directory
                folder_modules.append("_1_")

            # Conto i moduli contenuti/corrispondenti nella/alla directory
            tot_modules += len(folder_modules)
            folder_modules = []

        # Calcolo le nuove cartelle da visitare
        subfolders: Iterator[Tuple[str, List[str], List[str]]] = walk(folder)
        next(subfolders)
        for t_folder in subfolders:
            next_dirs.append(t_folder[0])
        stack = stack + next_dirs
        next_dirs = []

    return tot_modules