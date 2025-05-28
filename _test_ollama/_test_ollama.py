from typing import Dict, Any, List, Union
from os import mkdir
from os.path import exists as dir_exists
from requests import Session as ReqSession, Response
from re import search as reg_search, findall as reg_findall, sub as reg_replace, RegexFlag as RegexFlags
from functools import reduce
from ast import Module, parse as ast_parse
from _modulecode_nodevisitor import ModuleCodeVisitor

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
    prompts_dir: str = base_dir + "_prompts" + "\\"
    gentest_dir: str = base_dir + "tests" + "\\"

    if not dir_exists(gentest_dir):
        mkdir(gentest_dir)

    userpass_pair: str = "ollama:3UHn2uyu1sxgAy15"
    base_api: str = "158.110.146.224:1337"
    action: str = "/api/generate"
    api_url: str = "http://" + userpass_pair + "@" + base_api + action
    context_prompt: str = "You are a professional Python software developer."

    methsign_patt: str = r"(def\s+((?:[a-zA-Z0-9_\-]+))\s*\(((?:.|\n)*?)\)\s*(?:->\s*[a-zA-Z0-9\[\]]+)?:)"
    methname_patt: str = r"(def\s+)([a-zA-Z0-9_\-]+)"

    # ========== Stabilimento dei file contenenti i Templates dei Prompt ==========
    infoprompt_funcs_path: str = prompts_dir + "template_infoprompt_funcs.txt"
    taskprompt_funcs_path: str = prompts_dir + "template_taskprompt_funcs.txt"
    infoprompt_clss_path: str = prompts_dir + "template_infoprompt_classes.txt"
    taskprompt_clss_path: str = prompts_dir + "template_taskprompt_classes.txt"

    # ========== Lettura del nome del file python di cui generare i test ==========
    codefile_path: str = base_dir + input("Inserire il nome del file (con estensione .py) di cui generare i tests :>  "+base_dir)

    # ========== Scelta del modello utilizzato nella generazione dei test ==========
    chosen_model: str = input("Inserire la coppia modello:tag per selezionare il LLM da utilizzare :>  ")
    model_patt: str = r"^[a-zA-z0-9\.\-_]+(?:\:[a-zA-z0-9\.\-_]+)?$"
    if reg_search(model_patt, chosen_model) is None:
        raise ValueError("La coppia modello:tag data è malformata o invalida")

    # ========== Estrazione del codice da testare tramite l' AST del modulo ==========
    code_mod: Module
    code_mod_str: str
    with open(codefile_path, "r") as ftest:
        code_mod_str = reduce(lambda acc, x: acc + x, ftest.readlines(), "")
        code_mod = ast_parse(code_mod_str)

    test_visitor: ModuleCodeVisitor = ModuleCodeVisitor()

    test_visitor.visit(code_mod)
    mod_classes: List[str] = test_visitor.classes_definitions()
    mod_funcs: List[str] = test_visitor.funcs_definitions()

    # ========== Lettura dei Template di Prompt per Singole Funzioni (Informational e Task) ==========
    infoprompt_templ_clss: str
    with open(infoprompt_funcs_path, "r") as finfo:
        infoprompt_templ_clss = reduce(lambda acc, x: acc + x, finfo.readlines(), "")

    taskprompt_templ_clss: str
    with open(taskprompt_funcs_path, "r") as ftask:
        taskprompt_templ_clss = reduce(lambda acc, x: acc + x, ftask.readlines(), "")

    gen_code: str
    with ReqSession() as sesh:
    # ========== Invio dell' Informational Prompt per Singole Funzioni ==========
        response: Response = sesh.post(
            url = api_url,
            json = {
                "template": infoprompt_templ_clss,
                "system": context_prompt,
                "model": chosen_model,
                "prompt": code_mod_str,
                "format": "json",
                "stream": False,
                "raw": False,
                "temperature": 0.1,
                "keep-alive": "5m"
            }
        )

    # ========== Invio dei Task Prompts per Singole Funzioni ==========
        i: int = 0
        last: int = len(mod_funcs)-1
        keep_alive: Union[str, int] = "5m"
        for func in mod_funcs:
            # Estrazione nome della funzione per la creazione del suo file contenente il suo test
            func_sign: str = reg_search(methsign_patt, func).group()
            func_name: str = reg_search(methname_patt, func_sign).group(2)

            if i == last:
                keep_alive = -1

            response: Response = sesh.post(
                url = api_url,
                json = {
                    "template": taskprompt_templ_clss,
                    "model": chosen_model,
                    "prompt": func,
                    "format": "json",
                    "stream": False,
                    "raw": False,
                    "temperature": 0.1,
                    "keep-alive": keep_alive
                }
            )
            gen_code = response.json()["response"]

            with open(gentest_dir + "test_" + func_name + ".py", "w") as fgen:
                fgen.write(gen_code)

    # ========== Lettura dei Template di Prompt per Metodi delle Classi (Informational e Task) ==========
    infoprompt_templ_clss: str
    with open(infoprompt_clss_path, "r") as finfo:
        infoprompt_templ_clss = reduce(lambda acc, x: acc + x, finfo.readlines(), "")

    taskprompt_templ_clss: str
    with open(taskprompt_clss_path, "r") as ftask:
        taskprompt_templ_clss = reduce(lambda acc, x: acc + x, ftask.readlines(), "")

    meth_patt: str = r"(def\W(\w+)([\w\W]*?))(?=(def)|$)"
    for cls in mod_classes:
        with ReqSession() as sesh:
        # ========== Invio dell' Informational Prompt per Metodi delle Classi ==========
            response: Response = sesh.post(
                url=api_url,
                json = {
                    "template": infoprompt_templ_clss,
                    "system": context_prompt,
                    "model": chosen_model,
                    "prompt": cls,
                    "format": "json",
                    "stream": False,
                    "raw": False,
                    "temperature": 0.1,
                    "keep-alive": "5m"
                }
            )

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
                        "format": "json",
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
