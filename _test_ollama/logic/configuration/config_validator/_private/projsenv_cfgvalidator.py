from typing import List, Dict, Set, Any, Tuple
from ._a_base_cfgvalidator import _ABaseConfigValidator

# ============= RegEx Utilities ============ #
from regex import (
	search as reg_search,
	Match,
	RegexFlag as RegexFlags,
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
from pathlib import Path as SystemPath
# ======================================== #

from ....utils.path_validator import (
	PathValidator,
	EPathValidationErrorType
)

from ..exceptions import (
	WrongConfigFileFormatError,
	FieldDoesntExistsError,
	InvalidConfigValueError
)



class ProjsEnvironConfigValidator(_ABaseConfigValidator):
	"""
		Rappresenta un `IConfigValidator` per il file di configurazione che elenca le informazioni relative
		alla configurazione dell' ambiente focale per ogni progetto di i LLMs scelti genereranno i tests.
		
		Il file di configurazione letto sarà composto da un dizionario contenente:
			- "envconfig_dir" (str): L' eventuale nome della directory che contiene i files di configurazione per gli ambienti focali
			- "os_image" (str): L' immagine 'base' di docker da cui derivare ogni immagine degli ambienti focali
			- "python_version" (str): La versione di fallback dell' interprete Python da utilizzare (nel caso in cui il progetto non ne abbia una specifica)
			- "tools" (Dict[str, str]): Dizionario che contiene le path/directories relative ai tools da utilizzare nell' ambiente focale. Contiene:
			
				* "tools_root" (str): La root path che contiene i tools da aggiungere all' interno di ogni ambiente focale
				* "linting" (str): Il nome della directory che contiene i tools per eseguire la verifica di linting all' interno dell' ambiente focale
				
			- "project" (Dict[str, str]): Dizionario che contiene i parametri relativi ad ogni progetto focale. Contiene:
			
				* "dockerfile" (str): Il nome del dockerfile, creato da GenTestsAI, che costruirà l' immagine dell' ambiente focale
				* "pyversion_file" (str): L' eventuale nome del file testuale (in "envconfig_dir") che contiene la versione dell' interprete Python specifica per il progetto
				* "ext_deps_file" (str): L' eventuale nome del file testuale (in "envconfig_dir") che contiene le dipendenze non-Python del progetto focale
				* "python_deps_file" (str): L' eventuale nome del file testuale (in "envconfig_dir") che contiene le dipendenze Python del progetto focale
				* "pre_extdeps_script" (str): L' eventuale nome dello script shell (in "envconfig_dir") da eseguire prima dell' installazione delle dipendenze Python del progetto focale
				* "post_extdeps_script" (str): L' eventuale nome dello script shell (in "envconfig_dir") da eseguire dopo dell' installazione delle dipendenze Python del progetto focale
	"""
	
	_OUTER_FIELDS: Set[str] = {
		"envconfig_dir",
		"os_image", "python_version",
		"tools",
		"project"
	}
	_TOOLS_FIELDS: Set[str] = {
		"tools_root",
		"linting"
	}
	_1PROJ_FIELDS: Set[str] = {
		"dockerfile",
		"pyversion_file",
		"ext_deps_file", "python_deps_file",
		"pre_extdeps_script", "post_extdeps_script"
	}
	
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
		envconfig_dir: str = config_read["envconfig_dir"]
		os_image: str = config_read["os_image"]
		py_version: str = config_read["python_version"]
		project: Dict[str, str] = config_read["project"]
		tools: Dict[str, str] = config_read["tools"]
		
		proj_fields = set(project.keys())
		if proj_fields < self._1PROJ_FIELDS:
			raise FieldDoesntExistsError()
		if proj_fields > self._1PROJ_FIELDS:
			raise WrongConfigFileFormatError()
		
		tools_fields = set(tools.keys())
		if tools_fields < self._TOOLS_FIELDS:
			raise FieldDoesntExistsError()
		if tools_fields > self._TOOLS_FIELDS:
			raise WrongConfigFileFormatError()
		
		tools_root: str = tools["tools_root"]
		linting_tools: str = tools["linting"]
		
		self._assert_path(tools_root, "tools_root")
		self._assert_path(linting_tools, "linting")
		
		is_pyvers_valid: bool = reg_search(r"[0-9]+\.[0-9]+(\.[0-9]+)?", py_version) is not None
		if not is_pyvers_valid:
			raise InvalidConfigValueError("La versione di fallback dell' interprete Python è invalida")
		
		# TODO: Implementare la validazione del nome del formato dell' immagine
		"""namespace: str = "library"
		image: str = os_image
		
		has_namespace: bool = "/" in os_image
		if has_namespace:
			namespace, image = os_image.split("/", 1)
		
		tag: str
		image, tag = image.split(":")
		#self._assert_base_image_exists(os_image, image, tag)
		"""
		
		self._pathval.set_error_msg(
			EPathValidationErrorType.SYNTACTIC,
			'La path specificata dal parametro "dockerfile" è invalida'
		)
		self._pathval.set_error_msg(
			EPathValidationErrorType.NOTEXISTS,
			'Il dockerfile specificato da "dockerfile" non esiste'
		)
		self._pathval.set_error_msg(
			EPathValidationErrorType.PERMISSION,
			'Non si può accedere alla path specificata dal parametro "dockerfile"'
		)
		self._pathval.set_error_msg(
			EPathValidationErrorType.INACCESSIBLE,
			'La path specificata dal parametro "dockerfile" non è raggiungibile'
		)
		envconfig_root: str
		dockf_path: str
		path: SystemPath
		for full_root in self._full_roots:
			envconfig_root = path_join(full_root, envconfig_dir)
			if os_fdexists(envconfig_root):
				dockf_path = path_join(full_root, project["dockerfile"])
				
				try:
					self._pathval.assert_path(dockf_path)
				except (NotADirectoryError,
				        FileNotFoundError,
				        PermissionError,
				        OSError):
					raise InvalidConfigValueError()
	
	
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
			namespace: str,
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
					
				namespace: str
					Una stringa contenente il namespace dell' immagine
					
				image: str
					Una stringa contenente il nome dell' immagine
					
				tag: str
					Una stringa contenente il tag dell' immagine
					
			Raises
			------
				InvalidConfigValueError
					Si verifica se l' immagine non esiste nel registry fornito
		"""
		#TODO: Da implementare, necessario OAuth
		"""
			url = f"https://{registry}/{self._dhub_vers}/repositories/{namespace}/{image}/tags/{tag}/"
			response: HttpResponse = req_get(url, timeout=5)
			if not (response.status_code == 200):
				raise InvalidConfigValueError()
		"""