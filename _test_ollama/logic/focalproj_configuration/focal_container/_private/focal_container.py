from typing import Tuple

# ============== OS Utilities ============== #
# ============== OS Utilities ============== #
from os import (
	makedirs as os_mkdirs,
	environ as os_getenv
)
from shutil import rmtree as os_dremove
from os.path import exists as os_fdexists
# ========================================== #
# ============ Path Utilities ============ #
from os.path import (
	sep as path_sep,
	altsep as path_altsep,
	join as path_join
)
_PATH_SEPS: str = f"{path_sep}{path_altsep if path_altsep is not None else ''}"
# ======================================== #
# ============ Docker SDK Utilities ============ #
from docker import (
	from_env as docker_getclient,
	DockerClient
)
from docker.models.images import Image as DockerImage
from docker.models.containers import (
	Container as DockerContainer,
	ExecResult as DockerContainerExecResult
)
# ============================================== #

from ..exceptions import (
	ContainerNotRunningError,
	ContainerAlreadyRunningError,
	CommandNeverExecutedError
)



class FocalContainer:
	"""
		Rappresenta un oggetto capace di gestire un container docker legato ad uno specifico progetto focale.
		Ogni container docker è costruito sulla base di un' immagine docker pre-configurata per ospitare il
		progetto focale a cui è legata.
		
		In particolare l' utilizzo del container è finalizzato ai seguenti scopi:
		
			- Verifica della correttezza, a livello di linting, delle test-suites parziali generate
			- Calcolo della coverage di entrambi gli insiemi di test-suites (umane e dei LLMs)
	"""

	def __init__(
			self,
			docker_image: DockerImage,
			full_root: str,
			path_prefix: str,
			shared_dirname: str = "gtsai__shared",
			results_dirname: str = "gtsai__results",
			stop_timeout: int=100
	):
		"""
			Costruisce un nuovo FocalContainer basandolo sull' immagine docker, pre-configurata,
			da cui verrà istanziato il container docker

			Parameters
			----------
				docker_image: DockerImage
					Un oggetto `docker.models.images.Image` che rappresenta l'immagine docker pre-configurata
					su cui verrà basato il container docker gestito
					
				full_root: str
					Una stringa contenente la Full Project Root Path del progetto focale di cui verrà
					gestito il container docker

				path_prefix: str
					Una stringa contenente il path prefix, stabilito alla costruzione dell' immagine, che
					rappresenta la Full Project Root Path all' interno del container docker gestito

				shared_dirname: str
					Opzionale. Default = `"gtsai__shared"`. Una stringa rappresentante il nome della directory-volume,
					all' interno del `path_prefix`, che conterrà i files da esporre all' ambiente focale
					successivamente  alla sua creazione.
					Si presuppone l' esistenza di questa path nel sistema operativo che hosta il
					gestore degli ambienti focali, all' interno di `full_root`.
					
				results_dirname: str
					Opzionale. Default = `"gtsai__results"`. Una stringa rappresentante il nome della directory-volume,
					all' interno del `path_prefix`, che conterrà i files prodotti dall' ambiente focale come risultato
	
				stop_timeout: int
					Opzionale. Default = `100`. Un intero che indica il valore di timeout (in millisecondi)
					per lo stop del container docker, gestito da questo FocalContainer
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `docker_image` ha valore `None`
						- Il parametro `full_root` ha valore `None` o è una stringa vuota
						- Il parametro `path_prefix` ha valore `None` o è una stringa vuota
						- Il parametro `shared_dirname` ha valore `None` o è una stringa vuota
						- Il parametro `shared_dirname` rappresenta una path che non esiste in `full_root`
						- Il parametro `results_dirname` ha valore `None` o è una stringa vuota
						- Il parametro `stop_timeout` è minore di 1
		"""
		if (
			(docker_image is None) or
			(full_root is None) or (full_root == "") or
			(path_prefix is None) or (path_prefix == "") or
			(stop_timeout < 1)
		):
			raise ValueError()
		if not os_fdexists(path_join(full_root, shared_dirname)):
			raise ValueError()
		
		self._docker: DockerClient = None
		try:
			docker_host: str = os_getenv["DOCKER_HOST"]
			self._docker = DockerClient(base_url=docker_host)
		except KeyError:
			self._docker = docker_getclient()

		self._image = docker_image
		self._full_root: str = full_root.rstrip(_PATH_SEPS)

		self._path_prefix: str = path_prefix
		
		self._shared_dir: str = shared_dirname
		self._results_dir: str = results_dirname

		self._timeout: float = stop_timeout

		self._environ: DockerContainer = None
		self._running: bool = False
		
		self._cmd_ever_execd: bool = False
		self._lexec_exitcode: int = -1
		self._lexec_stdout: str = None
		self._lexec_stderr: str = None


	def start_container(self):
		"""
			Avvia il container docker basato sull' immagine associata a questo FocalContainer.
			Se il container docker, gestito da questo FocalContainer, è già in esecuzione allora esso deve
			essere prima terminato per essere ri-avviato.

			Raises
			------
				ContainerAlreadyRunningError
					Se è già in esecuzione il container docker, gestito da questo FocalContainer, alla
					chiamata di quest' operazione
		"""
		if self._running:
			raise ContainerAlreadyRunningError()
		
		shared_path: str = path_join(self._full_root, self._shared_dir)
		results_path: str = path_join(self._full_root, self._results_dir)
		
		os_dremove(results_path, ignore_errors=True)
		os_mkdirs(results_path)

		self._environ = self._docker.containers.run(
			image=self._image,
			detach=True,
			volumes={
				shared_path: {
					"bind": f"{self._path_prefix}/{self._shared_dir}",
					"mode": "rw"
				},
				results_path: {
					"bind": f"{self._path_prefix}/{self._results_dir}",
					"mode": "rw"
				}
			}
		)

		self._running = True


	def execute(
			self,
			command: str,
			privileged: bool = False
	):
		"""
			Esegue il comando shell dato come argomento nel container docker gestito da questo FocalContainer;
			e ne memorizza lo standard output, lo standard error e l' exit-code risultanti

			Parameters
			----------
				command: str
					Una stringa contenente il comando shell da eseguire all' interno del container
					docker in esecuzione gestito da questo FocalContainer

				privileged: bool
					Opzionale. Default = `False`. Un booleano che specifica se è necessario eseguire il
					comando con priviligi

			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `command` ha valore None
						- Il parametro `command` è una stringa vuota
			
				ContainerNotRunningError
					Se non è in esecuzione il container docker, gestito da questo FocalContainer, alla
					chiamata di quest' operazione
		"""
		result: DockerContainerExecResult = self._environ.exec_run(
			command,
			privileged=privileged,
			demux=True
		)
		output: Tuple[bytes, bytes] = result.output
		
		self._lexec_exitcode = result.exit_code
		self._lexec_stdout = output[0].decode("utf-8")
		self._lexec_stderr = output[1].decode("utf-8")
		
		if not self._cmd_ever_execd:
			self._cmd_ever_execd = True


	def stop_container(self):
		"""
			Termina l' esecuzione del container docker, gestito da questo FocalContainer

			Raises
			------
				ContainerNotRunningError
					Se non è in esecuzione il container docker, gestito da questo FocalContainer,
					alla chiamata di quest' operazione
		"""
		if not self._running:
			raise ContainerNotRunningError()

		self._environ.stop(timeout=self._timeout)
		self._environ.remove(
			v=True,
			force=True
		)
		self._environ = None

		self._running = False


	def get_last_stdout(self) -> str:
		"""
			Restituisce lo standard output relativo all' ultimo comando eseguito all' interno
			dell' ultimo container
			
			Raises
			------
				CommandNeverExecutedError
					Se non è mai stato eseguito nessun comando shell prima di chiamare quest' operazione
		"""
		if self._cmd_ever_execd:
			raise CommandNeverExecutedError()
		return self._lexec_stdout


	def get_last_stderr(self) -> str:
		"""
			Restituisce lo standard error relativo all' ultimo comando eseguito all' interno
			dell' ultimo container
			
			Raises
			------
				CommandNeverExecutedError
					Se non è mai stato eseguito nessun comando shell prima di chiamare quest' operazione
		"""
		if self._cmd_ever_execd:
			raise CommandNeverExecutedError()
		return self._lexec_stderr


	def get_last_exitcode(self) -> int:
		"""
			Restituisce l' exit-code relativo all' ultimo comando eseguito all' interno
			dell' ultimo container
			
			Raises
			------
				CommandNeverExecutedError
					Se non è mai stato eseguito nessun comando shell prima di chiamare quest' operazione
		"""
		if self._cmd_ever_execd:
			raise CommandNeverExecutedError()
		return self._lexec_exitcode