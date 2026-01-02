from typing import List, Dict, Set, Any
from ..import AJsonConfigReader

# ============ Path Utilities ============ #
from pathlib import Path as SystemPath
# ======================================== #

from ..exceptions import WrongConfigFileFormatError, FieldDoesntExistsError



class ProjectsJsonConfigReader(AJsonConfigReader):
	"""
		Rappresenta un `AJsonConfigReader` per il file di configurazione dei progetti focali di cui
		verranno generati i tests.
		
		Il file di configurazione letto sarà composto da un dizionario contenente:
			- Un dizionario Python per ogni progetto focale letto con gli stessi campi come letti nel file di configurazione
	"""
	
	_REQ_FIELDS: Set[str] = {"focal_root", "tests_root"}
	
	def __init__(
			self,
			file_path: str
	):
		"""
			Costruisce un nuovo ProjectsJsonConfigReader leggendo il file di configurazione alla path
			specificata.
			
			Il formato del file deve essere un dizionario JSON composto nel seguente modo::
			
				{
					"<project_1>": {
						"focal_root": "<focal_proj1_root_path>",
						"tests_root": "<tests_proj1_root_path>",
						(optional) "focal_excluded": [
							"<path_excluded_in_focal_root_1>",
							"<path_excluded_in_focal_root_2>",
							...
						]
					},
					...
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
	
	
	def _ap__assert_fields(
			self,
			config_read: Dict[str, Any]
	):
		config_fields: Set[str]
		extra_fields: Set[str]
		
		focal_root: str
		tests_root: str
		focal_excl: List[str]
		
		for proj_name, project in config_read.items():
			config_fields = set(project.keys())
			
			if self._REQ_FIELDS > config_fields:
				raise FieldDoesntExistsError()
			
			extra_fields = (
				config_fields.difference(self._REQ_FIELDS).union(
				self._REQ_FIELDS.difference(config_fields))
			)
			if extra_fields != {"focal_excluded"}:
				raise WrongConfigFileFormatError()
			
			focal_root = project["focal_root"]
			tests_root = project["tests_root"]
			focal_excl = project.get("focal_excluded", None)
			
			self._assert_path(focal_root)
			self._assert_path(tests_root)
			if focal_excl is not None:
				self._assert_focal_excl(focal_excl)
	
	
	def _ap__format_result(
			self,
			config_read: Dict[str, Any]
	) -> Dict[str, Any]:
		return config_read
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	@classmethod
	def _assert_path(
			cls,
			path: str
	):
		"""
			Verifica che la path fornita sia corretta sintatticamente ed esista
			nel sistema operativo.
			
			Se la verifica ha successo quest' operazione è equivalente ad una no-op
			
			Parameters
			----------
				path: str
					Una stringa contenente la path di cui verificare la correttezza sintattica
					ed esistenza nel sistema operativo
			
			Raises
			------
				WrongConfigFileFormatError
					Si verifica se:
					
						- La path non è sintatticamente valida
						- La path fornita non esiste
						
		"""
		prompts_path: SystemPath
		try:
			prompts_path = SystemPath(path)
			prompts_path.stat()
		except FileNotFoundError:
			raise WrongConfigFileFormatError()
		except PermissionError:
			pass
		except OSError:
			raise WrongConfigFileFormatError()
		
		
	@classmethod
	def _assert_focal_excl(
			cls,
			focal_excl: List[str]
	):
		"""
			Verifica la correttezza del campo "focal_excluded".
			
			Se la verifica ha successo quest' operazione è equivalente ad una no-op
			
			Parameters
			----------
				focal_excl: List[str]
					Una lista di stringhe contenente il valore del campo "focal_excluded"
			
			Raises
			------
				WrongConfigFileFormatError
					Si verifica se almeno una delle paths di "focal_excluded" è invalida
		"""
		for path in focal_excl:
			cls._assert_path(path)