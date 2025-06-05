from typing import Dict, List, Tuple
from os.path import split as path_split, join as path_join
from requests import post as req_post, Response
from functools import reduce
from re import split as reg_split
from pprint import pprint

from configuration import configure_script
from template_reading import read_templ_frompath
from code_extraction import extract_focalmodule_code
from prompt_building import build_full_singleprompt
from chat_history import ChatHistory
from tempfile import TemporaryDirectory, TemporaryFile


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

    config: Dict[str, str] = configure_script(base_dir)
    keep_alive: str = "30m"

    context_prompt: str = """You are a professional Python developer that generates test suites for modules, and ANSWERS with CODE ONLY."""

    # ========== Lettura del Template di Prompt ==========
    testprompt_path: str = path_join(config["prompts_dir"], "template_cot_codeonly_6.txt")
    test_templ: str = read_templ_frompath(testprompt_path)

    # ========== Estrazione del codice del singolo modulo  ==========
    result: Tuple[str, Dict[str, List[str]]] = extract_focalmodule_code(config["focalmod_path"])
    raw_module_code: str = result[0]
    module_code: Dict[str, List[str]] = result[1]

    # ========== Costruzione del Prompt Completo ==========
    full_prompt: str = build_full_singleprompt(
        test_templ,
        raw_module_code,
        ("optuna", "distributions")
    )

    #_test_dir\distributions.py
    chat_history: ChatHistory = ChatHistory()
    print("Lunghezza del Prompt Completo = "+str(len(reg_split(r"( |\n)+", full_prompt)))+" tokens")
    print("Richiesta di generazione dei test ... ", end="")
    chat_history.add_message("context", context_prompt)
    chat_history.add_message("user", full_prompt)
    response: Response = req_post(
        url = config["api_url"],
        json = {
            "model": config["model"],
            "messages": chat_history.history(),
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_k": 10,
                "top_p": 0.90,
                "num_ctx": 128000
            },
            "keep-alive": keep_alive
        }
    )
    print("[COMPLETATA]")

    resp_str: str = response.json()["message"]["content"]
    chat_history.clear()

    print("Response:")
    pprint(resp_str)

    #reduce(lambda acc, line: acc + "\n" + line, resp_lines[1:(len(resp_lines) - 1)], "").lstrip("\n")
    resp_lines: List[str] = resp_str.split("\n")

    py_code: str = reduce(lambda acc, line: acc + "\n" + line, resp_lines[1:(len(resp_lines)-1)], "").lstrip("\n")
    #: str = resp_parts[0]
    #imps_code: str = resp_parts[1]

    #py_code: str = imps_code + "\n\n" + gen_code

    orig_path: Tuple[str, str] = path_split(config["focalmod_path"])
    module_name: str = orig_path[1].split(".")[0]
    suite_path: str = path_join(orig_path[0], (module_name + "_testsuite.py"))
    with open(suite_path, "w") as fsuite:
        fsuite.write(py_code)

    print("Test suite del modulo salvata in '" + suite_path + "' !")
