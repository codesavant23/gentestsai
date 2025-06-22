from typing import Dict, List, Tuple
from os.path import split as path_split, join as path_join

from requests import Session as RequestSession
from re import (
    search as reg_search,
    findall as reg_findall,
    split as reg_split,
    RegexFlag as RegexFlags
)

from tree_sitter import Language, Parser, Tree, Node as TreeNode
from tree_sitter_python import language as py_grammar

from configuration import configure_script
from template_reading import read_templ_frompath
from code_extraction import (
    extract_fmodule_code,
    separate_fmodule_code,
    extract_fbyf_funcprompt_code,
    parse_codeonly_response
)
from chat_history import ChatHistory
from prompt_building import (
    build_full_fbyf_singleprompt,
    build_corrimps_prompt
)
from llm_interaction import ollama_interact
from sexp_utils import tree_to_sexp

from tempfile import TemporaryDirectory, TemporaryFile
from pprint import pprint


def _generate_tsuite_modfuncs(
        config: Dict[str, str],
        chat_history: ChatHistory,
        template: str,
        code_parser: Parser,
        module_code: str,
        module_funcs: List[str],
        context_names: Tuple[str, str]
) -> str:
    context_prompt: str = "You are a professional Python developer."

    funcsign_patt: str = r"(def\s+((?:[a-zA-Z0-9_\-]+))\s*\(((?:.|\n)*?)\)\s*(?:->\s*[a-zA-Z0-9\[\]]+)?:)"
    funcname_patt: str = r"(def\s+)([a-zA-Z0-9_\-]+)"

    resp_tree: Tree
    for func_def in module_funcs:
        func_sign: str = reg_search(funcsign_patt, func_def).group()
        func_name: str = reg_search(funcname_patt, func_sign).group(2)

        with RequestSession() as sesh:
            # ========== Costruzione del Prompt Completo ==========
            full_funcprompt: str = build_full_fbyf_singleprompt(
                template,
                module_code,
                func_name,
                context_names
            )

            #  _test_dir\distributions.py
            print("Function: ", func_name)
            chat_history.add_message("context", context_prompt)
            chat_history.add_message("user", full_funcprompt)
            print("Lunghezza del Prompt per la gen. di una Singola Funzione = " + str(len(reg_split(r"([ \n])+", full_funcprompt))) + " tokens")
            response: str = ollama_interact(
                config["api_url"],
                config["model"],
                sesh,
                chat_history,
                model_spec = {
                    "temperature": 0,
                    "top_k": 10,
                    "top_p": 0.90,
                    "num_ctx": 70000
                }
            )
            chat_history.clear()

            unwrapd_resp: str = parse_codeonly_response(response)
            print("Response: ")
            print(unwrapd_resp)

            resp_tree = code_parser.parse(unwrapd_resp.encode())
            resp_tree_root: TreeNode = resp_tree.root_node

            tree_sexp: str = tree_to_sexp(resp_tree.root_node)
            print("S-Expression: ", tree_sexp)

            result: Tuple[Tuple[List[TreeNode], List[TreeNode]], List[TreeNode]] = extract_fbyf_funcprompt_code(resp_tree_root)

            resp_imports: List[TreeNode] = result[0][0]
            resp_fromimps: List[TreeNode] = result[0][1]
            resp_funcs: List[TreeNode] = result[1]

            imports_str: str = ""
            fromimps_str: str = ""
            funcs_str: str = ""
            for import_ in resp_imports:
                imports_str += ("\n" + str(import_.text))
            imports_str.lstrip("\n")
            for fimport_ in resp_fromimps:
                fromimps_str += ("\n" + str(fimport_.text))
            fromimps_str.lstrip("\n")
            for func in resp_funcs:
                funcs_str += ("\n" + str(func.text))
            fromimps_str.lstrip("\n")

            print("\n----------------------------------------------------------")
            print("IMPORTS:")
            pprint(imports_str)
            print("FROM-IMPORTS:")
            pprint(fromimps_str)
            print("TESTS:")
            pprint(funcs_str)

            raise KeyboardInterrupt()

    return ""


def _generate_tsuite_testclss(
        config: Dict[str, str],
        chat_history: ChatHistory,
        template: str,
        code_parser: Parser,
        module_code: str,
        module_classes: List[str],
        classes_meths: Dict[str, List[str]],
        context_names: Tuple[str, str]
) -> str:
    None


def generate_tsuite(
        config: Dict[str, str],
        chat_history: ChatHistory,
        templs_paths: Tuple[str, str],
        context_names: Tuple[str, str]
) -> Tuple[str, str]:

    context_prompt: str = "You are a professional Python developer that generates test suites for modules, and ANSWERS with CODE ONLY."

    # ========== Lettura del Template di Prompt ==========
    templ_func_path: str = templs_paths[0]
    #templ_meth_path: str = templs_paths[1]

    templ_func: str = read_templ_frompath(templ_func_path)
    #templ_meth: str = read_templ_frompath(templ_meth_path)

    # ========== Estrazione del codice del modulo  ==========
    module_cst: Tree = extract_fmodule_code(config["focalmod_path"])

    raw_module_code: str = module_cst.root_node.text.decode()
    module_parts: Tuple[Dict[str, List[str]], Dict[str, List[str]]] = separate_fmodule_code(module_cst)
    module_entities: Dict[str, List[str]] = module_parts[0]
    module_classes: Dict[str, List[str]] = module_parts[1]

    python_lang: Language = Language(py_grammar())
    pycode_parser: Parser = Parser(python_lang)

    tsuite_funcs_code: str = _generate_tsuite_modfuncs(
        config,
        chat_history,
        templ_func,
        pycode_parser,
        raw_module_code,
        module_entities["funcs"],
        context_names
    )

    """tsuite_classes_code: str = _generate_tsuite_testclss(
        config,
        chat_history,
        templ_meth,
        pycode_parser,
        raw_module_code,
        module_entities["classes"],
        module_classes,
        context_names
    )"""

    # TODO: Finish code

    return ("","")




if __name__ == "__main__":
    base_dir: str = "C:\\Users\\filip\\Desktop\\Python_Projects\\thesis_project\\_test_ollama\\"

    config: Dict[str, str] = configure_script(base_dir)

    chat_history: ChatHistory = ChatHistory()
    result: Tuple[str, str] = generate_tsuite(
        config,
        chat_history,
        (path_join(config["prompts_dir"], "template_fbyf_func.txt"), ""),
        ("optuna", "distributions")
    )
    focal_code: str = result[0]
    tsuite_code: str = result[1]
    """tsuite_code = correct_tsuite_imports(
        config,
        chat_history,
        (focal_code, tsuite_code)
    )"""

    orig_path: Tuple[str, str] = path_split(config["focalmod_path"])
    module_name: str = orig_path[1].split(".")[0]
    suite_path: str = path_join(config["gentests_dir"], (module_name + "_testsuite.py"))
    with open(suite_path, "w") as fsuite:
        fsuite.write(tsuite_code)

    print("Test suite del modulo salvata in '" + suite_path + "' !")
