from typing import List, Dict, Set, Any, Tuple
from ._a_base_cfgvalidator import _ABaseConfigValidator

# ============= RegEx Utilities ============ #
from regex import (
	search as reg_search,
	Match,
)
# ========================================== #
# =========== RequestsForHumans Utilities =========== #
from requests import (
	get as req_get,
	Response as HttpResponse
)
# =================================================== #
# ============== OS Utilities ============== #
from os.path import exists as os_fdexists
# ========================================== #
# ============ Path Utilities ============ #
from os.path import join as path_join
# ======================================== #

from ....utils.path_validator import (
	PathValidator,
	EPathValidationErrorType
)

from ..exceptions import (
	ConfigExtraFieldsError,
	FieldDoesntExistsError,
	InvalidConfigValueError
)



class ProjsEnvironConfigValidator(_ABaseConfigValidator):
	"""
		Rappresenta un `IConfigValidator` per il file di configurazione che elenca le informazioni relative
		alla configurazione dell' ambiente focale per ogni progetto di i LLMs scelti genereranno i tests.
		
		Il file di configurazione letto sarà composto da un dizionario contenente:
			- "envconfig_dir" (str): Il nome dell' eventuale directory che contiene i files di configurazione per gli ambienti focali
			- "image_tag" (str): L' immagine 'base' di docker da cui derivare ogni immagine degli ambienti focali
			- "images_prefix" (str): Il prefisso da anteporre al tag delle immagini degli ambienti focali
			- "tools" (Dict[str, str]): Dizionario che contiene le path/directories relative ai tools da utilizzare in ogni ambiente focale. Contiene:
			
				* "tools_root" (str): La root path che contiene i tools da aggiungere all' interno di ogni ambiente focale
				* "linting" (str): Il nome della directory che contiene i tools per eseguire la verifica di linting all' interno dell' ambiente focale
				* "coverage" (str): Il nome della directory che contiene i tools per eseguire il calcolo della coverage all' interno dell' ambiente focale
				
			- "environ" (Dict[str, str]): Dizionario che contiene i parametri relativi agli ambienti focali. Contiene:
			
				* "path_prefix" (str): La path di base che ospita la Full Project Root Path, del progetto focale, all' interno di ogni ambiente focale
				* "lint_executer" (str): Il nome dello script che eseguirà la verifica di linting all' interno di ogni ambiente focale
				* "shared_dir" (str): Il nome della directory, all' interno del "path_prefix", che verrà utilizzata per la condivisione dei files tra il progetto focale e il suo ambiente
				
			- "project" (Dict[str, str]): Dizionario che contiene i parametri relativi ad ogni progetto focale. Contiene:
			
				* "dockerfile" (str): Il nome del dockerfile, creato da GenTestsAI, che costruirà l' immagine dell' ambiente focale
				* "pyversion_file" (str): Il nome dell' eventuale file testuale (in "envconfig_dir") che contiene la versione dell' interprete Python specifica per il progetto
				* "ext_deps_file" (str): Il nome dell' eventuale file testuale (in "envconfig_dir") che contiene le dipendenze non-Python del progetto focale
				* "python_deps_file" (str): Il nome dell' eventuale file testuale (in "envconfig_dir") che contiene le dipendenze Python del progetto focale
				* "pre_extdeps_script" (str): Il nome dell' eventuale script shell (in "envconfig_dir") da eseguire prima dell' installazione delle dipendenze non-Python del progetto focale
				* "post_extdeps_script" (str): Il nome dell' eventuale script shell (in "envconfig_dir") da eseguire dopo dell' installazione delle dipendenze non-Python del progetto focale
				* "post_pydeps_script" (str): Il nome dell' eventuale script shell (in "envconfig_dir") da eseguire dopo l' installazione delle dipendenze Python del progetto focale
	"""
	
	_OUTER_FIELDS: Set[str] = {
		"envconfig_dir",
		"images_prefix",
		"image_tag",
		"environ",
		"tools",
		"project"
	}
	_TOOLS_FIELDS: Set[str] = {
		"tools_root",
		"linting",
		"coverage"
	}
	_ENVIRON_FIELDS: Set[str] = {
		"path_prefix",
		"lint_executer",
		"shared_dir"
	}
	_1PROJ_FIELDS: Set[str] = {
		"dockerfile",
		"pyversion_file",
		"ext_deps_file", "python_deps_file",
		"pre_pydeps_script", "post_pydeps_script",
		"pre_extdeps_script", "post_extdeps_script"
	}
	
	_LINUXPATH_PATT: str = r"^(?P<linux_path>(/[\w.-]+/?)+)$"
	
	_SYNT_ERROR: str = 'La path specificata dal parametro "{param}" è invalida'
	_NOTEX_ERROR: str = 'La path specificata dal parametro "{param}" non esiste'
	_PERM_ERROR: str = 'Non si può accedere alla path specificata dal parametro "{param}"'
	_UNRE_ERROR: str = 'La path specificata dal parametro "{param}" non è raggiungibile'
	
	def __init__(
			self,
			config_dict: Dict[str, Any],
			full_roots: List[str],
			docker_hub_vers: str = "v2"
	):
		"""
			Costruisce un nuovo ProjsEnvironConfigValidator fornendogli il dizionario Python di configurazione
			che verrà associato a questo validatore
			
			Parameters
			----------
				config_dict: Dict[str, Any]
					Un dizionario variegato, indicizzato da stringhe, rappresentante il file di
					configurazione letto
					
				full_roots: List[str]
					Una lista di stringhe contenente le Full Project Root Paths dei progetti focali
					di cui verificare l' esistenza dei dockerfiles che generano gli ambienti focali
					
				docker_hub_vers: str
					Opzionale. Default = `v2`. Una stringa contenente la versione del  "Docker Hub Container Image Library"
					(come da endpoint) in cui verificare l' esistenza dell' immagine base specificata nel file di
					configurazione degli ambienti focali
			
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il dizionario fornito ha valore `None`
						- Il dizionario fornito è vuoto
						- La lista `full_roots` è vuota
						- La versione del "Docker Hub" fornita è "None"
						- La versione del "Docker Hub" fornita è una stringa vuota
		"""
		super().__init__(config_dict)
		
		if len(full_roots) == 0:
			raise ValueError()
		if (docker_hub_vers is None) or (docker_hub_vers == ""):
			raise ValueError()
		
		self._full_roots: List[str] = full_roots
		self._dhub_vers: str = docker_hub_vers
		
		self._pathval: PathValidator = PathValidator()
	
	
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		return (self._OUTER_FIELDS, set())
	
	
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		imgs_prefix: str = config_read["images_prefix"]
		image_tag: str = config_read["image_tag"]
		project: Dict[str, str] = config_read["project"]
		tools: Dict[str, str] = config_read["tools"]
		environ: Dict[str, str] = config_read["environ"]
		
		proj_fields = set(project.keys())
		if proj_fields < self._1PROJ_FIELDS:
			raise FieldDoesntExistsError()
		if proj_fields > self._1PROJ_FIELDS:
			raise ConfigExtraFieldsError()
		
		tools_fields = set(tools.keys())
		if tools_fields < self._TOOLS_FIELDS:
			raise FieldDoesntExistsError()
		if tools_fields > self._TOOLS_FIELDS:
			raise ConfigExtraFieldsError()
		
		environ_fields = set(environ.keys())
		if environ_fields < self._ENVIRON_FIELDS:
			raise FieldDoesntExistsError()
		if environ_fields > self._ENVIRON_FIELDS:
			raise ConfigExtraFieldsError()
		
		if imgs_prefix == "":
			raise InvalidConfigValueError()
		
		tools_root: str = tools["tools_root"]
		linting_tools: str = path_join(tools_root, tools["linting"])
		cov_tools: str = path_join(tools_root, tools["coverage"])
		
		self._assert_path(tools_root, "tools.tools_root")
		self._assert_path(linting_tools, "tools.linting")
		self._assert_path(cov_tools, "tools.coverage")
		
		if not os_fdexists(path_join(linting_tools, environ["lint_executer"])):
			raise InvalidConfigValueError()

		linux_path_found: Match[str]
		linux_path_found = reg_search(self._LINUXPATH_PATT, environ["path_prefix"])
		if linux_path_found.group("linux_path") is None:
			raise ValueError()
		
		is_pyvers_valid: bool = reg_search(r"[0-9]+\.[0-9]+(\.[0-9]+)?", image_tag) is not None
		if not is_pyvers_valid:
			raise InvalidConfigValueError("Il tag di fallback dell' immagine Python è invalido")
		self._assert_base_image_exists("registry.hub.docker.com", "python", image_tag)
	
	
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


	def _assert_base_image_exists(
			self,
			registry: str,
			image: str,
			tag: str
	):
		"""
			Verifica la validità del campo "os_image".
			
			Se la verifica ha successo quest' operazione è equivalente ad una no-op
			
			Parameters
			----------
				registry: str
					Una stringa contenente il registry da cui proviene l' immagine
					
				image: str
					Una stringa contenente il nome dell' immagine
					
				tag: str
					Una stringa contenente il tag dell' immagine
					
			Raises
			------
				InvalidConfigValueError
					Si verifica se l' immagine non esiste nel registry fornito
		"""
		url = f"https://{registry}/{self._dhub_vers}/repositories/library/{image}/tags/{tag}/"
		response: HttpResponse = req_get(url, timeout=5)
		if not (response.status_code == 200):
			raise InvalidConfigValueError()