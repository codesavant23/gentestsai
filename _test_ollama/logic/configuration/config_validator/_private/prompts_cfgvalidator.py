from typing import List, Dict, Set, Any, Tuple
from ._a_base_cfgvalidator import _ABaseConfigValidator

# ============ Path Utilities ============ #
from os.path import join as path_join
# ======================================== #
# ============== OS Utilities ============== #
from os import walk as os_walk
# ========================================== #
# ============= RegEx Utilities ============ #
from regex import search as reg_search
# ========================================== #

from ....utils.path_validator import (
	PathValidator,
	EPathValidationErrorType
)

from ..exceptions import (
	InvalidConfigValueError
)



class PromptsConfigValidator(_ABaseConfigValidator):
	"""
		Rappresenta un `IConfigValidator` per il file di configurazione che specifica i parametri relativi ai prompts.
		Esso specifica sia parametri generali dei prompts, sia i prompts da utilizzare per i processi di "Generazione"
		e "Correzione" di GenTestsAI.
		
		Il file di configurazione letto è un dizionario contenente:
		
			- "base_path" (str): La path assoluta di base che contiene le cartelle con i template prompts da utilizzare
			- "generic_dirname" (str): Il nome della directory, all' interno della "base_path" che contiene i template prompts indipendenti dal LLM
			- "file_names" (Dict[str, str]): Dizionario i nomi dei files di ogni template prompt da utilizzare. Contiene:
			
				* "functional" (str): Il nome del file che contiene il template prompt per funzioni
				* "methodal" (str): Il nome del file che contiene il template prompt per metodi
				* "correctional" (str): Il nome del file che contiene il template prompt per correzioni
				
			- "placeholders" (Dict[str, Any]): Dizionario che contiene la descrizione dei placeholders dei prompt. Contiene:
				
				* "start_del" (str): Il delimitatore iniziale di ogni placeholder
				* "end_del" (str): Il delimitatore finale di ogni placeholder
				* "common" (Dict[str, str]): Dizionario di placeholders comuni a tutte le categorie (functional, methodal, correctional) di template prompts utilizzati. Contiene:
				
					> "entity": Il placeholder (senza delimitatori) per l' entità (funzione/metodo)
					> "module": Il placeholder (senza delimitatori) per il nome del modulo focale
					> "project": Il placeholder (senza delimitatori) per il nome del progetto focale
					> "module_path": Il placeholder (senza delimitatori) per la path in cui è contenuto il modulo focale
					> "tsuite_path": Il placeholder (senza delimitatori) per la path che contiene la test-suite
					
				* "correctional" (Dict[str, str]): Dizionario di placeholders dei correctional template prompts utilizzati. Contiene:
					
					> "try_num": Il placeholder (senza delimitatori) per il numero di tentativo di correzione
					> "error_name": Il placeholder (senza delimitatori) per il nome dell' errore da correggere
					> "error_mess": Il placeholder (senza delimitatori) per il messaggio dell' errore da correggere
					
				* "code" (str): Il placeholder (senza delimitatori) per il codice focale nei functional e methodal template prompts utilizzati
				* "class_name" (str): Il placeholder (senza delimitatori) per il nome della classe nei methodal template prompts utilizzati
	"""
	_PLACEH_PATT: str = r"[A-Za-z0-9_]+"
	
	_OUTER_FIELDS: Set[str] = {
		"base_path", "generic_dirname",
		"file_names", "placeholders"
	}
	_FNAMES_FIELDS: Set[str] = {
		"functional", "methodal", "correctional"
	}
	_PLACEHS_FIELDS: Set[str] = {
		"start_del", "end_del",
		"common", "correctional",
		"code", "class_name"
	}
	
	_COMMON_FIELDS: Set[str] = {
		"entity",
		"module", "project",
		"module_path", "tsuite_path"
	}
	_CORR_FIELDS: Set[str] = {
		"try_num", "error_name", "error_mess"
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
		return (self._OUTER_FIELDS, set())
	
	
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		base_path: str = config_read["base_path"]
		generic_dirname: str = config_read["generic_dirname"]
		
		file_names: Dict[str, str] = config_read["file_names"]
		func_fname: str = file_names["functional"]
		meth_fname: str = file_names["methodal"]
		corr_fname: str = file_names["correctional"]
	
		self._assert_path(base_path, "base_path")
		self._assert_path(
			path_join(base_path, generic_dirname),
			"<base_path>/<generic_dirname>"
		)
		
		base_subdirs: List[str] = next(os_walk(base_path, topdown=True))[1]
		for prompt_dir in base_subdirs:
			self._assert_templates(
				path_join(base_path, prompt_dir),
				func_fname, meth_fname, corr_fname
			)
			
		self._assert_placehs(config_read["placeholders"])
	
	
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
					Una stringa contenente la path che contiene i prompts da verificare
					
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
		self._assert_path(
			path_join(base_path, func_fname),
			"func_fname"
		)
		self._assert_path(
			path_join(base_path, meth_fname),
			"meth_fname"
		)
		self._assert_path(
			path_join(base_path, corr_fname),
			"corr_fname"
		)
		
		
	@classmethod
	def _assert_placehs(cls, placeholders: Dict[str, Any]):
		placeh_names: List[str] = (list(placeholders["common"].values()) +
		                           list(placeholders["correctional"].values()))
		placeh_names.append(placeholders["code"])
		placeh_names.append(placeholders["class_name"])
		
		if len(set(placeh_names)) != len(placeh_names):
			raise InvalidConfigValueError()
		
		for placeh_name in placeh_names:
			cls._assert_placeh(placeh_name)
		
		
	@classmethod
	def _assert_placeh(cls, placeholder: str):
		"""
			Verifica se un placeholder è una stringa accettabile.
			
			Se la verifica ha successo quest' operazione è equivalente ad una no-op
			
			Raises
			------
				InvalidConfigValueError
					Si verifica se il placeholder contiene caratteri non accettabili
		"""
		is_placeh_valid: bool = reg_search(cls._PLACEH_PATT, placeholder) is not None
		if not is_placeh_valid:
			raise InvalidConfigValueError()