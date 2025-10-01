from pprint import pprint
from typing import Dict, Tuple, List, Iterator, Any, Literal

from re import (
	Match,
	search as reg_search,
	split as reg_split,
	RegexFlag as RegexFlags,
)

from os.path import (
	join as path_join,
	split as path_split
)

from sqlite3 import (
	Connection as SqlConnection,
	Cursor as SqlConnectionCursor
)

from _test_ollama.logic.tsuite_gen.chat_history import ChatHistory
from _test_ollama.logic.tsuite_gen.template_reading import (
	read_templ_frompath
)
from _test_ollama.logic.tsuite_gen.prompt_building import (
	build_full_corrprompt
)

from ollama import Client as OllamaClient, ChatResponse

from py_compile import (
	compile as py_compile,
	PycInvalidationMode as Pyc_InvMode,
	PyCompileError
)
from pylint.lint import (
	Run as PylRunner
)
from _test_ollama.logic.tsuite_gen.errorcollector_pylreporter import (
	LintingRelatedProblem,
	ErrorCollectorPylReporter
)

from datetime import datetime

CONTEXT_PROMPT: str = "You are a professional Python developer."
GENCODE_PATT: str = r"(?:<think>[\S\n\t ]*</think>)?\s*```python\n?(?P<gen_code>[\s\S]+)\n?```"
PYTEST_ERROR_PATT: str = r"E\s+(?P<exc_name>[A-Za-z0-9_]+Error):\s+(?P<exc_mess>.*)"



def correct_tsuite_1time(
		wrong_tsuite: str,
		error: Tuple[str, str],
		num_try: int,
		correction_type: Literal["synt", "lint"],
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

	chat_history.add_message("user", full_corrprompt)

	print("\n\n##### Chat-History Pre-Response: #####")
	pprint(chat_history.history())

	prompt_exists: bool
	corr_conn_cur.execute(f"""
		SELECT * FROM `{project_name}`
		WHERE `corr_type` = ?
		AND `num_try` = ? 
		AND `prompt` = ?
		AND `model` = ?
	""", [
		correction_type,
		num_try,
		full_corrprompt,
		config["model"]
	])
	rows: List[Tuple[str, str, str, str, str]] = corr_conn_cur.fetchall()
	prompt_exists = len(rows) > 0

	corr_code_match: Match[str]
	corr_code: str

	if not prompt_exists:
		prompt_tokens: int = -1
		resp_tokens: int = -1

		if debug:
			print("(Try: "+str(num_try+1)+") Correcting code of the module '" + context_names[1] + "' (\"" + context_names[0] + "\") ...")
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
		for chunk in response:
			full_response += chunk['message']['content']
			# Se è arrivato alla fine
			if "eval_count" in chunk:
				resp_tokens = chunk["eval_count"]
				prompt_tokens = chunk["prompt_eval_count"]
			print(chunk['message']['content'], end="")
		if debug:
			print("RECEIVED!")

		if (prompt_tokens + resp_tokens) >= config["model_options"]["num_ctx"]:
			raise Exception(f"Finestra di contesto saturata (PT = {prompt_tokens}, RT = {resp_tokens})")

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
			INSERT INTO {project_name} (corr_type, num_try, prompt, response, model)
			VALUES (?, ?, ?, ?, ?);
		""",
		[
			correction_type,
			num_try,
			full_corrprompt,
			corr_code,
			config["model"]
		])
		corr_conn.commit()
		if debug:
			print("Correction Cache Updated!", flush=True)
	else:
		corr_code = rows[0][3]
		if debug:
			print("Correction of error '" + error[0] + "' on '" + context_names[1] + "' (\"" + context_names[0] + "\") test-suite taken by the LLM Correction Cache", flush=True)
		print("\n\n\t#### Cached Response: ####")
		print(corr_code)

	chat_history.add_message("llm", ("```python\n" + corr_code.rstrip("\n") + "\n```"))

	return corr_code


def correct_tsuite(
		wrong_parttsuite_path: str,
		config: Dict[str, Any],
		chat_history: ChatHistory,
		templ_path: str,
		absolute_paths: Tuple[str, str],
		relative_paths: Tuple[str, str],
		context_names: Tuple[str, str],
		corr_cache: Tuple[SqlConnection, SqlConnectionCursor],
		debug: bool = False,
		debug_promptresp: bool = False,
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
	times_tried: int = 0
	max_tries: int = config["max_corr_times"]
	while (not exec_success) and (times_tried < max_tries):
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
				curr_code = fp.read()

			curr_code = correct_tsuite_1time(
				curr_code,
				(except_name, except_mess),
				times_tried,
				"synt",
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
				fp.flush()

			times_tried += 1

	if not exec_success:
		raise Exception("Errore! La test-suite parziale '"+wrong_parttsuite_path+"' non è stata corretta in sintassi")

	# ========== Correzione Non-Sintattica della test suite parziale ==========
	exec_success = False
	times_tried = 0

	full_proj_root: str = path_split(absolute_paths[0])[0]
	pyl_args: List[str] = [
		"--source-roots="+full_proj_root,
		wrong_parttsuite_path
	]

	error_found: LintingRelatedProblem
	error_position: Tuple[int, int]

	err_reporter: ErrorCollectorPylReporter = ErrorCollectorPylReporter()
	while (not exec_success) and (times_tried < max_tries):
		with open(wrong_parttsuite_path, "r") as fp:
			curr_code = fp.read()

		err_reporter.init_reporter()
		PylRunner(
			pyl_args,
			reporter=err_reporter,
			exit=False
		)

		if err_reporter.has_found_any_problem():
			error_found = err_reporter.get_found_problems()[0]

			error_position = error_found.get_code_position()
			except_name = error_found.get_short_name()
			except_mess = error_found.get_message() + f" (at line {error_position[0]}, column {error_position[1]})"

			print("Errore di PyLint: " + error_found.build_formatted_message())

			curr_code = correct_tsuite_1time(
				curr_code,
				(except_name, except_mess),
				times_tried,
				"lint",
				config,
				chat_history,
				templ_path,
				relative_paths,
				context_names,
				corr_cache,
				debug=debug,
				#debug_promptresp=debug_promptresp,
				debuglog_config=debuglog_config
			)

			with open(wrong_parttsuite_path, "w") as fp:
				fp.write(curr_code)
				fp.flush()

			times_tried += 1
		else:
			exec_success = True

	if not exec_success:
		raise Exception("Errore! La test-suite parziale '"+wrong_parttsuite_path+"' non è stata corretta in linting")

	return curr_code