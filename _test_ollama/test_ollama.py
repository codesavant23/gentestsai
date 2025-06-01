from typing import Dict, List, Tuple
from pprint import pprint
from os.path import split as path_split, join as path_join
from requests import Session as ReqSession, Response
from re import search as reg_search, findall as reg_findall, split as reg_split, RegexFlag as RegexFlags
from functools import reduce

from configuration import configure_script
from template_reading import extract_templs
from code_extraction import extract_focalmodule_code, extract_module_code
from module_testsuite import ModuleTestSuite
from prompt_building import build_full_infoprompt, build_full_taskprompt
from chat_history import ChatHistory


#
#   TODO: Aggiungere controlli sulla lunghezza del prompt e finestra di contesto
#


"""
    http://ollama:3UHn2uyu1sxgAy15@158.110.146.224:1337/api/generate 
    Attualmente i modelli caricati che puoi usare sono: 
    `llama3.1:latest` 
    `llama3.2-vision:90b` 
    `llama3.1:70b-instruct-q6_K`
    `qwq:latest` 
    `qwen3:32b`
"""


if __name__ == "__main__":
    base_dir: str = "C:\\Users\\filip\\Desktop\\Python_Projects\\thesis_project\\_test_ollama\\"

    module_test_suite: ModuleTestSuite = ModuleTestSuite([], [], [], [])

    config: Dict[str, str] = configure_script(base_dir)
    keep_alive: str = "30m"

    context_prompt: str = "You are a professional Python software developer."

    methsign_patt: str = r"(def\s+((?:[a-zA-Z0-9_\-]+))\s*\(((?:.|\n)*?)\)\s*(?:->\s*[a-zA-Z0-9\[\]]+)?:)"
    methname_patt: str = r"(def\s+)([a-zA-Z0-9_\-]+)"

    # ========== Stabilimento dei file contenenti i Templates dei Prompt e Lettura dei Template di Prompt ==========
    infoprompt_funcs_path: str = path_join(config["prompts_dir"], "template_infoprompt_funcs.txt")
    taskprompt_funcs_path: str = path_join(config["prompts_dir"], "template_taskprompt_funcs.txt")
    infoprompt_clss_path: str = path_join(config["prompts_dir"], "template_infoprompt_classes.txt")
    taskprompt_clss_path: str = path_join(config["prompts_dir"], "template_taskprompt_classes.txt")

    prompt_templs: Dict[str, str] = extract_templs(
        (
            (infoprompt_funcs_path, taskprompt_funcs_path),
            (infoprompt_clss_path, taskprompt_clss_path),
        )
    )

    # ========== Estrazione del codice del singolo modulo  ==========
    result: Tuple[str, Dict[str, List[str]]] = extract_focalmodule_code(config["focalmod_path"])
    raw_module_code: str = result[0]
    module_code: Dict[str, List[str]] = result[1]

    #
    # ========== Richiesta di Generazione dei Test Cases associati alle Funzioni del modulo ==========
    #

    # ========== Costruzione dell' Informational Prompt per la prima interazione ==========
    info_fullprompt: str = build_full_infoprompt(
        prompt_templs["funcs_infop"],
        raw_module_code
    )

    chat_history: ChatHistory = ChatHistory()
    with ReqSession() as sesh:
    # ========== Inizio chat con Invio dell' Informational Prompt per Singole Funzioni ==========
        #print(len(reg_split(r"( |\n)+", info_fullprompt)))
        #pprint(info_fullprompt)
        response: Response = sesh.post(
            url = config["api_url"],
            json = {
                "model": config["model"],
                "system": context_prompt,
                "prompt": info_fullprompt,
                "stream": False,
                "temperature": 0.1,
                "keep-alive": keep_alive
            }
        )
        chat_history.add_message("user", info_fullprompt)
        chat_history.add_message("llm", response.json()["message"]["content"])

        # ========== Invio dei Task Prompts per Singole Funzioni ==========
        task_fullprompt: str
        gen_code: str
        extraction: Dict[str, List[str]]
        for func in module_code["funcs"]:
            # Estrazione nome della funzione per la creazione del suo file contenente il suo test
            #func_sign: str = reg_search(methsign_patt, func).group()
            #func_name: str = reg_search(methname_patt, func_sign).group(2)

            task_fullprompt = build_full_taskprompt(
                prompt_templs["funcs_taskp"], func
            )
            print(len(task_fullprompt.split(" ")))

            # ========== Invio dei Task Prompts per Singole Funzioni ==========
            response: Response = sesh.post(
                url = config["api_url"],
                json = {
                    "model": config["model"],
                    "system": context_prompt,
                    "messages": chat_history.history(),
                    "prompt": task_fullprompt,
                    "stream": False,
                    "temperature": 0.1,
                    "keep-alive": keep_alive
                }
            )
            gen_code = response.json()["message"]["content"]

            #pprint(task_fullprompt)
            #print()
            #pprint(response.json())
            #raise KeyboardInterrupt()

            extraction = extract_module_code(gen_code)

            module_test_suite.add_import(
                reduce(lambda acc, x: acc + "\n" + x, extraction["imports"], "").strip(" \n\t")
            )
            module_test_suite.add_fromimport(
                reduce(lambda acc, x: acc + "\n" + x, extraction["froms"], "").strip(" \n\t")
            )
            module_test_suite.add_func(
                reduce(lambda acc, x: acc + "\n" + x, extraction["funcs"], "").strip(" \n\t")
            )
            module_test_suite.add_class(
                reduce(lambda acc, x: acc + "\n" + x, extraction["classes"], "").strip(" \n\t")
            )
    chat_history.clear()

    #
    # ========== Richiesta di Generazione delle Test Suites associate alle Classi ==========
    #

    cls_idx: int = 0
    mod_classes: List[str] = module_code["classes"]
    meth_patt: str = r"(def\W(\w+)([\w\W]*?))(?=(def)|$)"
    gen_cls_testsuite: str
    with ReqSession() as sesh:
        for cls in mod_classes:
            # Come test vengono utilizzati tutti gli import, e import parziali, del modulo focale
            module_imports: str = reduce(lambda acc, x: acc + "\n" + x, module_code["imports"], "").strip(" \n\t")
            module_fromimports: str = reduce(lambda acc, x: acc + "\n" + x, module_code["froms"], "").strip(" \n\t")

            cls_module: str = module_imports + "\n" + module_fromimports + "\n" + cls

            # ========== Costruzione dell' Informational Prompt per la prima interazione ==========
            info_fullprompt = build_full_infoprompt(
                prompt_templs["clss_infop"],
                cls_module
            )

            # ========== Invio dell' Informational Prompt per Metodi delle Classi ==========
            response: Response = sesh.post(
                url = config["api_url"],
                json = {
                    "model": config["model"],
                    "system": context_prompt,
                    "prompt": info_fullprompt,
                    "stream": False,
                    "temperature": 0.1,
                    "keep-alive": keep_alive
                }
            )
            chat_history.add_message("user", info_fullprompt)
            chat_history.add_message("llm", response.json()["message"]["content"])

            meths_code: List[str] = list(map(lambda x: x[0], reg_findall(meth_patt, cls, RegexFlags.NOFLAG)))

            # Rimozione possibile codice non parte dell' ultimo metodo
            last_meth_lines: List[str] = meths_code[len(meths_code) - 1].split("\n")
            last_return_patt: str = r"return [\W\w]+"
            line: str
            last_return_found: bool = False
            i: int = len(last_meth_lines) - 1
            while (i >= 0) and (not last_return_found):
                line = last_meth_lines[i]
                if reg_search(last_return_patt, line) is not None:
                    last_return_found = True
                    i += 2
                i -= 1
            if last_return_found:
                meths_code[len(meths_code) - 1] = reduce(lambda acc,x: acc + "\n" + x, last_meth_lines[0:i], "")

            # Estrazione nome della classe per la creazione della sua test suite
            cls_name: str = reg_search(r"(class\s+)([a-zA-Z0-9_\-]+)", cls.split("\n")[0]).group(2)

            # ========== Invio dei Task Prompts per Metodi delle Classi ==========
            gen_cls_testsuite = "class " + cls_name + "TestSuite:"
            extraction: Dict[str, List[str]]
            for meth in meths_code:
                task_fullprompt = build_full_taskprompt(
                    prompt_templs["clss_taskp"],
                    meth
                )

                response: Response = sesh.post(
                    url = config["api_url"],
                    json = {
                        "model": config["model"],
                        "system": context_prompt,
                        "messages": chat_history.history(),
                        "prompt": task_fullprompt,
                        "stream": False,
                        "temperature": 0.1,
                        "keep-alive": keep_alive
                    }
                )
                gen_code = response.json()["message"]["content"]

                extraction = extract_module_code(gen_code)

                module_test_suite.add_import(
                    reduce(lambda acc, x: acc + "\n" + x, extraction["imports"], "").strip(" \n\t")
                )
                module_test_suite.add_fromimport(
                    reduce(lambda acc, x: acc + "\n" + x, extraction["froms"], "").strip(" \n\t")
                )

                cls_body: str = reduce(lambda acc, x: acc + "\n" + x, extraction["funcs"], "").strip(" \n\t")

                gen_cls_testsuite += ("\n\n" + cls_body)

            gen_cls_testsuite = gen_cls_testsuite.strip(" \n\t")

            module_test_suite.add_class(gen_cls_testsuite)
            chat_history.clear()

    orig_path: Tuple[str, str] = path_split(config["focalmod_path"])
    module_name: str = orig_path[1].split(".")[0]
    with open(orig_path[0] + module_name + "_testsuite.py", "r") as fsuite:
        fsuite.write(module_test_suite.test_suite())