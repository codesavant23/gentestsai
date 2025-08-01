from typing import Dict, Tuple, Iterator

from functools import reduce

from re import (
    search as reg_search,
    split as reg_split,
    RegexFlag as RegexFlags,
)

from os import (
    remove as os_remove,
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
    dump as json_dump
)

from networkx.classes import is_empty

from _test_ollama.chat_history import ChatHistory
from _test_ollama.template_reading import (
    read_templ_frompath
)
from _test_ollama.prompt_building import (
    build_corr_prompt
)

from ollama import Client as OllamaClient, ChatResponse

from py_compile import (
    compile as py_compile,
    PyCompileError
)


CONTEXT_PROMPT: str = "You are a professional Python developer."
GENCODE_PATT: str = r"(?:<think>[\S\n\t ]*</think>)?\s*```python\n?(?P<gen_code>[\s\S]+)\n?```"

def correct_tsuite_1time(
        wrong_tsuite: str,
        error: Tuple[str, str],
        config: Dict[str, str],
        chat_history: ChatHistory,
        templ_path: str,
        paths: Tuple[str, str],
        context_names: Tuple[str, str],
        llm_history_corr: Dict[str, str],
        debug: bool = False
) -> str:

    templ: str = read_templ_frompath(templ_path)
    full_corr_prompt: str = build_corr_prompt(
        templ,
        wrong_tsuite,
        error,
        paths,
        context_names
    )

    chat_history.add_message("context", CONTEXT_PROMPT)
    chat_history.add_message("user", full_corr_prompt)

    corr_code: str
    if not (full_corr_prompt in llm_history_corr.keys()):
        if debug:
            print("Correcting code of the module '" + context_names[1] + "' (\"" + context_names[0] + "\") ...")
            print("Lunghezza del (Correct) Prompt = " + str(len(reg_split(r"([ \n])+", full_corr_prompt)) * 3 / 2) + " tokens")
            print("\tReceiving response... ", end="")

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
        if debug:
            print("RECEIVED!")

        full_response: str = ""
        for msg in response:
            full_response += msg['message']['content']

        corr_code = reg_search(GENCODE_PATT, full_response, RegexFlags.MULTILINE).group("gen_code")

        llm_history_corr[full_corr_prompt] = corr_code
        with open("last_history_corr.json", "w") as fp:
            json_dump(llm_history_corr, fp)
        if debug:
            print("Correction Cache Updated!")
    else:
        corr_code = llm_history_corr[full_corr_prompt]
        if debug:
            print("Correction of error '" + error[0] + "' on '" + context_names[1] + "' (\"" + context_names[0] + "\") test-suite taken by the LLM Correction Cache")

    return corr_code


def correct_tsuite(
        wrong_parttsuite_path: str,
        config: Dict[str, str],
        chat_history: ChatHistory,
        templ_path: str,
        paths: Tuple[str, str],
        context_names: Tuple[str, str],
        debug: bool = False,
):
    tsuite_path: str = paths[1]

    last_history_corr: Dict[str, str] = dict()
    if os_fdexists("last_history_corr.json"):
        content: str = ""
        with open("last_history_corr.json", "r") as fp:
            content = reduce(lambda acc, x: acc + "\n" + x, fp.readlines(), "").rstrip("\n")
        if not (content == ""):
            with open("last_history_corr.json", "r") as fp:
                last_history_corr = json_load(fp)
    else:
        with open("last_history_corr.json", "w") as fp:
            pass

    wrong_parttsuite: str
    with open(wrong_parttsuite_path, "r") as fp:
        wrong_parttsuite = reduce(lambda acc, x: acc + "\n" + x, fp.readlines())

    toexec_path: str = wrong_parttsuite_path
    curr_code: str = wrong_parttsuite
    except_name: str
    except_mess: str
    exec_success: bool = False
    while not exec_success:
        try:
            py_compile(toexec_path, doraise=True)
            exec_success = True
        except PyCompileError as err:
            except_name = reg_search(r"[A-Z][\w_\-]+Error", err.exc_type_name).group()
            except_mess = err.args[0]

            with open(toexec_path, "r") as fp:
                curr_code = reduce(lambda acc, x: acc + "\n" + x, fp.readlines())

            curr_code = correct_tsuite_1time(
                curr_code,
                (except_name, except_mess),
                config,
                chat_history,
                templ_path,
                paths,
                context_names,
                last_history_corr,
                debug=debug
            )

            toexec_path = path_join(tsuite_path, "__corr_temp.py")
            with open(toexec_path, "w") as fp:
                fp.write(curr_code)

    if toexec_path != wrong_parttsuite_path:
        os_remove(toexec_path)

    return curr_code