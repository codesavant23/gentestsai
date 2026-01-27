from typing import Dict, Set, Any, Tuple
from ._a_base_cfgvalidator import _ABaseConfigValidator

# ============ Path Utilities ============ #
from os.path import join as path_join
from pathlib import Path as SystemPath
# ======================================== #

from ....utils.path_validator import (
	PathValidator,
	EPathValidationErrorType
)

from ..exceptions import (
	InvalidConfigValueError
)



class PromptsConfigValidator(_ABaseConfigValidator):
	"""
		Rappresenta un `IConfigValidator` per il file di configurazione che specifica i prompts da utilizzare
		per i processi di "Generazione" e "Correzione" di GenTestsAI.
		
		Il file di configurazione letto è un dizionario contenente:
		
			- "base_path" (str): La path assoluta di base che contiene le cartelle con i template prompts da utilizzare
			- "generic_dirname" (str): Il nome della directory, all' interno della "base_path" che contiene i template prompts indipendenti dal LLM
			- "func_fname" (str): Il nome del file che contiene il template prompt per funzioni
			- "meth_fname" (str): Il nome del file che contiene il template prompt per metodi
			- "corr_fname" (str): Il nome del file che contiene il template prompt per correzioni
	"""
	_ALL_FIELDS: Set[str] = {
		"prompts_path",
		"generic_dirname",
		"func_fname", "meth_fname", "corr_fname"
	}
	
	_SYNT_ERROR: str = 'La path specificata dal parametro "{param}" è invalida'
	_NOTEX_ERROR: str = 'La path specificata dal parametro "{param}" non esiste'
	_PERM_ERROR: str = 'Non si può accedere alla path specificata dal parametro "{param}"'
	_UNRE_ERROR: str = 'La path specificata dal parametro "{param}" non è raggiungibile'

	def __init__(
			self,
			config_dict: Dict[str, Any]
	):
		"""
			Costruisce un nuovo PromptsConfigValidator fornendogli il dizionario Python di configurazione
			che verrà associato a questo validatore
			
			Parameters
			----------
				config_dict: Dict[str, Any]
					Un dizionario variegato, indicizzato da stringhe, rappresentante il file di
					configurazione letto
			
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il dizionario fornito ha valore `None`
						- Il dizionario fornito è vuoto
		"""
		super().__init__(config_dict)
		
		self._pathval: PathValidator = PathValidator()
	
	
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		return (self._ALL_FIELDS, set())
	
	
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		base_path: str = config_read["base_path"]
		generic_dirname: str = config_read["generic_dirname"]
		
		func_fname: str = config_read["func_fname"]
		meth_fname: str = config_read["meth_fname"]
		corr_fname: str = config_read["corr_fname"]
	
		self._assert_path(base_path, "base_path")
		self._assert_templates(
			base_path,
			func_fname, meth_fname, corr_fname
		)
	
	
	def _ap__assert_optional(self, config_read: Dict[str, Any]):
		return
	
	
	def _ap__assert_purperrors(self, config_read: Dict[str, Any]):
		return
	

	##	============================================================
	##						PRIVATE METHODS
	##	============================================================

	
	def _assert_path(
			self,
			path_totest: str,
			param: str
	):
		"""
			Verifica che la path fornita sia:
				
				- Corretta sintatticamente ed esista nel sistema operativo.
				- Sia raggiungibile
				- Sia accessibile
			
			Parameters
			----------
				path_totest: str
					Una stringa contenente la path di cui verificare l' esistenza e la correttezza sintattica
					
				param: str
					Una stringa contenente il parametro di cui verificare la path data
			
			Raises
			------
				InvalidConfigValueError
					Si verifica se:
					
						- La path non è sintatticamente valida
						- La path fornita non esiste
						- La path fornita è inaccessibile
		"""
		self._pathval.set_error_msg(
			EPathValidationErrorType.SYNTACTIC,
			self._SYNT_ERROR.format(param=param)
		)
		self._pathval.set_error_msg(
			EPathValidationErrorType.NOTEXISTS,
			self._NOTEX_ERROR.format(param=param)
		)
		self._pathval.set_error_msg(
			EPathValidationErrorType.PERMISSION,
			self._PERM_ERROR.format(param=param)
		)
		self._pathval.set_error_msg(
			EPathValidationErrorType.INACCESSIBLE,
			self._UNRE_ERROR.format(param=param)
		)
		
		try:
			self._pathval.assert_path(path_totest)
		except (NotADirectoryError,
		        FileNotFoundError,
		        PermissionError,
		        OSError):
			raise InvalidConfigValueError()
	
		
	def _assert_templates(
			self,
			base_path: str,
			func_fname: str,
			meth_fname: str,
			corr_fname: str,
	):
		"""
			Verifica che i files dei template prompts esistano nel sistema operativo
			
			Parameters
			----------
				base_path: str
					Una stringa contenente la path base che contiene i prompts da utilizzare
					
				func_fname: str
					Una stringa contenente il nome del file con il template prompt per funzioni
					
				meth_fname: str
					Una stringa contenente il nome del file con il template prompt per metodi
					
				corr_fname: str
					Una stringa contenente il nome del file con il template prompt per correzioni
			
			Raises
			------
				InvalidConfigValueError
					Si verifica se, almeno in una directory, almeno uno dei files dei template prompts
					non esiste
		"""
		base_path: SystemPath = SystemPath(base_path)
		error_on: str
		for curr_path, dirs, files in base_path.walk(top_down=True):
			if curr_path != base_path:
				self._assert_path(
					path_join(curr_path, func_fname),
					"func_fname"
				)
				self._assert_path(
					path_join(curr_path, meth_fname),
					"meth_fname"
				)
				self._assert_path(
					path_join(curr_path, corr_fname),
					"corr_fname"
				)