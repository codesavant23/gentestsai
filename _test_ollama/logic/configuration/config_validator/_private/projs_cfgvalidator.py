from typing import List, Dict, Set, Any, Tuple
from ._a_base_cfgvalidator import _ABaseConfigValidator

# ============ Path Utilities ============ #
from pathlib import Path as SystemPath
# ======================================== #

from ..exceptions import (
	FieldDoesntExistsError,
	WrongConfigFileFormatError,
	InvalidConfigValueError
)



class ProjectsJsonConfigReader(_ABaseConfigValidator):
	"""
		Rappresenta un `IConfigValidator` per il file di configurazione dei progetti focali di cui
		verranno generati i tests.
		
		Il file di configurazione letto è un dizionario contenente:
		
			-   Un entry dizionario per ogni progetto focale la cui chiave è il nome del progetto.
				Il dizionario contiene, obbligatoriamente:
				
					* "focal_root" (str): La Focal Project Root Path del progetto
					* "tests_root" (str): Se esiste nel file letto, il nome del file che contiene la cache legata al processo di "Generazione"
					
				e può contenere, opzionalmente:
					
					* "focal_excluded" (List[str]): Una lista di paths, derivanti dalla Focal Project Root Path, da non considerare come parte del codice focale
	"""
	
	_REQ_FIELDS: Set[str] = {"focal_root", "tests_root"}
	_OPT_FIELDS: Set[str] = {"focal_excluded"}
	
	def __init__(
			self,
			config_dict: Dict[str, Any]
	):
		"""
			Costruisce un nuovo ProjectsJsonConfigReader leggendo il file di configurazione alla path
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
	
	
	def _p__efields_strict(self) -> bool:
		return False
	
	
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		return (set(), set())
	
	
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		focal_root: str
		tests_root: str
		focal_excl: List[str]
		
		for proj_name, project in config_read.items():
			config_fields = set(project.keys())
			
			if config_fields < self._REQ_FIELDS:
				raise FieldDoesntExistsError()
			
			focal_root = project["focal_root"]
			tests_root = project["tests_root"]
			
			self._assert_path(focal_root, proj_name, "focal_root")
			self._assert_path(tests_root, proj_name, "tests_root")

	
	def _ap__assert_optional(self, config_read: Dict[str, Any]):
		for proj_name, project in config_read.items():
			config_fields = set(project.keys())
			
			extra_fields = (
				config_fields.difference(self._REQ_FIELDS).union(
				self._REQ_FIELDS.difference(config_fields))
			)
			if extra_fields != self._OPT_FIELDS:
				raise WrongConfigFileFormatError()
			
			focal_excl = project.get("focal_excluded", None)
			if focal_excl is not None:
				self._assert_focal_excl(focal_excl, proj_name)
				
				
	def _ap__assert_purperrors(self, config_read: Dict[str, Any]):
		return
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	@classmethod
	def _assert_path(
			cls,
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
				WrongConfigFileFormatError
					Si verifica se:
					
						- La path non è sintatticamente valida
						- La path fornita non esiste
		"""
		path: SystemPath
		try:
			path = SystemPath(path_totest)
			path.stat()
		except NotADirectoryError:
			raise InvalidConfigValueError(f'La path specificata dal parametro "{param}" è invalida (progetto "{proj_name}")')
		except FileNotFoundError:
			raise InvalidConfigValueError(f'La path specificata dal parametro "{param}" non esiste (progetto "{proj_name}")')
		except PermissionError:
			raise InvalidConfigValueError(f'Non si può accedere alla path specificata dal parametro "{param}" (progetto "{proj_name}")')
		except OSError:
			raise InvalidConfigValueError(f'La path specificata dal parametro "{param}" non è raggiungibile (progetto "{proj_name}")')


	@classmethod
	def _assert_focal_excl(
			cls,
			focal_excl: List[str],
			proj_name: str
	):
		"""
			Verifica la correttezza del campo "focal_excluded".
			
			Se la verifica ha successo quest' operazione è equivalente ad una no-op
			
			Parameters
			----------
				focal_excl: List[str]
					Una lista di stringhe contenente il valore del campo "focal_excluded"
					
				proj_name: str
					Una stringa contenente il nome del progetto di cui verificare il campo "focal_excluded"
			
			Raises
			------
				InvalidConfigValueError
					Si verifica se almeno una delle paths di "focal_excluded" è invalida
		"""
		for path in focal_excl:
			cls._assert_path(path, proj_name, "focal_excluded")