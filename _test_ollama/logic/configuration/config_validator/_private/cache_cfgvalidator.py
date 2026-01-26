from typing import Dict, Set, Any, Tuple
from ._a_base_cfgvalidator import _ABaseConfigValidator

from ....utils.path_validator import (
	PathValidator,
	EPathValidationErrorType
)

from ..exceptions import (
	InvalidConfigValueError
)



class CacheConfigValidator(_ABaseConfigValidator):
	"""
		Rappresenta un `IConfigValidator` per il file di configurazione che specifica eventuali caches da usare
		per i processi di "Generazione" e "Correzione" di GenTestsAI.
		
		Il file di configurazione letto sarà composto da un dizionario contenente:
			- "cache_root" (str): La root path che contiene le caches che verranno utilizzate
			- "gen_cache" (str): Se esiste nel file letto, il nome del file che contiene la cache legata al processo di "Generazione"
			- "corr_cache" (str): Se esiste nel file letto, il nome del file che contiene la cache legata al processo di "Correzione"
	"""
	_REQ_FIELDS: Set[str] = {"cache_root"}
	_OPT_FIELDS: Set[str] = {"gen_cache", "corr_cache"}
	
	_SYNT_ERROR: str = 'La path specificata dal parametro "{param}" è invalida'
	_NOTEX_ERROR: str = 'La path specificata dal parametro "{param}" non esiste'
	_PERM_ERROR: str = 'Non si può accedere alla path specificata dal parametro "{param}"'
	_UNRE_ERROR: str = 'La path specificata dal parametro "{param}" non è raggiungibile'
	
	def __init__(
			self,
			config_dict: Dict[str, Any]
	):
		"""
			Costruisce un nuovo CacheConfigValidator fornendogli la path del file di configurazione
			che verrà associato a questo lettore
			
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
		
		self._cache_root: str = None
		self._gen_fname: str = None
		self._corr_fname: str = None
		
		self._pathval: PathValidator = PathValidator()
	
	
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		return (self._REQ_FIELDS, self._OPT_FIELDS)
	
	
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		if "cache_root" not in config_read:
			raise InvalidConfigValueError()
		cache_root: str = config_read["cache_root"]
		
		self._assert_path("cache_root", cache_root)
	
	
	def _ap__assert_optional(self, config_read: Dict[str, Any]):
		gen_cache: str = config_read.get("gen_cache", None)
		if gen_cache is not None:
			if not isinstance(gen_cache, str):
				self._assert_path("gen_cache", gen_cache)
		
		corr_cache: str = config_read.get("corr_cache", None)
		if corr_cache is not None:
			if not isinstance(corr_cache, str):
				self._assert_path("corr_cache", corr_cache)
	
	
	def _ap__assert_purperrors(self, config_read: Dict[str, Any]):
		return
	

	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _assert_path(
			self,
			param: str,
			path_totest: str
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