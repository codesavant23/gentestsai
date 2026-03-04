from abc import ABC, abstractmethod

# ============== Docker SDK Utilities =============== #
from docker.models.images import Image as DockerImage
# =================================================== #

from .e_dockign_option import EDockignoreOption



class IFocalEnvConfigurator(ABC):
	"""
		Rappresenta un oggetto in grado di configurare un ambiente per l' esecuzione/test di un
		progetto focale.
		
		Ogni ambiente focale è principalmente utilizzato per:
		
			- Verifica della correttezza, a livello di linting, delle test-suites parziali dello specifico progetto focale a cui è legata l' immagine
			- Calcolo della coverage di entrambi gli insiemi di test-suites (umane e dei LLMs)
		
		La versione di `pylint` installata è specificata dai discendenti di questa classe astratta.
		La versione di `coverage.py` installata è specificata dai discendenti di questa classe astratta.
	"""
	
	
	@abstractmethod
	def set_default_pyversion(self, python_version: str):
		"""
			Imposta un nuovo tag per l' immagine "python" da utilizzare in caso il file
			contenente la versione specifica dell' interprete, per il progetto focale corrente,
			non esista

			Parameters
			----------
				python_version: str
					Una stringa contenente il tag dell' immagine "python" da utilizzare come fallback
					per la configurazione degli ambienti focali.
					Viene verificato che contenga una versione del seguente formato:
					`<maj>.<min>.<patch>` oppure `<maj>.<min>`.

			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `python_version` ha valore `None`
						- Il parametro `python_version` è una stringa vuota
						- Il parametro `python_version` non contiene una versione nel formato specificato
		"""
		pass
	
	
	@abstractmethod
	def set_focal_project(
			self,
			proj_name: str,
			full_root: str,
			focal_root: str,
			tests_root: str
	):
		"""
			Imposta i dati di contesto di un nuovo progetto focale

			Parameters
			----------
				proj_name: str
					Una stringa contenente il nome del nuovo progetto focale
			
				full_root: str
					Una stringa contenente la Full Project Root Path del nuovo progetto focale

				focal_root: str
					Una stringa contenente la Focal Project Root Path del nuovo progetto focale

				tests_root: str
					Una stringa contenente la Tests Project Root Path del nuovo progetto focale
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `proj_name` ha valore `None` o è una stringa vuota
						- Il parametro `full_root` ha valore `None` o è una stringa vuota
						- Il parametro `focal_root` ha valore `None` o è una stringa vuota
						- Il parametro `tests_root` ha valore `None` o è una stringa vuota
		"""
		pass
	
	
	@abstractmethod
	def set_path_prefix(self, path_prefix: str):
		"""
			Imposta un nuovo path prefix (path di base) da utilizzarsi come Full Project Root Path, nel container
			docker, che verrà istanziato in seguito, combinandolo con la Full Project Directory del progetto focale
			attualmente impostato

			Parameters
			----------
				path_prefix: str
					Una stringa contenente il nuovo path prefix da anteporre alla Full Project Directory del
					progetto focale scelto per costruire la Full Project Root Path all' interno del container

			Raises
			------
				ValueError
					Se il path prefix fornito non è in formato Linux
			
				FocalProjectNotSetError
					Se non è impostato un progetto focale prima di chiamare quest' operazione

				DefaultPythonVersionNotSetError
					Se non è stato impostato alcun tag di default per l' immagine "python"
					prima di chiamare quest' operazione
		"""
		pass
	
	
	@abstractmethod
	def build_image(
			self,
			wants_dockign: bool = True
	) -> DockerImage:
		"""
			Crea un' immagine docker, corrispondente all' ambiente focale, dell' ultimo progetto impostato
			che verrà utilizzata per istanziare il container che è l' ambiente effettivo.
			
			L' immagine docker creata ha come tag la seguente stringa:
				"<tag_prefix>_<project_name>:latest"
				
			dove `<tag_prefix>` è il prefisso scelto da apporre al tag e `<project_name>` è il nome del progetto
			focale di cui si sta creando l' immagine
			
			Nell' ambiente focale:
				- Vengono installati i seguenti software:
				
					- `curl` in versione latest
					- `git` in versione latest
					- `python` con versione in base a come è scelta (dal progetto focale, o fallback sul tag di default impostato in questo configuratore)
					- `pylint` con versione in base a come è scelta (dal progetto focale, o fallback sulla versione di default specificata dai discendenti)
					- `coverage.py` con versione in base a come è scelta (dal progetto focale, o fallback sulla versione di default specificata dai discendenti)
			
				- Vengono definite le seguenti variabili d'ambiente:
					
					- `PYTHON_VERSION`: La versione dell' interprete Python presente nell' ambiente focale
					- `FULL_ROOT`: La Full Project Root Path all' interno dell' ambiente focale
					- `FOCAL_ROOT`: La Focal Project Root Path all' interno dell' ambiente focale
					- `TESTS_ROOT`: La Tests Project Root Path all' interno dell' ambiente focale
					- `GENTESTS_ROOT`: La Gen-tests Project Root Path all' interno dell' ambiente focale
					- `LINTTOOLS_DIR`: Il nome della cartella con i tools per la verifica di linting
					
				- Vengono installate tutte le dipendenze del progetto focale, siano esse Python o non-Python,
				  specificate tramite i files nella sua Env-config Project Root Path

			Parameters
			----------
				wants_dockign: bool
					Opzionale. Default = `True`. Un booleano che indica se scrivere un file
					".dockerignore" prima della costruzione dell' immagine dell' ambiente focale.
					Se il progetto focale impostato ha già un eventuale ".dockerignore", esso verrà
					preservato e risostituito alla fine cancellando il ".dockerignore" scritto da questa
					operazione

			Returns
			-------
				DockerImage
					Un oggetto `docker.models.images.Image` che rappresenta l' immagine docker da utilizzare per
					istanziare il container con l' ambiente configurato per il progetto focale impostato

			Raises
			------
				FocalProjectNotSetError
					Se non è impostato nessun progetto focale prima di chiamare quest' operazione

				DefaultPythonVersionNotSetError
					Se non è stato impostato alcun tag di default per l' immagine "python"
					prima di chiamare quest' operazione
		"""
		pass