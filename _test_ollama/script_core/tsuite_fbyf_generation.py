from typing import Dict, List, Set, Tuple, Iterator

from regex import (
    Match,
    search as reg_search,
    split as reg_split,
    RegexFlag as RegexFlags
)

from sqlite3 import (
    Connection as SqlConnection,
    Cursor as SqlConnectionCursor
)

from os import (
    replace as os_rename
)
from os.path import (
    join as path_join,
)

from tree_sitter import Tree, Node as TreeNode

from _test_ollama.chat_history import ChatHistory

from _test_ollama.prompt_building import (
    build_full_fbyf_funcprompt,
    build_full_fbyf_methprompt
)

from _test_ollama.script_core.tsuite_correction import (
    correct_tsuite
)

from ollama import Client as OllamaClient, ChatResponse

CONTEXT_PROMPT: str = "You are a professional Python developer."
GENCODE_PATT: str = r"(?:<think>[\S\n\t ]*</think>)?\s*```python\n?(?P<gen_code>[\s\S]+)\n?```"
CLSDEF_PATT: str = r"class\s+(?P<cls_name>[a-zA-Z0-9\-\_]+)(\((?P<sup_cls>\S+(?:, *\S+)*)\):|:)"

FUNCNAME_PATT: str = r"(?:def\s+([A-z0-9_\-]+)\s*\()"


def generate_tsuite_modfuncs(
        config: Dict[str, str],
        chat_history: ChatHistory,
        template: str,
        module_code: str,
        module_funcs: List[str],
        paths: Tuple[str, str],
        context_names: Tuple[str, str],
        gen_cache: Tuple[SqlConnection, SqlConnectionCursor],
        corr_cache: Tuple[SqlConnection, SqlConnectionCursor],
        debug: bool = False
) -> None:
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
    gen_conn: SqlConnection = gen_cache[0]
    gen_conn_cur: SqlConnectionCursor = gen_cache[1]
    project_name: str = context_names[0]
    tsuite_path: str = paths[1]

    gen_code: str
    corrected_code: str

    chat_history.clear()
    func_name: str
    for func_def in module_funcs:
        func_name = reg_search(FUNCNAME_PATT, func_def, RegexFlags.MULTILINE).group(1)

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

        prompt_exists: bool
        gen_conn_cur.execute(f"""
            SELECT * FROM `{project_name}`
            WHERE `prompt` = ?
            AND `model` = ?
        """, [full_funcprompt, config["model"]])
        rows: List[Tuple[str, str, str]] = gen_conn_cur.fetchall()
        prompt_exists = len(rows) > 0

        if not prompt_exists:
            if debug:
                print("Generating tests for Function '" + func_name + "' ...")
                print("Lunghezza del (Func.) Prompt = " + str(
                    len(reg_split(r"([ \n])+", full_funcprompt)) * 3 / 2) + " tokens")
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

            gen_code = reg_search(GENCODE_PATT, full_response, RegexFlags.MULTILINE).group("gen_code")

            gen_conn_cur.execute(f"""
                INSERT INTO {project_name} (prompt, response, model)
                VALUES (?, ?, ?);
            """,
            [full_funcprompt, gen_code, config["model"]])
            gen_conn.commit()
            if debug:
                print("Generation Cache Updated!")
        else:
            gen_code = rows[0][1]
            if debug:
                print("Response of '" + func_name + "' taken by the LLM Generated Cache")

        parttsuite_name: str = func_name + "_" + config["model"].replace(":", "-") + "_tests.py"
        temp_parttsuite_name: str = "temp_" + parttsuite_name

        with open(path_join(tsuite_path, temp_parttsuite_name), "w", encoding="utf-8") as fp:
            fp.write(gen_code)

        corrected_code = correct_tsuite(
            path_join(tsuite_path, temp_parttsuite_name),
            config,
            chat_history,
            path_join(config["prompts_dir"], "template_fbyf_corr.txt"),
            paths,
            context_names,
            corr_cache,
            debug=debug
        )

        with open(path_join(tsuite_path, temp_parttsuite_name), "w") as fp:
            fp.write(corrected_code)
        os_rename(
            path_join(tsuite_path, temp_parttsuite_name),
            path_join(tsuite_path, parttsuite_name)
        )

        chat_history.clear()


def generate_tsuite_testclss(
        config: Dict[str, str],
        chat_history: ChatHistory,
        template: str,
        module_code: str,
        module_classes: List[str],
        classes_meths: Dict[str, List[str]],
        paths: Tuple[str, str],
        context_names: Tuple[str, str],
        gen_cache: Tuple[SqlConnection, SqlConnectionCursor],
        corr_cache: Tuple[SqlConnection, SqlConnectionCursor],
        debug: bool = False
) -> None:
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
    gen_conn: SqlConnection = gen_cache[0]
    gen_conn_cur: SqlConnectionCursor = gen_cache[1]

    project_name: str = context_names[0]
    tsuite_path: str = paths[1]

    fcls_name: str
    meth_name: str

    gen_code: str
    currcode_tree: Tree
    currcode_tree_root: TreeNode

    chat_history.clear()
    for fclass in module_classes:
        fcls_name = reg_search(CLSDEF_PATT, fclass).group("cls_name")

        if debug:
            print("Generating tests for Class '" + fcls_name + "' ...")
        for meth_def in classes_meths[fcls_name]:
            meth_name = reg_search(FUNCNAME_PATT, meth_def).group(1)

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

            prompt_exists: bool
            gen_conn_cur.execute(f"""
                SELECT * FROM `{project_name}`
                WHERE `prompt` = ?
                AND `model` = ?
            """, [full_methprompt, config["model"]])
            rows: List[Tuple[str, str, str]] = gen_conn_cur.fetchall()
            prompt_exists = len(rows) > 0

            if not prompt_exists:
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

                if debug:
                    print("\t\tReceiving response... ", end="")
                full_response: str = ""
                for msg in response:
                    full_response += msg['message']['content']
                if debug:
                    print("RECEIVED!")

                gen_code = reg_search(GENCODE_PATT, full_response, RegexFlags.MULTILINE).group("gen_code")

                gen_conn_cur.execute(f"""
                    INSERT INTO {project_name} (prompt, response, model)
                    VALUES (?, ?, ?);
                """,
                [full_methprompt, gen_code, config["model"]])
                gen_conn.commit()
                if debug:
                    print("\tGeneration Cache Updated!")
            else:
                gen_code = rows[0][1]
                if debug:
                    print("\tResponse of '" + meth_name + "' taken by the LLM Generated Cache")

            parttsuite_name: str = meth_name + "_" + config["model"].replace(":", "-") + "_tests.py"
            temp_parttsuite_name: str = "temp_" + parttsuite_name

            with open(path_join(tsuite_path, temp_parttsuite_name), "w", encoding="utf-8") as fp:
                fp.write(gen_code)

            corrected_code = correct_tsuite(
                path_join(tsuite_path, temp_parttsuite_name),
                config,
                chat_history,
                path_join(config["prompts_dir"], "template_fbyf_corr.txt"),
                paths,
                context_names,
                corr_cache,
                debug=debug
            )

            with open(path_join(tsuite_path, temp_parttsuite_name), "w") as fp:
                fp.write(corrected_code)
            os_rename(
                path_join(tsuite_path, temp_parttsuite_name),
                path_join(tsuite_path, parttsuite_name)
            )

            chat_history.clear()