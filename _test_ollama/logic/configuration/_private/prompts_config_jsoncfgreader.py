from typing import Dict, Set, Any
from .. import AJsonConfigReader

# ============== OS Utilities ============== #
from os.path import exists as os_fdexists
# ========================================== #
# ============ Path Utilities ============ #
from os.path import join as path_join
from pathlib import Path as SystemPath
# ======================================== #

from ..exceptions import (
	WrongConfigFileFormatError,
	FieldDoesntExistsError,
	InvalidConfigValueError
)



class PromptsJsonConfigReader(AJsonConfigReader):
	"""
		Rappresenta un `AJsonConfigReader` per il file di configurazione dei prompts da utilizzare.
		
		Il file di configurazione letto conterrà i seguenti campi:
			- "base_path" (str): La path assoluta di base che contiene le cartelle con i template prompts da utilizzare
			- "generic_dirname" (str): Il nome della directory, all' interno della "base_path" fornita che contiene i template prompts indipendenti dal LLM
			- "func_fname" (str): Il nome del file che contiene il template prompt per funzioni
			- "meth_fname" (str): Il nome del file che contiene il template prompt per metodi
			- "corr_fname" (str): Il nome del file che contiene il template prompt per correzioni
	"""

	_ALL_FIELDS: Set[str] = {"prompts_path", "generic_prompts_dir", "func_prompt", "meth_prompt", "corr_prompt"}

	def __init__(
			self,
			file_path: str
	):
		"""
			Costruisce un nuovo PromptsJsonConfigReader leggendo il file di configurazione alla path
			specificata.
			
			Il formato del file deve essere un dizionario JSON composto nel seguente modo::
			
				{
				    "prompts_path": "<prompts_absolute_path>",
				    "generic_prompts_dir": "<dirname_for_generic_prompts>",
				    "func_prompt": "<prompt_filename_for_functions>",
				    "meth_prompt": "<prompt_filename_for_methods>",
				    "corr_prompt": "<prompt_filename_for_corrections>"
				}
			
			Parameters
			----------
				file_path: str
					Una stringa rappresentante la path assoluta contenente il file di configurazione
					da associare e leggere
			
			Raises
			------
				ValueError
					Si verifica se:
					
						- La path del file di configurazione fornita ha valore `None`
						- La path del file di configurazione fornita è una stringa vuota
						
				WrongConfigFileTypeError
					Si verifica se:
						
						- Il file di configurazione dato non è un file JSON
						- Il file non è un file JSON valido
					
				InvalidConfigFilepathError
					Si verifica se:
					
						- La path del file di configurazione fornita risulta invalida sintatticamente
						- Non è possibile aprire il file di configurazione
		"""
		super().__init__(file_path)
		
		self._base_path: str = None
		self._gen_dirname: str = None
		self._func_fname: str = None
		self._meth_fname: str = None
		self._corr_fname: str = None
	
	
	def _ap__assert_fields(self, config_read: Dict[str, Any]):
		config_fields: Set[str] = set(config_read.keys())
		if self._ALL_FIELDS > config_fields:
			raise FieldDoesntExistsError()
		
		extra_fields: Set[str] = (
			config_fields.difference(self._ALL_FIELDS).union(
			self._ALL_FIELDS.difference(config_fields))
		)
		if extra_fields != set():
			raise WrongConfigFileFormatError()
		
		self._base_path = config_read["prompts_path"]
		self._gen_dirname = config_read["generic_prompts_dir"]
		self._func_fname = config_read["func_prompt"]
		self._meth_fname = config_read["meth_prompt"]
		self._corr_fname = config_read["corr_prompt"]
		
		self._assert_paths()
		self._assert_templates()
	
	
	def _ap__format_result(
			self,
			config_read: Dict[str, Any]
	) -> Dict[str, Any]:
		return {
			"base_path": self._base_path,
			"generic_dirname": self._gen_dirname,
			"func_fname": self._func_fname,
			"meth_fname": self._meth_fname,
			"corr_fname": self._corr_fname,
		}
	

	##	============================================================
	##						PRIVATE METHODS
	##	============================================================

	
	def _assert_paths(self):
		"""
			Verifica che la base path, e la path dei prompts generici, siano corrette
			sintatticamente ed esistano nel sistema operativo.
			
			Raises
			------
				InvalidConfigValueError()
					Si verifica se:
					
						- La base path fornita non esiste (o la path non è sintatticamente valida)
						- La path dei prompts generici non esiste (o la path non è sintatticamente valida)
						- La path dei prompts generici esiste ma non si hanno i permessi necessari
		"""
		prompts_path: SystemPath
		try:
			prompts_path = SystemPath(self._base_path, self._gen_dirname)
			prompts_path.stat()
		except FileNotFoundError:
			raise InvalidConfigValueError()
		except PermissionError:
			raise InvalidConfigValueError()
		except OSError:
			raise InvalidConfigValueError()
	
			
	def _assert_templates(self):
		"""
			Verifica che i files dei template prompts esistano nel sistema operativo
			
			Raises
			------
				InvalidConfigValueError
					Si verifica se, almeno in una directory, almeno uno dei files dei template prompts
					non esiste
		"""
		prompts_path: SystemPath = SystemPath(self._base_path)
		files_exists: bool = True
		for curr_path, dirs, files in prompts_path.walk(top_down=True):
			if curr_path != prompts_path:
				files_exists = files_exists and os_fdexists(path_join(curr_path, self._func_fname))
				files_exists = files_exists and os_fdexists(path_join(curr_path, self._meth_fname))
				files_exists = files_exists and os_fdexists(path_join(curr_path, self._corr_fname))
				
				if not files_exists:
					raise InvalidConfigValueError()