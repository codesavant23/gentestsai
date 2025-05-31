from typing import Dict, List, Tuple
from pprint import pprint
from requests import Session as ReqSession, Response
from re import search as reg_search, findall as reg_findall, RegexFlag as RegexFlags
from functools import reduce

from configuration import configure_script
from template_reading import extract_templs
from code_extraction import extract_focalmodule_code
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

    module_test_suite: Dict[str, List[str]] = dict()
    config: Dict[str, str] = configure_script(base_dir)
    keep_alive: str = "30m"

    context_prompt: str = "You are a professional Python software developer."

    methsign_patt: str = r"(def\s+((?:[a-zA-Z0-9_\-]+))\s*\(((?:.|\n)*?)\)\s*(?:->\s*[a-zA-Z0-9\[\]]+)?:)"
    methname_patt: str = r"(def\s+)([a-zA-Z0-9_\-]+)"

    # ========== Stabilimento dei file contenenti i Templates dei Prompt e Lettura dei Template di Prompt ==========
    infoprompt_funcs_path: str = config["prompts_dir"] + "template_infoprompt_funcs.txt"
    taskprompt_funcs_path: str = config["prompts_dir"] + "template_taskprompt_funcs.txt"
    infoprompt_clss_path: str = config["prompts_dir"] + "template_infoprompt_classes.txt"
    taskprompt_clss_path: str = config["prompts_dir"] + "template_taskprompt_classes.txt"

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

    # ========== Costruzione dell' Informational Prompt per la prima interazione ==========
    info_fullprompt: str = build_full_infoprompt(
        prompt_templs["funcs_infop"],
        raw_module_code
    )

    chat_history: ChatHistory = ChatHistory()
    with ReqSession() as sesh:
    # ========== Inizio chat con Invio dell' Informational Prompt per Singole Funzioni ==========
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

        # ========== Invio dei Task Prompts per Singole Funzioni ==========
        mod_funcs: List[str] = module_code["funcs"]

        i: int = 0
        last: int = len(mod_funcs)-1
        task_fullprompt: str
        for func in mod_funcs:
            # Estrazione nome della funzione per la creazione del suo file contenente il suo test
            #func_sign: str = reg_search(methsign_patt, func).group()
            #func_name: str = reg_search(methname_patt, func_sign).group(2)

            task_fullprompt = build_full_taskprompt(
                prompt_templs["funcs_taskp"], func
            )

            # ========== Invio dei Task Prompts per Singole Funzioni ==========
            response: Response = sesh.post(
                url = config["api_url"],
                json = {
                    "model": config["model"],
                    "system": context_prompt,
                    "messages": chat_history,
                    "prompt": task_fullprompt,
                    "stream": False,
                    "temperature": 0.1,
                    "keep-alive": keep_alive
                }
            )
            gen_codes.append(response.json()["response"])

            # TODO: Parsing
            # TODO: Estrazione degli import e degli import parziali e salvataggio in 'module_test_suite'
            # TODO: Estrazione dei test case generati e salvataggio in 'module_test_suite'

    chat_history.clear()

    mod_classes: List[str] = module_code["classes"]
    meth_patt: str = r"(def\W(\w+)([\w\W]*?))(?=(def)|$)"
    with ReqSession() as sesh:
        for cls in mod_classes:
            # TODO: Unire la classe e i suoi import necessari (o forse tutti gli import del modulo)
            cls_module: str = "NONE"

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
                    "prompt": cls,
                    "stream": False,
                    "raw": False,
                    "temperature": 0.1,
                    "keep-alive": "5m"
                }
            )
            chat_history.add_message("user", )

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

            # Estrazione nome della classe per la creazione del file contenente la sua test suite
            cls_name: str = reg_search(r"(class\s+)([a-zA-Z0-9_\-]+)", cls.split("\n")[0]).group(2)

            # ========== Invio dei Task Prompts per Metodi delle Classi ==========
            gen_tests: str = ""
            i = 0
            last: int = len(meths_code) - 1
            keep_alive: Union[str, int] = "5m"
            for meth in meths_code:
                if i == last:
                    keep_alive = 0

                response: Response = sesh.post(
                    url = api_url,
                    json = {
                        "template": taskprompt_templ_clss,
                        "model": chosen_model,
                        "prompt": meth,
                        "stream": False,
                        "raw": False,
                        "temperature": 0.1,
                        "keep-alive": keep_alive
                    }
                )
                gen_code = response.json()["response"]
                gen_tests += ("\n" + gen_code)

            gen_tests = gen_tests.lstrip(" \t\n")

            with open(gentest_dir + "test_" + cls_name + ".py", "w") as fgen:
                fgen.write(gen_tests)
