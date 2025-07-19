import re
from typing import Dict, List, Set, Tuple, Iterator

import regex

"""from re import (
    Match,
    search as reg_search,
    split as reg_split,
    RegexFlag as RegexFlags
)"""
from regex import (
    Match,
    MULTILINE as reg_MULTILINE,
    search as reg_search,
    split as reg_split,
    RegexFlag as RegexFlags
)

from tree_sitter import Parser, Tree, Node as TreeNode

from _test_ollama.code_extraction import (
    extract_fbyf_code,
)
from _test_ollama.chat_history import ChatHistory
from _test_ollama.prompt_building import (
    build_full_fbyf_funcprompt,
    build_full_fbyf_methprompt
)

from ollama import Client as OllamaClient, ChatResponse

CONTEXT_PROMPT: str = "You are a professional Python developer."
GENCODE_PATT: str = r"(?:<think>[\S\n\t ]*</think>)?\s*```python\n?(?P<gen_code>[\s\S]+)\n?```"
CLSDEF_PATT: str = r"class\s+(?P<cls_name>[a-zA-Z0-9\-\_]+)(\((?P<sup_cls>\S+)\):|:)"

FUNCSIGN_PATT: str = r"(def\s+(?P<func_name>[A-z0-9_\-]+)\s*\((?P<params>[A-z0-9,|:=\"\{\}\t\n ]*)\)\s*(?:->\s*[A-z0-9,|=\"\{\}\t\n \[\]]+)?:)"
FUNCSIGN_OLD_PATT: str = r"(def\s+((?:[a-zA-Z0-9_\-]+))\s*\(((?:.|\n)*?)\)\s*(?:->\s*[a-zA-Z0-9\[\]]+)?:)"

FUNCNAME_PATT: str = r"(def\s+)([a-zA-Z0-9_\-]+)"


def generate_tsuite_modfuncs(
        config: Dict[str, str],
        chat_history: ChatHistory,
        template: str,
        code_parser: Parser,
        module_code: str,
        module_funcs: List[str],
        paths: Tuple[str, str],
        context_names: Tuple[str, str],
        debug: bool = False
) -> Tuple[Dict[str, Set[str]], str]:
    """

        Parameters
        ----------
        config
        chat_history
        template
        code_parser
        module_code
        module_funcs
        context_names

        Returns
        -------
        Tuple[Dict[str, Set[str]], str]

        - [0]: Un dizionario di insiemi di stringhe, indicizzato con stringhe, contenente:

            - "imports": Gli import statement "completi"
            - "fimports": Gli import statement "parziali"

        - [1]: Una stringa contenente il codice di testing relativo alle funzioni proprie del modulo dato

    """
    chat_history.clear()

    gen_imports: Dict[str, Set[str]] = dict()
    gen_imports["imports"] = set()
    gen_imports["fimports"] = set()

    gen_funcs: str = ""

    currcode_tree: Tree
    currcode_tree_root: TreeNode
    gen_code: str

    for func_def in module_funcs:
        func_sign: Match[str] = reg_search(FUNCSIGN_PATT, func_def, reg_MULTILINE)
        func_name: str = func_sign.group("func_name")

        # ========== Costruzione del Prompt Completo ==========
        full_funcprompt: str = build_full_fbyf_funcprompt(
            template,
            module_code,
            func_name,
            paths,
            context_names
        )

        chat_history.add_message("context", CONTEXT_PROMPT)
        chat_history.add_message("user", full_funcprompt)

        if debug:
            print("Generating tests for Function '" + func_name + "' ...")
            print("Lunghezza del (Func.) Prompt = " + str(len(reg_split(r"([ \n])+", full_funcprompt)) * 3/2) + " tokens")
        oll: OllamaClient = OllamaClient(
            host = config["api_url"],
            headers = {'Authorization': config["api_auth"]}
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

        if debug:
            print("\tReceiving response... ", end="")
        full_response: str = ""
        for msg in response:
            full_response += msg['message']['content']
        if debug:
            print("RECEIVED!")

        chat_history.clear()

        gen_code = reg_search(GENCODE_PATT, full_response, RegexFlags.MULTILINE).group("gen_code")

        currcode_tree = code_parser.parse(gen_code.encode())
        currcode_tree_root = currcode_tree.root_node

        result: Tuple[Tuple[List[TreeNode], List[TreeNode]], List[TreeNode]] = extract_fbyf_code(currcode_tree_root)

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

    part_tsuite: Tuple[Dict[str, Set[str]], str] = (gen_imports, gen_funcs)
    return part_tsuite


def generate_tsuite_testclss(
        config: Dict[str, str],
        chat_history: ChatHistory,
        template: str,
        code_parser: Parser,
        module_code: str,
        module_classes: List[str],
        classes_meths: Dict[str, List[str]],
        paths: Tuple[str, str],
        context_names: Tuple[str, str],
        debug: bool = False
) -> Tuple[Dict[str, Set[str]], str]:
    """

        Parameters
        ----------
        config
        chat_history
        template
        code_parser
        module_code
        module_classes
        classes_meths
        context_names

        Returns
        -------
        Tuple[Dict[str, Set[str]], str]

        - [0]: Un dizionario di insiemi di stringhe, indicizzato con stringhe, contenente:

            - "imports": Gli import statement "completi"
            - "fimports": Gli import statement "parziali"

        - [1]: Una stringa contenente il codice di testing relativo alle classi contenute nel modulo dato
    """

    chat_history.clear()

    gen_classes: str = ""

    gen_imports: Dict[str, Set[str]] = dict()
    gen_imports["imports"] = set()
    gen_imports["fimports"] = set()

    fcls_name: str
    gen_class: str

    gen_code: str
    currcode_tree: Tree
    currcode_tree_root: TreeNode
    for fclass in module_classes:
        fcls_name = reg_search(CLSDEF_PATT, fclass).group("cls_name")
        gen_class = "class " + fcls_name + "Tests(TestCase):" + "\n"

        if debug:
            print("Generating tests for Class '" + fcls_name + "' ...")
        for meth_def in classes_meths[fcls_name]:
            meth_sign: Match[str] = reg_search(FUNCSIGN_PATT, meth_def)
            meth_name: str = meth_sign.group("func_name")

            full_methprompt: str = build_full_fbyf_methprompt(
                template,
                module_code,
                fcls_name,
                meth_name,
                paths,
                context_names
            )

            chat_history.add_message("context", CONTEXT_PROMPT)
            chat_history.add_message("user", full_methprompt)

            if debug:
                print("\tGenerating tests for Method '" + meth_name + "' ...")
                print("\tLunghezza del (Method) Prompt = " + str(len(reg_split(r"([ \n])+", full_methprompt)) * 3 / 2) + " tokens")

            oll: OllamaClient = OllamaClient(
                host=config["api_url"],
                headers={'Authorization': config["api_auth"]}
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

            currcode_tree = code_parser.parse(gen_code.encode())
            currcode_tree_root = currcode_tree.root_node

            result: Tuple[Tuple[List[TreeNode], List[TreeNode]], List[TreeNode]] = extract_fbyf_code(currcode_tree_root)

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
                gen_class += new_res_func + "\n"

        gen_classes += ("\n\n" + gen_class)

    part_tsuite: Tuple[Dict[str, Set[str]], str] = (gen_imports, gen_classes)
    return part_tsuite