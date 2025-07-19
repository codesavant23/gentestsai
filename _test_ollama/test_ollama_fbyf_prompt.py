from typing import Dict, List, Set, Tuple
from functools import reduce

from os import (
    walk as os_walk,
    replace as os_rename,
    remove as os_remove
)
from os.path import (
    sep as path_sep,
    commonpath as path_intersect,
    join as path_join,
    splitext as path_split_ext
)

from json import loads as json_loads

from re import (
    Match,
    sub as reg_replace,
    search as reg_search,
    findall as reg_findall,
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

from subprocess import run as subproc_run, CalledProcessError, CompletedProcess

from script_core.tsuite_fbyf_generation import (
    generate_tsuite_modfuncs,
    generate_tsuite_testclss
)

from script_core.tsuite_correction import (
    correct_tsuite,
    correct_tsuite_imports
)

PYTHON_LANG: Language = Language(py_grammar())
SCRIPT_DEBUG: bool = True


def generate_tsuite(
        focalmod_path: str,
        config: Dict[str, str],
        chat_history: ChatHistory,
        templs_paths: Tuple[str, str],
        paths: Tuple[str, str],
        context_names: Tuple[str, str]
) -> str:
    # ========== Lettura del Template di Prompt ==========
    templ_func_path: str = templs_paths[0]
    templ_meth_path: str = templs_paths[1]

    templ_func: str = read_templ_frompath(templ_func_path)
    templ_meth: str = read_templ_frompath(templ_meth_path)

    # ========== Estrazione del codice del modulo  ==========
    module_cst: Tree = extract_fmodule_code(focalmod_path)

    raw_module_code: str = module_cst.root_node.text.decode()
    module_parts: Tuple[Dict[str, List[str]], Dict[str, List[str]]] = separate_fmodule_code(module_cst)
    module_entities: Dict[str, List[str]] = module_parts[0]
    module_classes: Dict[str, List[str]] = module_parts[1]

    pycode_parser: Parser = Parser(PYTHON_LANG)

    tsuite_funcs: Tuple[Dict[str, Set[str]], str]  = generate_tsuite_modfuncs(
        config,
        chat_history,
        templ_func,
        pycode_parser,
        raw_module_code,
        module_entities["funcs"],
        paths,
        context_names,
        SCRIPT_DEBUG
    )
    tsuite_funcs_imps: Dict[str, Set[str]] = tsuite_funcs[0]
    tsuite_funcs_code: str = tsuite_funcs[1]

    tsuite_classes: Tuple[Dict[str, Set[str]], str] = generate_tsuite_testclss(
        config,
        chat_history,
        templ_meth,
        pycode_parser,
        raw_module_code,
        module_entities["classes"],
        module_classes,
        paths,
        context_names,
        SCRIPT_DEBUG
    )
    tsuite_classes_imps: Dict[str, Set[str]] = tsuite_classes[0]
    tsuite_classes_code: str = tsuite_classes[1]

    tsuite_imports: Set[str] = set()
    tsuite_imports_str: str = ""

    i: int
    j: int
    not_finished: bool
    for imp_type in ["imports", "fimports"]:
        i = 0
        j = 0
        not_finished = True
        while not_finished:
            if (i >= len(tsuite_funcs_imps[imp_type])) and (j >= len(tsuite_classes_imps[imp_type])):
                not_finished = False
            elif i < len(tsuite_funcs_imps[imp_type]):
                tsuite_imports.add(tsuite_funcs_imps[imp_type].pop())
                i += 1
            elif j < len(tsuite_classes_imps[imp_type]):
                tsuite_imports.add(tsuite_classes_imps[imp_type].pop())
                j += 1

    for imp_stat in tsuite_imports:
        tsuite_imports_str += (imp_stat + "\n")
    tsuite_imports_str = tsuite_imports_str.rstrip("\n")

    generated_tsuite: str = tsuite_imports_str + "\n\n\n" + (tsuite_funcs_code + "\n\n" + tsuite_classes_code)

    return generated_tsuite




if __name__ == "__main__":
    prompts_testdir: str = "C:\\Users\\filip\\Desktop\\Python_Projects\\thesis_project\\_test_ollama\\_prompts"
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

    test_entered: bool = False
    for i, proj_root in enumerate(projects, start=0):
        config = configure_dirs(
            prompts_root,
            path_join(test_paths[i], "gen_tests"),
            old_config = config
        )

        if SCRIPT_DEBUG:
            print("PROJ_ROOT = ", proj_root)
        for curr_path, dirs, files in os_walk(proj_root):
            for file in files:
                file_check = reg_search(r"[\S]+\.py$", file)

                if (file != "__init__.py") and (file_check is not None):
                    if SCRIPT_DEBUG:
                        print("Scorrimento dei file: File corrente \"" + file + "\"")
                    test_entered = True

                    curr_file = path_join(curr_path, file)
                    module_name = path_split_ext(file)[0]

                    chat_history: ChatHistory = ChatHistory()

                    tsuite_fname: str = module_name + "_testsuite.py"
                    temp_prefix: str = "temp_"
                    temp_tsuite_fname: str = temp_prefix + tsuite_fname

                    common_path: str = path_intersect([curr_path, proj_root])
                    rel_path: str = curr_path.replace(common_path, "").strip(path_sep)
                    tsuite_path: str = path_join(config["gentests_dir"], rel_path)

                    tsuite_code: str = generate_tsuite(
                        curr_file,
                        config,
                        chat_history,
                        (
                            path_join(config["prompts_dir"], "template_fbyf_func.txt"),
                            path_join(config["prompts_dir"], "template_fbyf_meth.txt")
                         ),
                        (curr_path, tsuite_path),
                        (names[i], module_name)
                    )

                    temp_tsuite_path: str = path_join(tsuite_path, temp_tsuite_fname)
                    with open(temp_tsuite_path, "w") as fp:
                        fp.write(tsuite_code)

                    max_retries: int = 5
                    exec_success: bool
                    never_corrected: bool = True
                    i: int = 0
                    module_dottedpath: str = curr_path.replace(path_sep, ".").strip(".") + "." + module_name
                    coverage_cmd: str = "coverage run --source=" + module_dottedpath + " " + temp_tsuite_path
                    corrected_code: str = ""
                    # do-while
                    while True:
                        exec_success = False
                        try:
                            result: CompletedProcess[str] = subproc_run(
                                coverage_cmd.split(" "),
                                check = True,
                                capture_output = True,
                                text = True,
                            )
                            exec_success = True
                        except CalledProcessError as err:
                            never_corrected = False

                            results: List[Match[str]] = reg_findall(r"^[\w_\-]+Error", err.output)
                            last_exception = results.pop()

                            focalmod_cst: Tree = extract_fmodule_code(curr_file)
                            if last_exception == "ImportError":
                                corrected_code = correct_tsuite_imports(
                                    focalmod_cst.root_node.text.decode(),
                                    tsuite_code,
                                    config,
                                    chat_history,
                                    path_join(config["prompts_dir"], "template_fbyf_corrimps.txt"),
                                    (curr_path, tsuite_path),
                                    (names[i], module_name)
                                )
                            else:
                                corrected_code = correct_tsuite(
                                    focalmod_cst.root_node.text.decode(),
                                    tsuite_code,
                                    config,
                                    chat_history,
                                    path_join(config["prompts_dir"], "template_fbyf_corr.txt"),
                                    (curr_path, tsuite_path),
                                    (names[i], module_name)
                                )

                        i += 1

                        # do-while termination condition
                        if exec_success or i >= max_retries:
                            break

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

                if test_entered:
                    raise KeyboardInterrupt()