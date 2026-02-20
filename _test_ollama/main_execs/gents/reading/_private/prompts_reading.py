from typing import List, Dict

# ============ Path Utilities ============ #
from os.path import (
	join as path_join,
	split as path_split
)
# ======================================== #
# ============== OS Utilities ============== #
from os import walk as os_walk
from os.path import exists as os_fdexists
# ========================================== #

from main_execs.gents import normalize_llmname



def _read_templprompts(
		paths: List[str],
		templs_names: Dict[str, str]
) -> Dict[str, str]:
	templ_prompts: Dict[str, str] = dict()
	templ_fname: str
	dict_key: str
	
	for templ_path in paths:
		templ_fname = path_split(templ_path)[1]
		dict_key = next(k for k, v in templs_names.items() if v == templ_fname)
		
		with open(templ_path) as templ_file:
			templ_prompts[dict_key] = templ_file.read()
	
	return templ_prompts


def read_fallback_templprompts(
		fallback_path: str,
		templs_names: Dict[str, str]
) -> Dict[str, str]:
	templ_paths: List[str] = next(os_walk(fallback_path))[2]
	
	return _read_templprompts(templ_paths, templs_names)


def read_1model_templprompts(
		prompts_basepath: str,
		model_name: str,
		algorithm: str, chars: int,
		templs_names: Dict[str, str],
) -> Dict[str, str]:
	model_dirname = normalize_llmname(model_name, algorithm, chars)
	
	model_path: str = path_join(prompts_basepath, model_dirname)
	if not os_fdexists(path_join(model_path)):
		return None
	
	templ_paths: List[str] = next(os_walk(model_path, topdown=True))[2]
	
	return _read_templprompts(templ_paths, templs_names)