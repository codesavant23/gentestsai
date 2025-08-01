from typing import Dict, List, Tuple
from functools import reduce

from os import (
    walk as os_walk,
    mkdir as os_mkdir,
)
from shutil import (
    rmtree as os_dremove
)
from os.path import (
    exists as os_fdexists,
    sep as path_sep,
    commonpath as path_intersect,
    join as path_join,
    splitext as path_split_ext
)

from json import (
    load as json_load,
    loads as json_loads
)

from re import (
    Match,
    search as reg_search,
)

from tree_sitter import Language, Parser, Tree
from tree_sitter_python import language as py_grammar

from configuration import (
    configure_ollama,
    configure_dirs
)
from template_reading import read_templ_frompath
from code_extraction import (
    extract_fmodule_code,
    separate_fmodule_code,

)
from chat_history import ChatHistory

from script_core.tsuite_fbyf_generation import (
    generate_tsuite_modfuncs,
    generate_tsuite_testclss
)

PYTHON_LANG: Language = Language(py_grammar())
SCRIPT_DEBUG: bool = True


def generate_tsuite(
        proj_root: str,
        module_path: str,
        config: Dict[str, str],
        chat_history: ChatHistory,
        templs_paths: Tuple[str, str],
        context_names: Tuple[str, str]
) -> None:
    module_name: str = context_names[1]

    # ========== Lettura del Template di Prompt ==========
    templ_func_path: str = templs_paths[0]
    templ_meth_path: str = templs_paths[1]

    templ_func: str = read_templ_frompath(templ_func_path)
    templ_meth: str = read_templ_frompath(templ_meth_path)

    # ========== Estrazione del codice del modulo  ==========
    focalmod_file: str = path_join(
        module_path,
        (module_name + ".py")
    )
    module_cst: Tree = extract_fmodule_code(focalmod_file)

    raw_module_code: str = module_cst.root_node.text.decode()
    module_parts: Tuple[Dict[str, List[str]], Dict[str, List[str]]] = separate_fmodule_code(module_cst)
    module_entities: Dict[str, List[str]] = module_parts[0]
    module_classes: Dict[str, List[str]] = module_parts[1]

    pycode_parser: Parser = Parser(PYTHON_LANG)

    # ========== Lettura/Creazione della Cache di Generazione  ==========
    last_history_gen: Dict[str, str] = dict()
    if os_fdexists("last_history_gen.json"):
        with open("last_history_gen.json", "r") as fp:
            last_history_gen = json_load(fp)
    else:
        with open("last_history_gen.json", "w") as fp:
            pass

    # ========== Calcolo della directory che conterrà la test-suite ==========
    common_path: str = path_intersect([module_path, proj_root])
    rel_path: str = module_path.replace(common_path, "").strip(path_sep)
    tsuite_path: str = path_join(
        path_join(config["gentests_dir"], rel_path), module_name
    )

    # ========== Creazione/sovrascrittura della directory test-suite ==========
    if os_fdexists(tsuite_path):
        os_dremove(tsuite_path)
    os_mkdir(tsuite_path)

    if SCRIPT_DEBUG:
        print("Calculated Test-Suite path for '" + context_names[1] + "' (\"" + context_names[0] + "\"): " + tsuite_path)

    # ========== Generazione Completa (con correzione e scrittura) delle test-suite parziali delle funzioni ==========
    generate_tsuite_modfuncs(
        config,
        chat_history,
        templ_func,
        pycode_parser,
        raw_module_code,
        module_entities["funcs"],
        (module_path, tsuite_path),
        context_names,
        last_history_gen,
        SCRIPT_DEBUG
    )

    # ========== Generazione Completa (con correzione e scrittura) delle test-suite parziali delle classi ==========
    generate_tsuite_testclss(
        config,
        chat_history,
        templ_meth,
        pycode_parser,
        raw_module_code,
        module_entities["classes"],
        module_classes,
        (module_path, tsuite_path),
        context_names,
        last_history_gen,
        SCRIPT_DEBUG
    )


if __name__ == "__main__":
    projects: List[str]
    names: List[str]

    buffer: str
    with open("dirs.json", "r") as fp:
        buffer = reduce(lambda acc, x: acc + x, fp.readlines())
    dirs_file: Dict[str, str] = json_loads(buffer)

    with open("projs.json", "r") as fp:
        buffer = reduce(lambda acc, x: acc + x, fp.readlines())
    projs_file: Dict[str, List[str]] = json_loads(buffer)

    prompts_root = dirs_file["prompts_path"]
    projects = projs_file["roots"]
    names = projs_file["names"]
    test_paths = projs_file["tests"]

    config: Dict[str, str] = configure_ollama(
        "158.110.146.224:1337",
        "ollama:3UHn2uyu1sxgAy15",
        "qwen3:32b"
    )

    curr_file: str
    module_name: str

    file_check: Match[str]
    chat_history: ChatHistory = ChatHistory()
    for i, proj_root in enumerate(projects, start=0):
        config = configure_dirs(
            prompts_root,
            path_join(test_paths[i], "gen_tests"),
            old_config = config
        )

        if SCRIPT_DEBUG:
            print("Current project '" + names[i] + "' | Project_Root = " + proj_root)
        for curr_path, dirs, files in os_walk(proj_root):
            for file in files:
                file_check = reg_search(r"[\S]+\.py$", file)

                if (file != "__init__.py") and (file_check is not None):
                    if SCRIPT_DEBUG:
                        print("Current module-file: \"" + file + "\"")

                    curr_file = path_join(curr_path, file)
                    module_name = path_split_ext(file)[0]

                    generate_tsuite(
                        proj_root,
                        curr_path,
                        config,
                        chat_history,
                        (
                            path_join(config["prompts_dir"], "template_fbyf_func.txt"),
                            path_join(config["prompts_dir"], "template_fbyf_meth.txt")
                         ),
                        (names[i], module_name)
                    )

                    chat_history.clear()

                    ## COVERAGE PART
                    """
                        temp_tsuite_path: str = path_join(tsuite_path, temp_tsuite_fname)
                        with open(temp_tsuite_path, "w") as fp:
                            fp.write(tsuite_code)
    
                        i: int = 0
                        module_dottedpath: str = curr_path.replace(path_sep, ".").strip(".") + "." + module_name
                        coverage_cmd: str = "coverage run --source=" + module_dottedpath + " " + temp_tsuite_path
                        # coverage run --source=optuna.cli .../gen_tests/temp_cli_testsuite.py
                        corrected_code: str = ""
    
                        correct_tsuite_path: str = path_join(tsuite_path, tsuite_fname)
                        if exec_success:
                            if never_corrected:
                                os_rename(temp_tsuite_path, correct_tsuite_path)
                            else:
                                os_remove(temp_tsuite_path)
                                with open(correct_tsuite_path, "w") as fp:
                                    fp.write(corrected_code)
                        else:
                            raise RuntimeError("The Test Suite hasn't been corrected, after " + str(max_retries) + " tries !!")
                    """