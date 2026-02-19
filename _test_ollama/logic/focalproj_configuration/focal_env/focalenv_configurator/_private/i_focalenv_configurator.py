from abc import ABC, abstractmethod

# ============== Docker SDK Utilities =============== #
from docker.models.images import Image as DockerImage
# =================================================== #

from .e_imgbuilt_option import EImageBuiltOption



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
			Imposta una nuova versione di default dell' interprete Python da utilizzare in caso
			il file contenente la versione specifica dell' interprete, per il progetto
			focale corrente, non esista

			Parameters
			----------
				python_version: str
					Una stringa contenente la versione dell' interprete Python da utilizzare come
					default.
					Il formato della versione è il seguente: `<maj>.<min>.<patch>` oppure `<maj>.<min>`

			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `python_version` ha valore `None`
						- Il parametro `python_version` è una stringa vuota
						- Il parametro `python_version` non è nel formato specificato
		"""
		pass
	
	
	@abstractmethod
	def set_focal_project(self, full_root: str, focal_root: str, tests_root: str):
		"""
			Imposta i dati di contesto di un nuovo progetto focale

			Parameters
			----------
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
					Se non è stata impostata alcuna versione di default dell' interprete Python da utilizzare
					prima di chiamare quest' operazione
		"""
		pass
	
	
	@abstractmethod
	def build_image(
			self,
			post_steps: EImageBuiltOption = EImageBuiltOption.DOCKIGNORE
	) -> DockerImage:
		"""
			Crea un' immagine docker, corrispondente all' ambiente focale, dell' ultimo progetto impostato
			che verrà utilizzata per istanziare il container che è l' ambiente effettivo
			
			Nell' ambiente focale:
				- Vengono installati i seguenti software:
				
					- `curl` in versione latest
					- `git` in versione latest
					- `pyenv` in versione latest
					- `python` con versione in base a come è scelta (dal progetto focale, o fallback sulla versione di default impostata in questo configuratore)
					- `pylint` con versione in base a come è scelta (dal progetto focale, o fallback sulla versione di default specificata dai discendenti)
					- `coverage.py` con versione in base a come è scelta (dal progetto focale, o fallback sulla versione di default specificata dai discendenti)
			
				- Vengono definite le seguenti variabili d'ambiente:
					
					- `PYTHON_VERSION`: La versione dell' interprete Python che è stata installata
					- `PYENV_ROOT`: La root path che contiene il software `pyenv` per l' installazione dell' interprete Python specifico
					- `FULL_ROOT`: La Full Project Root Path all' interno dell' ambiente focale
					- `FOCAL_ROOT`: La Focal Project Root Path all' interno dell' ambiente focale
					- `TESTS_ROOT`: La Tests Project Root Path all' interno dell' ambiente focale
					- `GENTESTS_ROOT`: La Gen-tests Project Root Path all' interno dell' ambiente focale
					- `LINTTOOLS_DIR`: Il nome della cartella con i tools per la verifica di linting
					- `CONTTOOLS_ROOT`: La root path che contiene i tools per operazioni da eseguire all' interno dell' ambiente focale
					
				- Vengono installate tutte le dipendenze del progetto focale, siano esse Python o non-Python,
				  specificate tramite i files nella sua Env-config Project Root Path

			Parameters
			----------
				post_steps: EImageBuiltOption
					Opzionale. Default = `DOCKIGNORE`. Un valore `EImageBuiltOption` che indica cosa fare
					dopo aver costruito l' immagine dell' ambiente focale

			Returns
			-------
				DockerImage
					Un oggetto `docker.models.images.Image` che rappresenta l' immagine docker da utilizzare per
					istanziare il container con l' ambiente configurato per il progetto focale impostato

			Raises
			------
				BaseImageNotSetError
					Se non è stata impostata alcuna immagine base per il costruttore di dockerfiles
					alla chiamata di questa operazione
			
				FocalProjectNotSetError
					Se non è impostato nessun progetto focale prima di chiamare quest' operazione

				DefaultPythonVersionNotSetError
					Se non è stata impostata alcuna versione di default dell' interprete Python da utilizzare
					prima di chiamare quest' operazione
		"""
		pass