from typing import Dict, Set, Any, Tuple
from ._a_base_cfgvalidator import _ABaseConfigValidator

# ============ Path Utilities ============ #
from os.path import join as path_join
# ======================================== #
from ....utils.path_validator import (
	EPathValidationErrorType,
	PathValidator
)

from ..exceptions import (
	InvalidConfigValueError,
	ConfigExtraFieldsError,
	FieldDoesntExistsError
)



class CalcCovConfigValidator(_ABaseConfigValidator):
	"""
		Rappresenta un `IConfigValidator` per il file di configurazione delle opzioni
		di calcolo coverage delle test-suites.
		
		Il file di configurazione letto è un dizionario contenente:
		
			- "covconfig_dir" (str): Il nome dell' eventuale directory che corrisponde alla Cov-config Project Root Path di ogni progetto focale
			- "pytargs_fname" (str): Il nome dell' eventuale file JSON che contiene la lista di argomenti per `pytest`
			- "covargs_fname" (str): Il nome dell' eventuale file JSON che contiene la lista di argomenti per `pytest`
	"""
	
	_REQ_FIELDS: Set[str] = {
		"covconfig_dir",
		"pytargs_fname",
		"covargs_fname",
		"environ"
	}
	_ENVIRON_FIELDS: Set[str] = {
		"humancov_script",
		"llmcov_script",
	}
	
	_SYNT_ERROR: str = 'La path specificata dal parametro "{param}" è invalida'
	_NOTEX_ERROR: str = 'La path specificata dal parametro "{param}" non esiste'
	_PERM_ERROR: str = 'Non si può accedere alla path specificata dal parametro "{param}"'
	_UNRE_ERROR: str = 'La path specificata dal parametro "{param}" non è raggiungibile'
	
	def __init__(
			self,
			config_dict: Dict[str, Any],
			covtools_root: str
	):
		"""
			Costruisce un nuovo ProjectsConfigValidator leggendo il file di configurazione alla path
			specificata.
			
			Parameters
			----------
				config_dict: Dict[str, Any]
					Un dizionario variegato, indicizzato da stringhe, rappresentante
					il file di configurazione letto
					
				covtools_root: str
					Una stringa rappresentante la path che contiene i tools per la coverage
					da utilizzare all' interno degli ambienti focali

			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `config_dict` ha valore `None`
						- Il parametro `config_dict` è un dizionario vuoto
						- Il parametro `covtools_root` ha valore `None`
						- Il parametro `covtools_root` è una stringa vuota
		"""
		super().__init__(config_dict)
		
		if (covtools_root is None) or (covtools_root == ""):
			raise ValueError()
		
		self._covtools_root: str = covtools_root
		self._pathval: PathValidator = PathValidator()
	
	
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		return (self._REQ_FIELDS, set())
	
	
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		covconfig_dir: str = config_read["covconfig_dir"]
		pytargs_fname: str = config_read["pytargs_fname"]
		covargs_fname: str = config_read["covargs_fname"]
		environ: Dict[str, str] = config_read["environ"]
		
		if covconfig_dir == "":
			raise InvalidConfigValueError()
		if pytargs_fname == "":
			raise InvalidConfigValueError()
		if covargs_fname == "":
			raise InvalidConfigValueError()
		
		environ_fields = set(environ.keys())
		if environ_fields < self._ENVIRON_FIELDS:
			raise FieldDoesntExistsError()
		if environ_fields > self._ENVIRON_FIELDS:
			raise ConfigExtraFieldsError()
		
		self._assert_path(
			path_join(self._covtools_root, environ["humancov_script"]),
			"environ.humancov_script"
		)
		self._assert_path(
			path_join(self._covtools_root, environ["llmcov_script"]),
			"environ.llmcov_script"
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