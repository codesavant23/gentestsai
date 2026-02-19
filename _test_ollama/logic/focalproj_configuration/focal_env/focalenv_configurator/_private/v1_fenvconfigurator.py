from typing import Tuple
from ._a_base_fenvconfigurator import _ABaseFocalEnvConfigurator

from ....dockerfile_builder import ATransactDockfBuilder



class V1FocalEnvConfigurator(_ABaseFocalEnvConfigurator):
	"""
		Rappresenta un `IFocalEnvConfigurator` che crea immagini di ambienti focali
		con installato `pylint=="4.0.4"` e `coverage.py=="7.10.4"`
	"""
	
	def __init__(
			self,
			dockf_builder: ATransactDockfBuilder,
			gentests_dir: str,
			envconfig_dir: str,
			dockerfile_fname: str,
			py_vers_fname: str,
			deps_files: Tuple[str, str, str, str],
			tools_root: str,
			linttools_dir: str,
			conttools_root: str = None,
			path_prefix: str = None
	):
		"""
			Costruisce un nuovo V1FocalEnvConfigurator associandolo:
				
				- All' `ATransactDockfBuilder` da utilizzare per costruire il dockerfile dell' immagine
				- Alla struttura della Env-Config Project Root Path
				- Al nome assegnato alla directory della Gen-tests Project Root Path
				
			E' necessario, dopo ciò, eseguire:
			
				- L' operazione `.set_focal_project(...)`
				- L' operazione `.set_default_pyversion(...)`
				
			Parameters
			----------
				dockf_builder: ATransactDockfBuilder
					Un oggetto `ATransactDockfBuilder` rappresentante il costruttore di dockerfiles
					da utilizzare per generare le immagini degli ambienti focali
					
				gentests_dir: str
					Una stringa contenente il nome della directory che contiene i tests generati
					dai LLMs
					
				envconfig_dir: str
					Una stringa contenente il nome della directory della Env-Config Project Root Path
					di ogni progetto focale
				
				dockerfile_fname: str
					Una stringa contenente il nome del dockerfile che verrà generato per ogni immagine
					di ambiente focale
					
				py_vers_fname: str
					Una stringa contenente il nome dell' eventuale file che contiene la versione specifica
					dell' interprete Python da utilizzare nell' ambiente focale
					
				deps_files: Tuple[str, str, str, str]
					Una 4-tupla di stringhe contenente:
						
						- [0]: Il nome dell' eventuale file che specifica le dipendenze Python del progetto focale
						- [1]: Il nome dell' eventuale file che specifica le dipendenze non-Python del progetto focale
						- [2]: Il nome dell' eventuale script che contiene il codice shell da eseguire prima l' installazione delle dipendenze esterne
						- [3]: Il nome dell' eventuale script che contiene il codice shell da eseguire dopo l' installazione delle dipendenze esterne
			
				tools_root: str
					Una stringa rappresentante la path che contiene i tools da utilizzare all' interno
					dell' ambiente focale
					
				linttools_dir: str
					Una stringa contenente il nome della directory, all' interno di `tools_root`,
					che contiene i tools per effettuare la verifica di linting
					
				conttools_root: str
					Opzionale. Default = `self.CONTTOOLS_ROOT`. Una stringa rappresentante la path, relativa
					all' ambiente focale, che contiene i tools da utilizzare all' interno di esso
					
				path_prefix: str
					Opzionale. Default = `None`. Una stringa rappresentante l' eventuale primo path prefix
					da utilizzare per le immagini prodotte con questo IFocalEnvConfigurator
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `dockf_builder` ha valore `None`
						- Il parametro `gentests_dir` ha valore `None` o è una stringa vuota
						- Il parametro `envconfig_dir` ha valore `None` o è una stringa vuota
						- Il parametro `dockerfile_fname` ha valore `None` o è una stringa vuota
						- Il parametro `py_vers_fname` ha valore `None` o è una stringa vuota
						- Il parametro `deps_files` ha valore `None`, è una tupla vuota; oppure uno dei suoi elementi è `None` o almeno uno è una stringa vuota
						- Il parametro `tools_root` ha valore `None, è una stringa vuota, oppure è una path invalida
						- Il parametro `linttools_dir` ha valore `None`, è una stringa vuota, oppure non esiste quella directory in `tools_root`
						- Il parametro `conttools_root` è una stringa vuota, oppure è una path Linux invalida
		"""
		super().__init__(
			dockf_builder,
			gentests_dir, envconfig_dir, dockerfile_fname, py_vers_fname, deps_files,
			tools_root, linttools_dir, conttools_root
		)
	
	
	def _ap__pylint_version(self) -> str:
		return "4.0.4"
	
	
	def _ap__covpy_version(self) -> str:
		return "7.10.4"
	

	##	============================================================
	##						PRIVATE METHODS
	##	============================================================