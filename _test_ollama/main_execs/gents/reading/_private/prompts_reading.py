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

from main_execs.gents._private.llmnames_normalizing import normalize_llmname



def _invert_templnames_dict(
		templ_names: Dict[str, str]
) -> Dict[str, str]:
	return {v: k for k, v in templ_names.items()}


def _obtain_templ_paths(templ_basepath: str) -> List[str]:
	"""
		Calcola le paths di ogni template prompt data la path di una directory
		che li contiene
		
		Parameters
		----------
			templ_basepath: str
				Una stringa rappresentante la path che contiene i files dei template prompts
				
		Returns
		-------
			List[str]
				Una lista di stringhe contenente le paths ai files dei template prompts
	"""
	contents_list: List[str] = next(os_walk(templ_basepath, topdown=True))[2]
	
	for i, filename in enumerate(contents_list):
		contents_list[i] = path_join(templ_basepath, filename)
		
	return contents_list


def _read_templ_prompt(
		templ_path: str
) -> str:
	"""
		Legge un template prompt data la sua path
	"""
	templ_prompt: str = ""
	
	with open(templ_path, "r") as fp_tfile:
		templ_prompt = fp_tfile.read()
	
	return templ_prompt


def read_templprompts(
		templ_basepath: str,
		templ_names: Dict[str, str]
) -> Dict[str, str]:
	"""
		Legge i files dei template prompts dalla path specificata attenendosi
		ai nomi dei templates forniti
		
		Parameters
		----------
			templ_basepath: str
				Una stringa rappresentante la path che contiene i files dei template
				prompts
				
			templ_names: Dict[str, str]
				Un dizionario di stringhe, indicizzato da stringhe, contenente i nomi dei
				files che rappresentano i template prompts da leggere
				
		Returns
		-------
			Dict[str, str]
				Un dizionario di stringhe, indicizzato da stringhe, contenente i template prompts
				letti
	"""
	result: Dict[str, str] = dict()
	templ_paths: List[str] = _obtain_templ_paths(templ_basepath)
	
	inv_templ_fnames: Dict[str, str] = _invert_templnames_dict(templ_names)
	templ_fname: str
	for templ_path in templ_paths:
		templ_fname = path_split(templ_path)[1]
		templ_key = inv_templ_fnames.get(templ_fname, None)
		if templ_key is not None:
			result[templ_key] = _read_templ_prompt(templ_path)
			
	return result


def read_1model_templprompts(
		templ_basepath: str,
		model_name: str,
		algorithm: str, chars: int,
		templ_names: Dict[str, str],
) -> Dict[str, str]:
	"""
		Legge i files dei template prompts, di un particolare modello, attenendosi
		ai nomi dei templates forniti
		
		Parameters
		----------
			templ_basepath: str
				Una stringa rappresentante la path che contiene la directory del modello
				con all' interno i suoi template prompts specifici
				
			model_name: str
				Una stringa rappresentante il nome del LLM di cui si vogliono leggere
				i template prompts
				
			algorithm: str
				Una stringa rappresentante l' algoritmo di hashing utilizzato per i nomi
				delle directories dei template prompts specifici

			chars: int
				Un intero che indica il numero di caratteri utilizzati del digest del nome del modello
				
			templ_names: Dict[str, str]
				Un dizionario di stringhe, indicizzato da stringhe, contenente i nomi dei
				files che rappresentano i template prompts da leggere
				
		Returns
		-------
			Dict[str, str]
				Un dizionario di stringhe, indicizzato da stringhe, contenente i template prompts
				specifici del modello letti.
				Viene restituito il valore `None` se la directory del modello non esiste
	"""
	
	model_dirname = normalize_llmname(model_name, algorithm, chars)
	
	model_path: str = path_join(templ_basepath, model_dirname)
	if not os_fdexists(model_path):
		return None
	
	return read_templprompts(model_path, templ_names)