import base64
from typing import Dict, List, Set, Tuple, Iterator
from os.path import split as path_split, join as path_join

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
)
from chat_history import ChatHistory
from prompt_building import (
    build_full_fbyf_funcprompt,
    build_full_fbyf_methprompt,
    build_corrimps_prompt
)

from ollama import Client as OllamaClient, ChatResponse

from sexp_utils import tree_to_sexp

from tempfile import TemporaryDirectory, TemporaryFile
from pprint import pprint

PYTHON_LANG: Language = Language(py_grammar())
CONTEXT_PROMPT: str = "You are a professional Python developer."
GENCODE_PATT: str = r"(?:<think>[\S\n\t ]*</think>)?\s*```python\n?(?P<gen_code>[\s\S]+)\n?```"
CLSDEF_PATT: str = r"class\s+(?P<cls_name>[a-zA-Z0-9\-\_]+)(\((?P<sup_cls>\S+)\):|:)"
FUNCSIGN_PATT: str = r"(def\s+((?:[a-zA-Z0-9_\-]+))\s*\(((?:.|\n)*?)\)\s*(?:->\s*[a-zA-Z0-9\[\]]+)?:)"
FUNCNAME_PATT: str = r"(def\s+)([a-zA-Z0-9_\-]+)"


def _generate_tsuite_modfuncs(
        config: Dict[str, str],
        chat_history: ChatHistory,
        template: str,
        code_parser: Parser,
        module_code: str,
        module_funcs: List[str],
        context_names: Tuple[str, str]
) -> str:
    chat_history.clear()

    gen_imports: Dict[str, Set[str]] = dict()
    gen_imports["imports"] = set()
    gen_imports["fimports"] = set()

    gen_funcs: str = ""

    currcode_tree: Tree
    currcode_tree_root: TreeNode
    gen_code: str

    for func_def in module_funcs:
        func_sign: str = reg_search(FUNCSIGN_PATT, func_def).group()
        func_name: str = reg_search(FUNCNAME_PATT, func_sign).group(2)

        # ========== Costruzione del Prompt Completo ==========
        full_funcprompt: str = build_full_fbyf_funcprompt(
            template,
            module_code,
            func_name,
            context_names
        )

        chat_history.add_message("context", CONTEXT_PROMPT)
        chat_history.add_message("user", full_funcprompt)

        print("Generating tests for Function '" + func_name + "' ...")
        print("Lunghezza del (Func.) Prompt = " + str(len(reg_split(r"([ \n])+", full_funcprompt)) * 3/2) + " tokens")

        oll: OllamaClient = OllamaClient(
            host = config["api_url"],
            headers = {'Authorization': f'Basic {base64.b64encode(config["api_auth"].encode()).decode()}'}
        )
        response: Iterator[ChatResponse] | ChatResponse = oll.chat(
            config["model"],
            chat_history.history(),
            options = {
                "temperature": 0,
                "num_ctx": 88192,
            },
            stream = True,
            think = False
        )

        chat_history.clear()

        full_response: str = ""
        for msg in response:
            full_response += msg['message']['content']

        gen_code = reg_search(GENCODE_PATT, full_response, RegexFlags.MULTILINE).group("gen_code")

        currcode_tree = code_parser.parse(gen_code.encode())
        currcode_tree_root = currcode_tree.root_node

        """tree_sexp: str = tree_to_sexp(currcode_tree_root)
        print("S-Expression: ", tree_sexp)"""

        result: Tuple[Tuple[List[TreeNode], List[TreeNode]], List[TreeNode]] = extract_fbyf_funcprompt_code(currcode_tree_root)

        for imp_stat in result[0][0]:
            gen_imports["imports"].add(imp_stat.text.decode())
        for fimp_stat in result[0][1]:
            gen_imports["fimports"].add(fimp_stat.text.decode())
        gen_imports["fimports"].add("from unittest import TestCase")

        new_res_func: str
        res_func_str: str
        for res_func in result[1]:
            res_func_str = res_func.text.decode()
            new_res_func = ("\t" + res_func_str.replace("\n", "\n\t"))
            gen_funcs += new_res_func + "\n"

    part_tsuite: str = ""

    for imp_stat in gen_imports["imports"]:
        part_tsuite += imp_stat + "\n"
    for fimp_stat in gen_imports["fimports"]:
        part_tsuite += fimp_stat + "\n"
    part_tsuite = part_tsuite.rstrip("\n")

    part_tsuite += ("\n\n" + "class ModuleFunctionsTests(TestCase):" + "\n")
    part_tsuite += gen_funcs

    return part_tsuite


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
    for fclass in module_classes:
        fcls_name: str = reg_search(CLSDEF_PATT, fclass).group("cls_name")

        print("Generating tests for Class '" + fcls_name + "' ...")
        for meth_def in classes_meths[fcls_name]:
            meth_sign: str = reg_search(FUNCSIGN_PATT, meth_def).group()
            meth_name: str = reg_search(FUNCNAME_PATT, meth_sign).group(2)

            full_methprompt: str = build_full_fbyf_methprompt(
                template,
                module_code,
                fcls_name,
                meth_name,
                context_names
            )

            chat_history.add_message("context", CONTEXT_PROMPT)
            chat_history.add_message("user", full_methprompt)

            print("\tGenerating tests for Method '" + meth_name + "' ...")
            print("\tLunghezza del (Method) Prompt = " + str(len(reg_split(r"([ \n])+", full_methprompt)) * 3/2) + " tokens")

            oll: OllamaClient = OllamaClient(
                host=config["api_url"],
                headers={'Authorization': f'Basic {base64.b64encode(config["api_auth"].encode()).decode()}'}
            )
            response: Iterator[ChatResponse] | ChatResponse = oll.chat(
                config["model"],
                chat_history.history(),
                options={
                    "temperature": 0,
                    "num_ctx": 88192,
                },
                stream=True,
                think=False
            )

            chat_history.clear()

            full_response: str = ""
            for msg in response:
                full_response += msg['message']['content']

            gen_code = reg_search(GENCODE_PATT, full_response, RegexFlags.MULTILINE).group("gen_code")

            # TODO: Finish Code


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

    pycode_parser: Parser = Parser(PYTHON_LANG)

    tsuite_funcs_code: str = _generate_tsuite_modfuncs(
        config,
        chat_history,
        templ_func,
        pycode_parser,
        raw_module_code,
        module_entities["funcs"],
        context_names
    )

    #  _test_dir\distributions.py
    # Versione Attuale = Ollama 0.95
    print("")
    print("T_SUITE FUNCS CODE:")
    print(tsuite_funcs_code)

    raise KeyboardInterrupt()

    tsuite_classes_code: str = _generate_tsuite_testclss(
        config,
        chat_history,
        templ_meth,
        pycode_parser,
        raw_module_code,
        module_entities["classes"],
        module_classes,
        context_names
    )

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
