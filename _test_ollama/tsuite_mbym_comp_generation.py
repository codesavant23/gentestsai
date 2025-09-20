from typing import Dict, List, Tuple, Any

from os import (
	makedirs as os_mkdirs,
)
from shutil import (
	rmtree as os_dremove
)
from os.path import (
	sep as path_sep,
	exists as os_fdexists,
	commonpath as path_intersect,
	join as path_join,
	split as path_split,
	relpath as path_relative,
)

from sqlite3 import (
	Connection as SqlConnection,
	Cursor as SqlConnectionCursor
)

from template_reading import read_templ_frompath
from code_extraction import (
	extract_fmodule_code,
	separate_fmodule_code,
)
from tree_sitter import Tree
from chat_history import ChatHistory

from tsuite_fbyf_generation import (
	generate_tsuite_modfuncs,
	generate_tsuite_testclss
)



def generate_module_tsuite(
		module_path: str,
		skipped_tests_fname: str,
		config: Dict[str, Any],
		chat_history: ChatHistory,
		templs_paths: Tuple[str, str, str],
		context_names: Tuple[str, str],
		gen_cache: Tuple[SqlConnection, SqlConnectionCursor],
		corr_cache: Tuple[SqlConnection, SqlConnectionCursor],
		debug: bool = False,
		debug_promptresp: bool = False,
		debug_log_config: Dict[str, str] = None,
		debug_errlog_config: Dict[str, str] = None
) -> None:
	module_name: str = context_names[1]
	focal_proj_root: str = config["focal_proj_root"]

	# ========== Lettura del Template di Prompt ==========
	templ_func_path: str = templs_paths[0]
	templ_meth_path: str = templs_paths[1]
	templ_corr_path: str = templs_paths[2]

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

	# ========== Calcolo della directory che conterrà la test-suite del modulo ==========
	common_path: str = path_intersect([module_path, focal_proj_root])
	rel_path: str = module_path.replace(common_path, "").strip(path_sep)
	tsuite_path: str = path_join(
		path_join(config["test_proj_root"], rel_path), module_name
	)

	# ========== Creazione/sovrascrittura della directory test-suite ==========
	if debug:
		print("Calculated Test-Suite path for '" + context_names[1] + "' (\"" + context_names[0] + "\"): " + tsuite_path)

	if os_fdexists(tsuite_path):
		os_dremove(tsuite_path)
	os_mkdirs(tsuite_path)

	# ========== Calcolo delle path relative da inserire nei prompts di generazione/correzione ==========
	parent_path: str = path_intersect([
		focal_proj_root,
		focalmod_file,
		tsuite_path
	])
	to_remove: str = path_split(parent_path)[0]

	module_path_nof: str = path_split(focalmod_file)[0]

	focalmod_path_rel: str = path_relative(module_path_nof, start=to_remove)
	tsuite_path_rel: str = path_relative(tsuite_path, start=to_remove)

	focalmod_path_rel = "./" + (focalmod_path_rel.replace("\\", "/").lstrip("./")) + "/"
	tsuite_path_rel = "./" + (tsuite_path_rel.replace("\\", "/").lstrip("./")) + "/"

	skipped_tests_file: str = path_join(
		tsuite_path,
		skipped_tests_fname
	)
	with open(skipped_tests_file, "w") as fjson:
		fjson.write("{}")
		fjson.flush()

	# ========== Generazione Completa (con correzione e scrittura) delle test-suite parziali delle funzioni ==========
	generate_tsuite_modfuncs(
		config,
		chat_history,
		templ_func,
		templ_corr_path,
		raw_module_code,
		module_entities["funcs"],
		{
			"absolute": (module_path, tsuite_path),
			"relative": (focalmod_path_rel, tsuite_path_rel)
		},
		context_names,
		skipped_tests_file,
		gen_cache,
		corr_cache,
		debug=debug,
		debug_promptresp=debug_promptresp,
		debug_log_config=debug_log_config,
		debug_errlog_config=debug_errlog_config
	)

	# ========== Generazione Completa (con correzione e scrittura) delle test-suite parziali delle classi ==========
	generate_tsuite_testclss(
		config,
		chat_history,
		templ_meth,
		templ_corr_path,
		raw_module_code,
		module_entities["classes"],
		module_classes,
		{
			"absolute": (module_path, tsuite_path),
			"relative": (focalmod_path_rel, tsuite_path_rel)
		},
		context_names,
		skipped_tests_file,
		gen_cache,
		corr_cache,
		debug=debug,
		debug_promptresp=debug_promptresp,
		debug_log_config=debug_log_config,
		debug_errlog_config=debug_errlog_config
	)

	# ========== Rimozione dei files .pyc (i compilati) ==========
	"""Utilizza 'tsuite_path_rel' """