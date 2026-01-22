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
			- "project" (Dict[str, str]): Dizionario che contiene i parametri relativi ad ogni progetto focale. Contiene:
			
				* "dockerfile" (str): Il nome del dockerfile, creato da GenTestsAI, che costruirà l' immagine dell' ambiente focale
				* "pyversion_file" (str): L' eventuale nome del file testuale (in "envconfig_dir") che contiene la versione dell' interprete Python specifica per il progetto
				* "external_deps_file" (str): L' eventuale nome del file testuale (in "envconfig_dir") che contiene le dipendenze non-Python del progetto focale
				* "python_deps_file" (str): L' eventuale nome del file testuale (in "envconfig_dir") che contiene le dipendenze Python del progetto focale
				* "pre_extdeps_script" (str): L' eventuale nome dello script shell (in "envconfig_dir") da eseguire prima dell' installazione delle dipendenze Python del progetto focale
				* "post_extdeps_script" (str): L' eventuale nome dello script shell (in "envconfig_dir") da eseguire dopo dell' installazione delle dipendenze Python del progetto focale
	"""
	
	_OUTER_FIELDS: Set[str] = {
		"envconfig_dir",
		"os_image", "python_version",
		"project"
	}
	_1PROJ_FIELDS: Set[str] = {
		"dockerfile",
		"pyversion_file",
		"external_deps_file", "python_deps_file",
		"pre_extdeps_script", "post_extdeps_script"
	}
	
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
	
	
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		return (self._OUTER_FIELDS, set())
	
	
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		_OUTER_FIELDS: Set[str] = {
			"envconfig_dir",
			"os_image", "python_version",
			"project"
		}
		envconfig_dir: str = config_read["envconfig_dir"]
		os_image: str = config_read["os_image"]
		py_version: str = config_read["python_version"]
		project: Dict[str, str] = config_read["project"]
		
		oneproj_fields = set(project.keys())
		if oneproj_fields < self._1PROJ_FIELDS:
			raise FieldDoesntExistsError()
		if oneproj_fields > self._1PROJ_FIELDS:
			raise WrongConfigFileFormatError()
		
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
		
		envconfig_root: str
		dockf_path: str
		path: SystemPath
		for full_root in self._full_roots:
			envconfig_root = path_join(full_root, envconfig_dir)
			if os_fdexists(envconfig_root):
				dockf_path = path_join(full_root, project["dockerfile"])

				try:
					path = SystemPath(dockf_path)
					path.stat()
				except NotADirectoryError:
					raise InvalidConfigValueError(f'La path specificata dal parametro "dockerfile" è invalida')
				except FileNotFoundError:
					raise InvalidConfigValueError(f'Il dockerfile specificato da "dockerfile" non esiste')
				except PermissionError:
					raise InvalidConfigValueError(f'Non si può accedere alla path specificata dal parametro "dockerfile"')
				except OSError:
					raise InvalidConfigValueError(f'La path specificata dal parametro "dockerfile" non è raggiungibile')
	
	
	def _ap__assert_optional(self, config_read: Dict[str, Any]):
		return
	
	
	def _ap__assert_purperrors(self, config_read: Dict[str, Any]):
		return


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


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