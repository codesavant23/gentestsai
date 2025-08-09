from typing import Dict, Tuple, List, Iterator

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
    join as path_join,
)

from sqlite3 import (
    Cursor as SqlConnectionCursor
)

from _test_ollama.chat_history import ChatHistory
from _test_ollama.template_reading import (
    read_templ_frompath
)
from _test_ollama.prompt_building import (
    build_full_corrprompt
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
        corr_conn_cur: SqlConnectionCursor,
        debug: bool = False
) -> str:
    project_name: str = context_names[0]

    templ: str = read_templ_frompath(templ_path)
    full_corrprompt: str = build_full_corrprompt(
        templ,
        wrong_tsuite,
        error,
        paths,
        context_names
    )

    chat_history.add_message("context", CONTEXT_PROMPT)
    chat_history.add_message("user", full_corrprompt)

    prompt_exists: bool
    corr_conn_cur.execute(f"""
        SELECT * FROM `{project_name}`
        WHERE `prompt` = ?
        AND `model` = ?
    """, [full_corrprompt, config["model"]])
    rows: List[Tuple[str, str]] = corr_conn_cur.fetchall()
    prompt_exists = len(rows) > 0

    corr_code: str
    if not prompt_exists:
        if debug:
            print("Correcting code of the module '" + context_names[1] + "' (\"" + context_names[0] + "\") ...")
            print("Lunghezza del (Correct) Prompt = " + str(len(reg_split(r"([ \n])+", full_corrprompt)) * 3 / 2) + " tokens")

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
            print("\tReceiving response... ", end="")
        full_response: str = ""
        for msg in response:
            full_response += msg['message']['content']
        if debug:
            print("RECEIVED!")

        corr_code = reg_search(GENCODE_PATT, full_response, RegexFlags.MULTILINE).group("gen_code")

        corr_conn_cur.execute(f"""
            INSERT INTO {project_name} (prompt, response, model)
            VALUES (?, ?, ?);
        """,
        [full_corrprompt, corr_code, config["model"]])
        if debug:
            print("Correction Cache Updated!")
    else:
        corr_code = rows[0][1]
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
        corr_conn_cur: SqlConnectionCursor,
        debug: bool = False,
):
    tsuite_path: str = paths[1]

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
                corr_conn_cur,
                debug=debug
            )

            toexec_path = path_join(tsuite_path, "__corr_temp.py")
            with open(toexec_path, "w") as fp:
                fp.write(curr_code)

    if toexec_path != wrong_parttsuite_path:
        os_remove(toexec_path)

    return curr_code