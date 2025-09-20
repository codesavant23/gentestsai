# TODO: (Secondario) Finire di sistemare tutti gli Spazi con i TAB in ogni file
from typing import Dict, List, Any
from functools import reduce

from re import (
	Match,
	search as reg_search,
)

from os import (
	walk as os_walk,
	makedirs as os_mkdirs,
)
from shutil import (
	rmtree as os_dremove
)
from os.path import (
	sep as path_sep,
	altsep as path_altsep,
	exists as os_fdexists,
	join as path_join,
	split as path_split,
	splitext as path_split_ext
)

from sqlite3 import (
	connect as sql_connect,
	Connection as SqlConnection,
	Cursor as SqlConnectionCursor
)

from chat_history import ChatHistory

from configuration import (
	configure_ollama,
	read_gentests_conf
)
from json import (
	loads as json_loads
)

from tsuite_mbym_comp_generation import (
	generate_module_tsuite
)

SCRIPT_DEBUG: bool = True



if __name__ == "__main__":
# ========== Macro-processo di "Configurazione Parametri" del progetto ==========
	# ========== Lettura dei file di configurazione del progetto ==========
	all_configs: Dict[str, Any] = read_gentests_conf()

	general_config: Dict[str, Any] = all_configs["general_config"]
	projs_config: Dict[str, Dict[str, Any]] = all_configs["projs_config"]
	ollama_config: Dict[str, str] = all_configs["ollama_config"]
	models_config: List[Dict[str, Any]] = all_configs["models_config"]
	prompts_config: Dict[str, str] = all_configs["prompts_config"]

	# ========== DEBUG: Lettura della configurazione di debug ==========
	with open("debug.json", "r") as fp:
		buffer = reduce(lambda acc, x: acc + x, fp.readlines())
	debug_config: Dict[str, Dict[str, str]] = json_loads(buffer)
	debug_log_config: Dict[str, str] = debug_config["curr_resp_log"]
	debug_errlog_config: Dict[str, str] = debug_config["post_resp_log"]
	cache_config: Dict[str, str] = debug_config["caching"]

	project_names: List[str] = list(projs_config.keys())

	# ========== DEBUG: Calcolo delle path delle caches ==========
	gen_cache_path: str = path_join(cache_config["cache_root"], cache_config["gen_cache_db"])
	corr_cache_path: str = path_join(cache_config["cache_root"], cache_config["corr_cache_db"])

	# ========== DEBUG: Apertura, ed eventuale creazione, delle caches ==========
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

# ========== Macro-processo di "Generazione Completa (dei tests) dei Progetti", per ogni modello ==========
	curr_config: Dict[str, Any]
	default_model_config = general_config["def_model_params"]
	general_files_excl: List[str] = general_config["excluded_files"]

	templ_func_prompt_path: str
	templ_meth_prompt_path: str
	templ_corr_prompt_path: str

	model_name: str
	model_ctxwin: int
	model_options: Dict[str, Any]

	model_dirname: str
	prompt_dirname: str

	project_info: Dict[str, Any]
	focal_proj_root: str
	focal_excluded: List[str]
	test_dirname: str
	test_proj_root: str

	curr_file: str
	module_name: str
	file_namecheck: Match[str]
	file_poscheck: bool
	chat_history: ChatHistory = ChatHistory()

	# ========== Scorrimento dei modelli da valutare ==========
	for curr_model in models_config:
		model_name = curr_model["name"]
		model_ctxwin = curr_model.get("context_window", default_model_config["context_window"]) #TODO: Aggiungere controllo sull' esistenza di "context_window" (default)
		model_options = curr_model.get("options", default_model_config["options"]) #TODO: Aggiungere controllo sull' esistenza di "options" (default)

		model_dirname = model_name.replace(":", "_")
		test_dirname = path_join(
			general_config["gen_tests_dir"],
			model_dirname
		)

		# ========== Lettura degli, eventuali, prompt specifici per modello (o fallback sui generici) ==========
		if os_fdexists(path_join(prompts_config["prompts_path"], model_dirname)):
			prompt_dirname = model_dirname
		else:
			prompt_dirname = prompts_config["generic_prompts_dir"]

		templ_func_prompt_path = path_join(
			path_join(prompts_config["prompts_path"], prompt_dirname),
			prompts_config["func_prompt"]
		)
		templ_meth_prompt_path = path_join(
			path_join(prompts_config["prompts_path"], prompt_dirname),
			prompts_config["meth_prompt"]
		)
		templ_corr_prompt_path = path_join(
			path_join(prompts_config["prompts_path"], prompt_dirname),
			prompts_config["corr_prompt"]
		)

		curr_config = configure_ollama(
			ollama_config["api_url"],
			ollama_config["userpass_pair"],
			model_name,
			ollama_config["connect_timeout"],
			ollama_config["response_timeout"]
		)
		model_options["num_ctx"] = model_ctxwin
		curr_config["model_options"] = model_options

		# ========== Scorrimento di ogni progetto di cui generare i tests ==========
		for project_name in project_names:
			project_info = projs_config[project_name]
			focal_proj_root = project_info["focal_root"]
			focal_excluded = project_info.get("focal_excluded", [])

			# ========== Calcolo, e svuotamento, della Gentest Project Root Path del progetto corrente ==========
			focal_proj_root = focal_proj_root.rstrip(path_sep).rstrip(path_altsep)
			test_proj_root = path_join(
				path_split(focal_proj_root)[0],
				test_dirname
			)

			if os_fdexists(test_proj_root):
				os_dremove(test_proj_root)
			os_mkdirs(test_proj_root)

			curr_config["test_proj_root"] = test_proj_root
			curr_config["focal_proj_root"] = focal_proj_root

			# ========== Eventuale creazione della tabella del progetto nella cache di "Generazione" ==========
			gen_conn_cur.execute(f"""
				CREATE TABLE IF NOT EXISTS "{project_name}" (
					`prompt` TEXT,
					`response` TEXT,
					`model` TEXT,
					PRIMARY KEY (`prompt`, `model`)
				)
			""")

			# ========== Eventuale creazione della tabella del progetto nella cache di "Correzione" ==========
			corr_conn_cur.execute(f"""
				CREATE TABLE IF NOT EXISTS "{project_name}" (
					`prompt` TEXT,
					`response` TEXT,
					`model` TEXT,
					PRIMARY KEY (`prompt`, `model`)
				)
			""")

			# ========== Scorrimento di ogni directory/file appartenente al progetto ==========
			if SCRIPT_DEBUG:
				print("Current project '" + project_name + "' | Project_Root = " + focal_proj_root)
			for curr_path, dirs, files in os_walk(focal_proj_root):
				if not curr_path in focal_excluded:
					for file in files:
						file_namecheck = reg_search(r"^\S(\S| )*\.py$", file)

						# Se il file rappresenta un modulo Python parte del codice focale
						if (
							(not (file in general_files_excl)) and
							(not (file in focal_excluded)) and
							(file_namecheck is not None)
						):
							curr_file = path_join(curr_path, file)
							module_name = path_split_ext(file)[0]

							if SCRIPT_DEBUG:
								print("Current module-file: \"" + file + "\" | Module_Path = " + curr_file)

							# ========== Generazione completa dei tests per quello specifico modulo ==========
							generate_module_tsuite(
								curr_path,
								general_config["skipped_tests_file"],
								curr_config,
								chat_history,
								(
									templ_func_prompt_path,
									templ_meth_prompt_path,
									templ_corr_prompt_path
								),
								(project_name, module_name),
								(gen_conn, gen_conn_cur),
								(corr_conn, corr_conn_cur),
								debug=SCRIPT_DEBUG,
								debug_promptresp=True,
								debug_log_config=debug_log_config,
								debug_errlog_config=debug_errlog_config
							)

							chat_history.clear()
	corr_conn.close()
	gen_conn.close()