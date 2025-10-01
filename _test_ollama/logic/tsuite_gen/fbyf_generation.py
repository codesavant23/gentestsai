from typing import Dict, List, Tuple, Iterator, Any

from io import (
	TextIOWrapper
)

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

from shutil import (
	rmtree as os_dremove
)
from os import (
	replace as os_rename,
	makedirs as os_mkdirs,
)
from os.path import (
	join as path_join,
	exists as os_fdexists,
	splitext as path_splitext
)

from tree_sitter import Tree, Node as TreeNode

from _test_ollama.logic.tsuite_gen.chat_history import ChatHistory

from _test_ollama.logic.tsuite_gen.prompt_building import (
	build_full_fbyf_funcprompt,
	build_full_fbyf_methprompt
)

from _test_ollama.logic.tsuite_gen.fbyf_correction import (
	correct_tsuite
)

from ollama import (
	Client as OllamaClient,
	ChatResponse
)

from json import (
	loads as json_loads,
	dumps as json_dumps,
)

from datetime import datetime

from pprint import pprint

CONTEXT_PROMPT: str = "You are a professional Python developer."
GENCODE_PATT: str = r"(?:<think>[\S\n\t ]*</think>)?\s*```python\n?(?P<gen_code>[\s\S]+)\n?```"
CLSDEF_PATT: str = r"class\s+(?P<cls_name>[a-zA-Z0-9\-\_]+)(\((?P<sup_cls>\S+(?:, *\S+)*)\):|:)"

FUNCNAME_PATT: str = r"(?:def\s+([A-z0-9_\-]+)\s*\()"



def generate_tsuite_modfuncs(
		config: Dict[str, Any],
		chat_history: ChatHistory,
		template: str,
		template_corr_path: str,
		module_code: str,
		module_funcs: List[str],
		paths: Dict[str, Tuple[str, str]],
		context_names: Tuple[str, str],
		skipped_tests_file: str,
		gen_cache: Tuple[SqlConnection, SqlConnectionCursor],
		corr_cache: Tuple[SqlConnection, SqlConnectionCursor],
		debug: bool = False,
		debug_promptresp: bool = False,
		debug_log_config: Dict[str, str] = None,
		debug_errlog_config: Dict[str, str] = None
) -> None:
	"""
		TODO:
	"""
	gen_conn: SqlConnection = gen_cache[0]
	gen_conn_cur: SqlConnectionCursor = gen_cache[1]
	fplog_resp: TextIOWrapper = None

	project_name: str = context_names[0]

	absolute_paths: Tuple[str, str] = paths["absolute"]
	relative_paths: Tuple[str, str] = paths["relative"]
	tsuite_path: str = absolute_paths[1]

	gen_code_match: Match[str]
	gen_code: str = ""
	corrected_code: str

	mod_funcs_skipd: List[str] = []
	skipd_tests: Dict[str, Any]

	func_name: str

	chat_history.clear()
	for func_def in module_funcs:
		func_name = reg_search(FUNCNAME_PATT, func_def, RegexFlags.MULTILINE).group(1)

		# ========== Costruzione del Prompt Completo ==========
		full_funcprompt: str = build_full_fbyf_funcprompt(
			template,
			module_code,
			func_name,
			relative_paths,
			context_names
		)

		chat_history.add_message("context", CONTEXT_PROMPT)
		chat_history.add_message("user", full_funcprompt)

		if debug_promptresp:
			print("\n\n##### Chat-History Pre-Response: #####")
			pprint(chat_history.history())

		prompt_exists: bool
		gen_conn_cur.execute(f"""
			SELECT * FROM `{project_name}`
			WHERE `prompt` = ?
			AND `model` = ?
		""", [full_funcprompt, config["model"]])
		rows: List[Tuple[str, str, str]] = gen_conn_cur.fetchall()
		prompt_exists = len(rows) > 0

		not_skipped: bool = False
		if not prompt_exists:
			prompt_tokens: int = -1
			resp_tokens: int = -1

			if debug:
				now: datetime = datetime.now()
				datetime_now: str = (str(now.day) + "-" + str(now.month) + "-" + str(now.year) + "_" +
									 str(now.hour) + ":" + str(now.minute) + ":" + str(now.second))
				print("Generating tests for Function '" + func_name + "' ... Started at: " + datetime_now)
				print("Lunghezza del (Func.) Prompt = " + str(
					len(reg_split(r"([ \n])+", full_funcprompt)) * 3 / 2) + " tokens")
			oll: OllamaClient = OllamaClient(
				host=config["api_url"],
				headers={'Authorization': config["api_auth"]},
				timeout=config["timeout"]
			)
			response: Iterator[ChatResponse] | ChatResponse = oll.chat(
				config["model"],
				chat_history.history(),
				options=config["model_options"],
				stream=True,
				think=False,
			)

			if debug_log_config is not None:
				now: datetime = datetime.now()
				datetime_now: str = (str(now.day) + "-" + str(now.month) + "-" + str(now.year) + "_" +
									 str(now.hour) + "-" + str(now.minute) + "-" + str(now.second))

				prompt_parts: Tuple[str, str] = path_splitext(debug_log_config["prompt"])
				resp_parts: Tuple[str, str] = path_splitext(debug_log_config["resp"])

				prompt_path: str = path_join(
					debug_log_config["log_path"],
					prompt_parts[0] + "-" + datetime_now + "_" + func_name + prompt_parts[1]
				)
				resp_path: str = path_join(
					debug_log_config["log_path"],
					resp_parts[0] + "-" + datetime_now + "_" + func_name + resp_parts[1]
				)

				with open(prompt_path, "w") as fplog_prompt:
					fplog_prompt.write(full_funcprompt)
					fplog_prompt.flush()

				fplog_resp = open(resp_path, "w")
			if debug:
				print("\tReceiving response... ", end="")
			full_response: str = ""
			if debug_log_config is None:
				for chunk in response:
					full_response += chunk['message']['content']
					if debug_promptresp:
						print(chunk['message']['content'], end="", flush=True)
					# Se è arrivato alla fine
					if "eval_count" in chunk:
						resp_tokens = chunk["eval_count"]
						prompt_tokens = chunk["prompt_eval_count"]
			else:
				try:
					for chunk in response:
						full_response += chunk['message']['content']
						if debug_promptresp:
							print(chunk['message']['content'], end="", flush=True)
						fplog_resp.write(chunk["message"]["content"])
						fplog_resp.flush()
						# Se è arrivato alla fine
						if "eval_count" in chunk:
							resp_tokens = chunk["eval_count"]
							prompt_tokens = chunk["prompt_eval_count"]
				except:
					fplog_resp.close()
			if debug:
				print("RECEIVED!")
			if debug_log_config is not None:
				fplog_resp.close()

			if (prompt_tokens == -1) or (resp_tokens == -1):
				now: datetime = datetime.now()
				datetime_now: str = (str(now.day) + "-" + str(now.month) + "-" + str(now.year) + "_" +
									 str(now.hour) + ":" + str(now.minute) + ":" + str(now.second))
				raise ValueError(
					f"C'è stato un errore!! ( Prompt_Tokens={prompt_tokens} | Resp_Tokens={resp_tokens} )" +
					f" {datetime_now}"
				)

			# Se il modello non è andato in generazione ciclica -> allora la test-suite parziale è stata generata
			# (e me ne accorgo dalla finestra di contesto perfettamente satura)
			if (prompt_tokens + resp_tokens) < config["model_options"]["num_ctx"]:
				not_skipped = True
				gen_code_match = reg_search(GENCODE_PATT, full_response, RegexFlags.MULTILINE)

				if debug:
					if (gen_code_match is None) and (debug_errlog_config is not None):
						log_path: str = debug_errlog_config["promptresp_log_path"]
						promptfile_name: str = debug_errlog_config["lasterr_prompt"]
						respfile_name: str = debug_errlog_config["lasterr_resp"]

						with open(path_join(log_path, promptfile_name), "w", encoding="utf-8") as fprompt:
							fprompt.write(full_funcprompt)
							fprompt.flush()
						with open(path_join(log_path, respfile_name), "w", encoding="utf-8") as fresp:
							fresp.write(full_response)
							fresp.flush()

				gen_code = gen_code_match.group("gen_code")

				gen_conn_cur.execute(f"""
					INSERT INTO {project_name} (prompt, response, model)
					VALUES (?, ?, ?);
				""",
				[full_funcprompt, gen_code, config["model"]])
				gen_conn.commit()
				if debug:
					print("Generation Cache Updated!")
			else:
				print("Skipped generating tests for '" + func_name + "' as the max context window has been reached")
				mod_funcs_skipd.append(func_name)
		else:
			not_skipped = True
			gen_code = rows[0][1]
			if debug:
				print("Response of '" + func_name + "' taken by the LLM Generated Cache")
			if debug_promptresp:
				print("\n\n\t#### Cached Response: ####")
				print(gen_code)

		if not_skipped:
			chat_history.add_message("llm", ("```python\n" + gen_code.rstrip("\n") + "\n```"))

			parttsuite_name: str = "test_" + func_name + ".py"
			temp_parttsuite_name: str = "temp_" + parttsuite_name

			with open(path_join(tsuite_path, temp_parttsuite_name), "w", encoding="utf-8") as fp:
				fp.write(gen_code)

			corrected_code = correct_tsuite(
				path_join(tsuite_path, temp_parttsuite_name),
				config,
				chat_history,
				template_corr_path,
				absolute_paths,
				relative_paths,
				context_names,
				corr_cache,
				debug=debug,
				debuglog_config=debug_errlog_config
			)

			with open(path_join(tsuite_path, temp_parttsuite_name), "w", encoding="utf-8") as fp:
				fp.write(corrected_code)
			os_rename(
				path_join(tsuite_path, temp_parttsuite_name),
				path_join(tsuite_path, parttsuite_name)
			)

		chat_history.clear()

	if len(mod_funcs_skipd) > 0:
		with open(skipped_tests_file, "w+") as fskipd:
			skipd_tests = json_loads(fskipd.read())
			skipd_tests["functions"] = mod_funcs_skipd
			json_dumps(skipd_tests)


def generate_tsuite_testclss(
		config: Dict[str, Any],
		chat_history: ChatHistory,
		template: str,
		template_corr_path: str,
		module_code: str,
		module_classes: List[str],
		classes_meths: Dict[str, List[str]],
		paths: Dict[str, Tuple[str, str]],
		context_names: Tuple[str, str],
		skipped_tests_file: str,
		gen_cache: Tuple[SqlConnection, SqlConnectionCursor],
		corr_cache: Tuple[SqlConnection, SqlConnectionCursor],
		debug: bool = False,
		debug_promptresp: bool = False,
		debug_log_config: Dict[str, str] = None,
		debug_errlog_config: Dict[str, str] = None
) -> None:
	"""
		TODO:
	"""
	gen_conn: SqlConnection = gen_cache[0]
	gen_conn_cur: SqlConnectionCursor = gen_cache[1]
	fplog_resp: TextIOWrapper = None

	project_name: str = context_names[0]

	absolute_paths: Tuple[str, str] = paths["absolute"]
	relative_paths: Tuple[str, str] = paths["relative"]
	base_tsuite_path: str = absolute_paths[1]
	base_rel_tsuite_path: str = relative_paths[1]

	fcls_name: str
	meth_name: str
	cls_dirname: str
	tsuite_path: str
	rel_tsuite_path: str

	gen_code_match: Match[str]
	gen_code: str = ""
	currcode_tree: Tree
	currcode_tree_root: TreeNode

	mod_cls_skipd: Dict[str, List[str]] = dict()
	cls_meths_skipd: List[str]
	skipd_tests: Dict[str, Any]

	chat_history.clear()
	for fclass in module_classes:
		fcls_name = reg_search(CLSDEF_PATT, fclass).group("cls_name")

		cls_meths_skipd = []

		cls_dirname = "class_" + fcls_name
		tsuite_path = path_join(base_tsuite_path, cls_dirname)
		rel_tsuite_path = path_join(base_rel_tsuite_path, cls_dirname)
		if os_fdexists(tsuite_path):
			os_dremove(tsuite_path)
		os_mkdirs(tsuite_path)

		if debug:
			print("Generating tests for Class '" + fcls_name + "' ...")
		for meth_def in classes_meths[fcls_name]:
			meth_name = reg_search(FUNCNAME_PATT, meth_def).group(1)

			full_methprompt: str = build_full_fbyf_methprompt(
				template,
				module_code,
				fcls_name,
				meth_name,
				(relative_paths[0], rel_tsuite_path),
				context_names
			)

			chat_history.add_message("context", CONTEXT_PROMPT)
			chat_history.add_message("user", full_methprompt)

			if debug_promptresp:
				print("\n\n##### Chat-History Pre-Response: #####")
				pprint(chat_history.history())

			prompt_exists: bool
			gen_conn_cur.execute(f"""
				SELECT * FROM `{project_name}`
				WHERE `prompt` = ?
				AND `model` = ?
			""", [full_methprompt, config["model"]])
			rows: List[Tuple[str, str, str]] = gen_conn_cur.fetchall()
			prompt_exists = len(rows) > 0

			not_skipped: bool = False
			if not prompt_exists:
				prompt_tokens: int = -1
				resp_tokens: int = -1

				if debug:
					now: datetime = datetime.now()
					datetime_now: str = (str(now.day) + "-" + str(now.month) + "-" + str(now.year) + "_" +
										 str(now.hour) + ":" + str(now.minute) + ":" + str(now.second))
					print("\tGenerating tests for Method '" + meth_name + "' ... Started at: " + datetime_now)
					print("\tLunghezza del (Method.) Prompt = " + str(len(reg_split(r"([ \n])+", full_methprompt)) * 3 / 2) + " tokens")

				oll: OllamaClient = OllamaClient(
					host=config["api_url"],
					headers={'Authorization': config["api_auth"]},
					timeout=config["timeout"],
				)
				response: Iterator[ChatResponse] | ChatResponse = oll.chat(
					config["model"],
					chat_history.history(),
					options=config["model_options"],
					stream=True,
					think=False,
				)

				if debug_log_config is not None:
					now: datetime = datetime.now()
					datetime_now: str = (str(now.day) + "-" + str(now.month) + "-" + str(now.year) + "_" +
										 str(now.hour) + "-" + str(now.minute) + "-" + str(now.second))

					prompt_parts: Tuple[str, str] = path_splitext(debug_log_config["prompt"])
					resp_parts: Tuple[str, str] = path_splitext(debug_log_config["resp"])

					prompt_path: str = path_join(
						debug_log_config["log_path"],
						prompt_parts[0] + "-" + datetime_now + "@" + fcls_name + "_" + meth_name + prompt_parts[1]
					)
					resp_path: str = path_join(
						debug_log_config["log_path"],
						resp_parts[0] + "-" + datetime_now + "@" + fcls_name + "_" + meth_name + resp_parts[1]
					)

					with open(prompt_path, "w") as fplog_prompt:
						fplog_prompt.write(full_methprompt)
						fplog_prompt.flush()

					fplog_resp = open(resp_path, "w")
				if debug:
					print("\t\tReceiving response... ", end="")
				full_response: str = ""
				if debug_log_config is None:
					for chunk in response:
						full_response += chunk['message']['content']
						if debug_promptresp:
							print(chunk['message']['content'], end="", flush=True)
						# Se è arrivato alla fine
						if "eval_count" in chunk:
							resp_tokens = chunk["eval_count"]
							prompt_tokens = chunk["prompt_eval_count"]
				else:
					try:
						for chunk in response:
							full_response += chunk['message']['content']
							if debug_promptresp:
								print(chunk['message']['content'], end="", flush=True)
							fplog_resp.write(chunk["message"]["content"])
							fplog_resp.flush()
							# Se è arrivato alla fine
							if "eval_count" in chunk:
								resp_tokens = chunk["eval_count"]
								prompt_tokens = chunk["prompt_eval_count"]
					except:
						fplog_resp.close()
				if debug:
					print("RECEIVED!")
				if debug_log_config is not None:
					fplog_resp.close()

				if (prompt_tokens == -1) or (resp_tokens == -1):
					now: datetime = datetime.now()
					datetime_now: str = (str(now.day) + "-" + str(now.month) + "-" + str(now.year) + "_" +
										 str(now.hour) + ":" + str(now.minute) + ":" + str(now.second))
					raise ValueError(f"C'è stato un errore!! ( Prompt_Tokens={prompt_tokens} | Resp_Tokens={resp_tokens} ) " +
									 f"{datetime_now}")

				# Se il modello non è andato in generazione ciclica -> allora la test-suite parziale è stata generata
				# (e me ne accorgo dalla finestra di contesto perfettamente satura)
				if (prompt_tokens + resp_tokens) < config["model_options"]["num_ctx"]:
					not_skipped: bool = True
					gen_code_match = reg_search(GENCODE_PATT, full_response, RegexFlags.MULTILINE)

					if debug:
						if (gen_code_match is None) and (debug_errlog_config is not None):
							log_path: str = debug_errlog_config["promptresp_log_path"]

							with open(path_join(log_path, debug_errlog_config["lasterr_prompt"]), "w",
									  encoding="utf-8") as fprompt:
								fprompt.write(full_methprompt)
								fprompt.flush()
							with open(path_join(log_path, debug_errlog_config["lasterr_resp"]), "w",
									  encoding="utf-8") as fresp:
								fresp.write(full_response)
								fresp.flush()

					gen_code = gen_code_match.group("gen_code")

					gen_conn_cur.execute(f"""
						INSERT INTO {project_name} (prompt, response, model)
						VALUES (?, ?, ?);
						""",
					[full_methprompt, gen_code, config["model"]])
					gen_conn.commit()
					if debug:
						print("\tGeneration Cache Updated!")
				else:
					print("\tSkipped generating tests for '" + meth_name + "' as the max context window has been reached")
					cls_meths_skipd.append(meth_name)
			else:
				not_skipped = True
				gen_code = rows[0][1]
				if debug:
					print("\tResponse of '" + meth_name + "' taken by the LLM Generated Cache")
				if debug_promptresp:
					print("\n\n\t#### Cached Response: ####")
					print(gen_code)

			if not_skipped:
				chat_history.add_message("llm", ("```python\n" + gen_code.rstrip("\n") + "\n```"))

				parttsuite_name: str = "test_" + meth_name + ".py"
				temp_parttsuite_name: str = "temp_" + parttsuite_name

				with open(path_join(tsuite_path, temp_parttsuite_name), "w", encoding="utf-8") as fp:
					fp.write(gen_code)

				corrected_code = correct_tsuite(
					path_join(tsuite_path, temp_parttsuite_name),
					config,
					chat_history,
					template_corr_path,
					absolute_paths,
					(relative_paths[0], rel_tsuite_path),
					context_names,
					corr_cache,
					debug=debug,
					debug_promptresp=debug_promptresp,
					debuglog_config=debug_errlog_config
				)

				with open(path_join(tsuite_path, temp_parttsuite_name), "w", encoding="utf-8") as fp:
					fp.write(corrected_code)
				os_rename(
					path_join(tsuite_path, temp_parttsuite_name),
					path_join(tsuite_path, parttsuite_name)
				)

			chat_history.clear()

		if len(cls_meths_skipd) > 0:
			mod_cls_skipd[fcls_name] = cls_meths_skipd

	if len(mod_cls_skipd.keys()) > 0:
		with open(skipped_tests_file, "w+") as fskipd:
			skipd_tests = json_loads(fskipd.read())
			skipd_tests["classes"] = mod_cls_skipd
			json_dumps(skipd_tests)