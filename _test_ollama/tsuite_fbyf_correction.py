from typing import Dict, Tuple, List, Iterator, Any
from functools import reduce

from io import (
	StringIO
)

from re import (
	Match,
	search as reg_search,
	split as reg_split,
	RegexFlag as RegexFlags,
)

from os.path import (
	join as path_join
)

from sqlite3 import (
	Connection as SqlConnection,
	Cursor as SqlConnectionCursor
)

from chat_history import ChatHistory
from template_reading import (
	read_templ_frompath
)
from prompt_building import (
	build_full_corrprompt
)

from ollama import Client as OllamaClient, ChatResponse

from py_compile import (
	compile as py_compile,
	PycInvalidationMode as Pyc_InvMode,
	PyCompileError
)
from pytest import (
	main as pytest_run,
	ExitCode as EPytestExitCode
)
from regfailure_pytplugin import (
	RegisterFailurePyTestPlugin
)

from datetime import datetime

CONTEXT_PROMPT: str = "You are a professional Python developer."
GENCODE_PATT: str = r"(?:<think>[\S\n\t ]*</think>)?\s*```python\n?(?P<gen_code>[\s\S]+)\n?```"
PYTEST_ERROR_PATT: str = r"E\s+(?P<exc_name>[A-Za-z0-9_]+Error):\s+(?P<exc_mess>.*)"



def correct_tsuite_1time(
		wrong_tsuite: str,
		error: Tuple[str, str],
		config: Dict[str, Any],
		chat_history: ChatHistory,
		templ_path: str,
		relative_paths: Tuple[str, str],
		context_names: Tuple[str, str],
		corr_cache: Tuple[SqlConnection, SqlConnectionCursor],
		debug: bool = False,
		debuglog_config: Dict[str, str] = None
) -> str:
	corr_conn: SqlConnection = corr_cache[0]
	corr_conn_cur: SqlConnectionCursor = corr_cache[1]
	project_name: str = context_names[0]

	templ: str = read_templ_frompath(templ_path)
	full_corrprompt: str = build_full_corrprompt(
		templ,
		wrong_tsuite,
		error,
		relative_paths,
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

	corr_code_match: Match[str]
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
			options=config["model_options"],
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

		corr_code_match = reg_search(GENCODE_PATT, full_response, RegexFlags.MULTILINE)

		if debug:
			if (corr_code_match is None) and (debuglog_config is not None):
				now: datetime = datetime.now()
				datetime_now: str = (str(now.day) + "-" + str(now.month) + "-" + str(now.year) + "_" +
									 str(now.hour) + "-" + str(now.minute) + "-" + str(now.second))
				log_path: str = debuglog_config["promptresp_log_path"]
				promptfile_name: str = debuglog_config["lasterr_prompt"] + "_" + datetime_now
				respfile_name: str = debuglog_config["lasterr_resp"] + "_" + datetime_now

				with open(path_join(log_path, promptfile_name), "w", encoding="utf-8") as fprompt:
					fprompt.write(full_corrprompt)
				with open(path_join(log_path, respfile_name), "w", encoding="utf-8") as fresp:
					fresp.write(full_response)

		corr_code = corr_code_match.group("gen_code")

		corr_conn_cur.execute(f"""
			INSERT INTO {project_name} (prompt, response, model)
			VALUES (?, ?, ?);
		""",
		[full_corrprompt, corr_code, config["model"]])
		corr_conn.commit()
		if debug:
			print("Correction Cache Updated!")
	else:
		corr_code = rows[0][1]
		if debug:
			print("Correction of error '" + error[0] + "' on '" + context_names[1] + "' (\"" + context_names[0] + "\") test-suite taken by the LLM Correction Cache")

	return corr_code


def correct_tsuite(
		wrong_parttsuite_path: str,
		config: Dict[str, Any],
		chat_history: ChatHistory,
		templ_path: str,
		relative_paths: Tuple[str, str],
		context_names: Tuple[str, str],
		corr_cache: Tuple[SqlConnection, SqlConnectionCursor],
		debug: bool = False,
		debuglog_config: Dict[str, str] = None
):
	wrong_parttsuite: str
	with open(wrong_parttsuite_path, "r") as fp:
		wrong_parttsuite = fp.read()

	curr_code: str = wrong_parttsuite
	except_name: str
	except_mess: str

	# ========== Correzione Sintattica della test suite parziale ==========
	exec_success: bool = False
	while not exec_success:
		try:
			py_compile(
				wrong_parttsuite_path,
				doraise=True,
				invalidation_mode=Pyc_InvMode.TIMESTAMP
			)
			exec_success = True
		except PyCompileError as err:
			except_name = reg_search(r"[A-Z][\w_\-]+Error", err.exc_type_name).group()
			except_mess = err.args[0]

			with open(wrong_parttsuite_path, "r") as fp:
				curr_code = reduce(lambda acc, x: acc + "\n" + x, fp.readlines())

			curr_code = correct_tsuite_1time(
				curr_code,
				(except_name, except_mess),
				config,
				chat_history,
				templ_path,
				relative_paths,
				context_names,
				corr_cache,
				debug=debug,
				debuglog_config=debuglog_config
			)

			with open(wrong_parttsuite_path, "w") as fp:
				fp.write(curr_code)

	# ========== Correzione Non-Sintattica della test suite parziale ==========
	exec_success = False
	failure_plugin: RegisterFailurePyTestPlugin = RegisterFailurePyTestPlugin()

	pytest_output: str
	error_info: Dict[str, str]

	while not exec_success:
		with open(wrong_parttsuite_path, "r") as fp:
			curr_code = fp.read()

		failure_plugin.init_plugin()
		pytest_run([
			"-q",
			"--disable-warnings",
			wrong_parttsuite_path
		], plugins=[failure_plugin])

		if failure_plugin.has_run_failed():
			error_info = failure_plugin.get_error_info()

			except_name = error_info["except_name"]
			except_mess = error_info["except_message"]

			curr_code = correct_tsuite_1time(
				curr_code,
				(except_name, except_mess),
				config,
				chat_history,
				templ_path,
				relative_paths,
				context_names,
				corr_cache,
				debug=debug,
				debuglog_config=debuglog_config
			)

			with open(wrong_parttsuite_path, "w") as fp:
				fp.write(curr_code)
		else:
			exec_success = True

	return curr_code