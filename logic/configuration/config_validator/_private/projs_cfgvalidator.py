from typing import List, Dict, Set, Any, Tuple
from ._a_base_cfgvalidator import _ABaseConfigValidator

# ============ Path Utilities ============ #
from os.path import (
	sep as path_sep,
	altsep as path_altsep,
	join as path_join
)
_PATH_SEPS: str = f"{path_sep}{path_altsep if path_altsep is not None else ''}"
# ======================================== #
from ....utils.path_validator import (
	EPathValidationErrorType,
	PathValidator
)

from ..exceptions import (
	FieldDoesntExistsError,
	ConfigExtraFieldsError,
	InvalidConfigValueError
)



class ProjectsConfigValidator(_ABaseConfigValidator):
	"""
		Rappresenta un `IConfigValidator` per il file di configurazione dei progetti focali di cui
		verranno generati i tests.
		
		Il file di configurazione letto è un dizionario contenente:
		
			-   Un entry dizionario per ogni progetto focale la cui chiave è il nome del progetto.
				Ogni dizionario contiene, obbligatoriamente:
				
					* "full_root" (str): La Full Project Root Path del progetto (come path assoluta)
					* "focal_root" (str): La Focal Project Root Path del progetto (come path relativa alla Full Project Root Path)
					* "tests_root" (str): La Tests Project Root Path del progetto (come path relativa alla Full Project Root Path)
					
				e può contenere, opzionalmente:
					
					* "focal_excluded" (List[str]): Una lista di paths relative alla Focal Project Root Path, da non considerare come parte del codice focale
					* "tests_excluded" (List[str]): Una lista di paths relative alla Tests Project Root Path, da non considerare come parte della test-suite dell' intero progetto
	"""
	
	_REQ_FIELDS: Set[str] = {"full_root", "focal_root", "tests_root"}
	_OPT_FIELDS: Set[str] = {"focal_excluded", "tests_excluded"}
	
	_SYNT_ERROR: str = 'La path specificata dal parametro "{param}" è invalida (progetto "{proj_name}")'
	_NOTEX_ERROR: str = 'La path specificata dal parametro "{param}" non esiste (progetto "{proj_name}")'
	_PERM_ERROR: str = 'Non si può accedere alla path specificata dal parametro "{param}" (progetto "{proj_name}")'
	_UNRE_ERROR: str = 'La path specificata dal parametro "{param}" non è raggiungibile (progetto "{proj_name}")'
	
	def __init__(
			self,
			config_dict: Dict[str, Any]
	):
		"""
			Costruisce un nuovo ProjectsConfigValidator leggendo il file di configurazione alla path
			specificata.
			
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
	
	
	def _p__efields_strict(self) -> bool:
		return False
	
	
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		return (set(), set())
	
	
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		full_root: str
		focal_root: str
		tests_root: str
		focal_excl: List[str]
		
		for proj_name, project in config_read.items():
			config_fields = set(project.keys())
			
			if config_fields < self._REQ_FIELDS:
				raise FieldDoesntExistsError()
			
			full_root = project["full_root"].rstrip(_PATH_SEPS)
			focal_root = project["focal_root"].rstrip(_PATH_SEPS)
			tests_root = project["tests_root"].rstrip(_PATH_SEPS)
			
			self._assert_path(full_root, proj_name, "full_root")
			self._assert_path(path_join(full_root, focal_root), proj_name, "focal_root")
			self._assert_path(path_join(full_root, tests_root), proj_name, "tests_root")

	
	def _ap__assert_optional(self, config_read: Dict[str, Any]):
		focal_excluded: List[str]
		tests_excluded: List[str]
		
		full_root: str
		focal_root: str
		tests_root: str
		
		for proj_name, project in config_read.items():
			config_fields = set(project.keys())
			
			extra_fields = (
				config_fields.difference(self._REQ_FIELDS).union(
				self._REQ_FIELDS.difference(config_fields))
			)
			if extra_fields.difference(self._OPT_FIELDS) != set():
				raise ConfigExtraFieldsError()
			
			full_root = project["full_root"].rstrip(_PATH_SEPS)
			focal_root = path_join(full_root, project["focal_root"].rstrip(_PATH_SEPS))
			tests_root = path_join(full_root, project["tests_root"].rstrip(_PATH_SEPS))
			
			focal_excluded = project.get("focal_excluded", None)
			if focal_excluded is not None:
				self._assert_excluded_paths(
					focal_root,
					focal_excluded,
					proj_name,
					"focal_excluded"
				)
				
			tests_excluded = project.get("tests_excluded", None)
			if tests_excluded is not None:
				self._assert_excluded_paths(
					tests_root,
					tests_excluded,
					proj_name,
					"tests_excluded"
				)
	
	
	def _ap__assert_purperrors(self, config_read: Dict[str, Any]):
		return
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _assert_path(
			self,
			path_totest: str,
			proj_name: str,
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
					
				proj_name: str
					Una stringa contenente il nome del progetto focale di cui testare la path
					
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
			self._SYNT_ERROR.format(param=param, proj_name=proj_name)
		)
		self._pathval.set_error_msg(
			EPathValidationErrorType.NOTEXISTS,
			self._NOTEX_ERROR.format(param=param, proj_name=proj_name)
		)
		self._pathval.set_error_msg(
			EPathValidationErrorType.PERMISSION,
			self._PERM_ERROR.format(param=param, proj_name=proj_name)
		)
		self._pathval.set_error_msg(
			EPathValidationErrorType.INACCESSIBLE,
			self._UNRE_ERROR.format(param=param, proj_name=proj_name)
		)
		
		try:
			self._pathval.assert_path(path_totest)
		except (NotADirectoryError,
		        FileNotFoundError,
		        PermissionError,
		        OSError):
			raise InvalidConfigValueError()


	def _assert_excluded_paths(
			self,
			root: str,
			excluded_list: List[str],
			proj_name: str,
			param: str
	):
		"""
			Verifica la correttezza dei campi che riguardano le paths escluse.
			
			Se la verifica ha successo quest' operazione è equivalente ad una no-op
			
			Parameters
			----------
				root: str
					Una stringa contenente la root path a cui sono relative le paths escluse fornite
			
				excluded_list: List[str]
					Una lista di stringhe contenente le path relative escluse
					
				proj_name: str
					Una stringa contenente il nome del progetto di cui si sta verificando le paths escluse
					
				param: str
					Una stringa contenente il nome del campo che si sta verificando
			
			Raises
			------
				InvalidConfigValueError
					Si verifica se almeno una delle paths escluse è invalida
		"""
		for path in excluded_list:
			self._assert_path(path_join(root, path), proj_name, param)