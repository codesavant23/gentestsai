from typing import Dict, Tuple, Iterator

from re import (
    search as reg_search,
    split as reg_split,
    RegexFlag as RegexFlags
)

from _test_ollama.chat_history import ChatHistory
from _test_ollama.template_reading import (
    read_templ_frompath
)
from _test_ollama.prompt_building import (
    build_corr_prompt,
    build_corrimps_prompt
)

from ollama import Client as OllamaClient, ChatResponse

from _test_ollama.script_core.tsuite_fbyf_generation import (
    CONTEXT_PROMPT,
    GENCODE_PATT
)


def correct_tsuite_imports(
        focal_code: str,
        wrong_tsuite: str,
        config: Dict[str, str],
        chat_history: ChatHistory,
        templ_path: str,
        paths: Tuple[str, str],
        context_names: Tuple[str, str],
        debug: bool = False
) -> str:
    chat_history.clear()

    templ: str = read_templ_frompath(templ_path)
    full_corrimps_prompt: str = build_corrimps_prompt(
        templ,
        focal_code,
        wrong_tsuite,
        paths,
        context_names
    )

    chat_history.add_message("context", CONTEXT_PROMPT)
    chat_history.add_message("user", full_corrimps_prompt)

    if debug:
        print("Correcting imports of the module '" + context_names[1] + "' (\"" + context_names[0] + "\") ...")
        print("Lunghezza del (Correct Imports) Prompt = " + str(len(reg_split(r"([ \n])+", full_corrimps_prompt)) * 3 / 2) + " tokens")

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

    return gen_code


def correct_tsuite(
        focal_code: str,
        wrong_tsuite: str,
        config: Dict[str, str],
        chat_history: ChatHistory,
        templ_path: str,
        paths: Tuple[str, str],
        context_names: Tuple[str, str],
        debug: bool = False
) -> str:
    chat_history.clear()

    templ: str = read_templ_frompath(templ_path)
    full_corrimps_prompt: str = build_corr_prompt(
        templ,
        focal_code,
        wrong_tsuite,
        paths,
        context_names
    )

    chat_history.add_message("context", CONTEXT_PROMPT)
    chat_history.add_message("user", full_corrimps_prompt)

    if debug:
        print("Correcting code of the module '" + context_names[1] + "' (\"" + context_names[0] + "\") ...")
        print("Lunghezza del (Correct) Prompt = " + str(len(reg_split(r"([ \n])+", full_corrimps_prompt)) * 3 / 2) + " tokens")
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

    chat_history.clear()

    full_response: str = ""
    for msg in response:
        full_response += msg['message']['content']

    gen_code = reg_search(GENCODE_PATT, full_response, RegexFlags.MULTILINE).group("gen_code")

    return gen_code