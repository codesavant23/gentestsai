from typing import Dict, List, Tuple
from functools import reduce

from os import (
    walk as os_walk,
    makedirs as os_mkdirs,
)
from shutil import (
    rmtree as os_dremove
)
from os.path import (
    exists as os_fdexists,
    sep as path_sep,
    commonpath as path_intersect,
    join as path_join,
    splitext as path_split_ext
)

from json import (
    loads as json_loads
)
from sqlite3 import (
    connect as sql_connect,
    Connection as SqlConnection,
    Cursor as SqlConnectionCursor
)

from re import (
    Match,
    search as reg_search,
)

from configuration import (
    configure_ollama,
    configure_dirs
)
from template_reading import read_templ_frompath
from code_extraction import (
    extract_fmodule_code,
    separate_fmodule_code,
)
from tree_sitter import Tree
from chat_history import ChatHistory

from script_core.tsuite_fbyf_generation import (
    generate_tsuite_modfuncs,
    generate_tsuite_testclss
)

SCRIPT_DEBUG: bool = True



def generate_module_tsuite(
        proj_root: str,
        module_path: str,
        config: Dict[str, str],
        chat_history: ChatHistory,
        templs_paths: Tuple[str, str],
        context_names: Tuple[str, str],
        gen_cache: Tuple[SqlConnection, SqlConnectionCursor],
        corr_cache: Tuple[SqlConnection, SqlConnectionCursor]
) -> None:
    module_name: str = context_names[1]

    # ========== Lettura del Template di Prompt ==========
    templ_func_path: str = templs_paths[0]
    templ_meth_path: str = templs_paths[1]

    templ_func: str = read_templ_frompath(templ_func_path)
    templ_meth: str = read_templ_frompath(templ_meth_path)

    # ========== Estrazione del codice del modulo  ==========
    focalmod_file: str = path_join(
        module_path,
        (module_name + ".py")
    )
    module_cst: Tree = extract_fmodule_code(focalmod_file)

    raw_module_code: str = module_cst.root_node.text.decode()
    module_parts: Tuple[Dict[str, List[str]], Dict[str, List[str]]] = separate_fmodule_code(module_cst)
    module_entities: Dict[str, List[str]] = module_parts[0]
    module_classes: Dict[str, List[str]] = module_parts[1]

    # ========== Calcolo della directory che conterrà la test-suite ==========
    common_path: str = path_intersect([module_path, proj_root])
    rel_path: str = module_path.replace(common_path, "").strip(path_sep)
    tsuite_path: str = path_join(
        path_join(config["gentests_dir"], rel_path), module_name
    )

    # ========== Creazione/sovrascrittura della directory test-suite ==========
    if SCRIPT_DEBUG:
        print("Calculated Test-Suite path for '" + context_names[1] + "' (\"" + context_names[0] + "\"): " + tsuite_path)

    if os_fdexists(tsuite_path):
        os_dremove(tsuite_path)
    os_mkdirs(tsuite_path)

    # ========== Generazione Completa (con correzione e scrittura) delle test-suite parziali delle funzioni ==========
    generate_tsuite_modfuncs(
        config,
        chat_history,
        templ_func,
        raw_module_code,
        module_entities["funcs"],
        (module_path, tsuite_path),
        context_names,
        gen_cache,
        corr_cache,
        SCRIPT_DEBUG
    )

    # ========== Generazione Completa (con correzione e scrittura) delle test-suite parziali delle classi ==========
    generate_tsuite_testclss(
        config,
        chat_history,
        templ_meth,
        raw_module_code,
        module_entities["classes"],
        module_classes,
        (module_path, tsuite_path),
        context_names,
        gen_cache,
        corr_cache,
        SCRIPT_DEBUG
    )


if __name__ == "__main__":
    # ========== Lettura dei file di configurazione del progetto ==========
    buffer: str
    with open("dirs.json", "r") as fp:
        buffer = reduce(lambda acc, x: acc + x, fp.readlines())
    dirs_config: Dict[str, str] = json_loads(buffer)

    with open("projs.json", "r") as fp:
        buffer = reduce(lambda acc, x: acc + x, fp.readlines())
    projs_config: Dict[str, List[str]] = json_loads(buffer)

    with open("ollama.json", "r") as fp:
        buffer = reduce(lambda acc, x: acc + x, fp.readlines())
    ollamaauth_config: Dict[str, str] = json_loads(buffer)

    with open("models.json", "r") as fp:
        buffer = reduce(lambda acc, x: acc + x, fp.readlines())
    models_toevaluate: List[str] = json_loads(buffer)

    with open("cache.json", "r") as fp:
        buffer = reduce(lambda acc, x: acc + x, fp.readlines())
    cache_config: Dict[str, str] = json_loads(buffer)

    prompts_root: str = dirs_config["prompts_path"]
    projects: List[str] = projs_config["roots"]
    project_names: List[str] = projs_config["names"]
    test_paths: List[str] = projs_config["tests"]

    # ========== Calcolo delle path delle caches ==========
    gen_cache_path: str = path_join(cache_config["cache_root"], cache_config["gen_cache_db"])
    corr_cache_path: str = path_join(cache_config["cache_root"], cache_config["corr_cache_db"])

    # ========== Apertura, ed eventuale creazione, delle caches ==========
    if not os_fdexists(gen_cache_path):
        with open(gen_cache_path, "w") as fp:
            pass

    gen_conn: SqlConnection = sql_connect(gen_cache_path)
    gen_conn_cur: SqlConnectionCursor = gen_conn.cursor()

    if not os_fdexists(corr_cache_path):
        with open(corr_cache_path, "w") as fp:
            pass

    corr_conn: SqlConnection = sql_connect(corr_cache_path)
    corr_conn_cur: SqlConnectionCursor = corr_conn.cursor()

    # ========== Registrazione del blocco di codice di chiusura dei databases di caching ==========
    """py_guarantee(
        db_caches_close,
        gen_conn=gen_conn,
        corr_conn=corr_conn
    )

    if sys_platform == "win32":
        sig_reghandler(OsSignals.SIGBREAK, db_caches_close_handler)
    else:
        sig_reghandler(OsSignals.SIGKILL, db_caches_close_handler)
        sig_reghandler(OsSignals.SIGBUS, db_caches_close_handler)

    sig_reghandler(OsSignals.SIGILL, db_caches_close_handler)
    sig_reghandler(OsSignals.SIGSEGV, db_caches_close_handler)
    sig_reghandler(OsSignals.SIGABRT, db_caches_close_handler)
    sig_reghandler(OsSignals.SIGTERM, db_caches_close_handler)
    sig_reghandler(OsSignals.SIGINT, db_caches_close_handler)"""
    # =============================================================================================

    curr_file: str
    module_name: str
    file_check: Match[str]
    chat_history: ChatHistory = ChatHistory()

    curr_config: Dict[str, str]
    # ========== Scorrimento dei modelli da valutare ==========
    for model_toevaluate in models_toevaluate:
        curr_config = configure_ollama(
            ollamaauth_config["api_url"],
            ollamaauth_config["userpass_pair"],
            model_toevaluate
        )

        # ========== Scorrimento di ogni progetto di cui generare i tests ==========
        for i, proj_root in enumerate(projects, start=0):
            curr_config = configure_dirs(
                prompts_root,
                path_join(test_paths[i], "gen_tests"),
                old_config = curr_config
            )

            # ========== Eventuale creazione della tabella del progetto nella cache di "Generazione" ==========
            gen_conn_cur.execute(f"""
                CREATE TABLE IF NOT EXISTS "{project_names[i]}" (
                    `prompt` TEXT,
                    `response` TEXT,
                    `model` TEXT,
                    PRIMARY KEY (`prompt`, `model`)
                )
            """)

            # ========== Eventuale creazione della tabella del progetto nella cache di "Correzione" ==========
            corr_conn_cur.execute(f"""
                CREATE TABLE IF NOT EXISTS "{project_names[i]}" (
                    `prompt` TEXT,
                    `response` TEXT,
                    `model` TEXT,
                    PRIMARY KEY (`prompt`, `model`)
                )
            """)

            # ========== Scorrimento di ogni directory/file appartenente al progetto ==========
            if SCRIPT_DEBUG:
                print("Current project '" + project_names[i] + "' | Project_Root = " + proj_root)
            for curr_path, dirs, files in os_walk(proj_root):
                for file in files:
                    file_check = reg_search(r"[\S]+\.py$", file)

                    # Se il file rappresenta un modulo Python parte del codice focale
                    if (file != "__init__.py") and (file_check is not None):
                        curr_file = path_join(curr_path, file)
                        module_name = path_split_ext(file)[0]

                        if SCRIPT_DEBUG:
                            print("Current module-file: \"" + file + "\" | Module_Path = " + curr_file)

                        # ========== Generazione completa dei tests per quello specifico modulo ==========
                        generate_module_tsuite(
                            proj_root,
                            curr_path,
                            curr_config,
                            chat_history,
                            (
                                path_join(curr_config["prompts_dir"], "template_fbyf_func.txt"),
                                path_join(curr_config["prompts_dir"], "template_fbyf_meth.txt")
                             ),
                            (project_names[i], module_name),
                            (gen_conn, gen_conn_cur),
                            (corr_conn, corr_conn_cur)
                        )

                        chat_history.clear()
    gen_conn.close()
    corr_conn.close()