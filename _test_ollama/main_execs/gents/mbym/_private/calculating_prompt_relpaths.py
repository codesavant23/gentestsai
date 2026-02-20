from typing import Tuple
# ============ Path Utilities ============ #
from os.path import (
	split as path_split,
	commonpath as path_intersect,
	relpath as path_relative
)
# ======================================== #



def calculate_prompt_relpaths(
		focal_root: str,
		tsuite_path: str,
		module_path: str
) -> Tuple[str, str]:
	# Calcolo delle path relative da inserire nei prompts
	parent_path: str = path_intersect([
		focal_root,         # Full Project Root Path
		module_path,        # Path del modulo focale
		tsuite_path         # Path della directory test-suite del modulo focale
	])
	
	# Si rimuove fino alla cartella immediatamente superiore
	# così che il LLM capisca che sia la posizione relativa
	# sia della directory test-suite che del module-file focale
	to_remove: str = path_split(parent_path)[0]
	
	module_path_rel: str = path_relative(
		path_split(module_path)[0], start=to_remove
	)
	tsuite_path_rel: str = path_relative(tsuite_path, start=to_remove)
	
	# Si rendono le path POSIX-Like in caso si stia eseguendo in sistema operativo Windows
	module_path_rel = module_path_rel.replace("\\", "/").lstrip("./")
	tsuite_path_rel = tsuite_path_rel.replace("\\", "/").lstrip("./")

	module_path_rel = f"./{module_path_rel}/"
	tsuite_path_rel = f"./{tsuite_path_rel}/"
	
	return (module_path_rel, tsuite_path_rel)