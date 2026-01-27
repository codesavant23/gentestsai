from typing import List, Tuple
from abc import abstractmethod
from .. import (
	IFocalEnvConfigurator,
	EImageBuiltOption
)

# ============== Docker SDK Utilities =============== #
from docker import (
	from_env as docker_getclient,
	DockerClient
)
from docker.models.images import Image as DockerImage
# =================================================== #
# ============ RegEx Utilities ============ #
from regex import (
	search as reg_search,
	Match,
)
# ========================================= #
# ============ OS Utilities ============ #
from os.path import exists as os_fdexists
from os import remove as os_remove
# ====================================== #
# ============ Path Utilities ============ #
from os.path import (
	join as path_join,
	split as path_split,
	relpath as path_relative
)
from pathlib import PosixPath
# ======================================== #

from ....dockerfile_builder import ATransactDockfBuilder

from ....exceptions import (
	FocalProjectNotSetError,
	DefaultPythonVersionNotSetError
)



class _ABaseFocalEnvConfigurator(IFocalEnvConfigurator):
	"""
		Rappresenta un `IFocalEnvConfigurator` di base, ovvero che contiene la logica
		comune ad ogni `IFocalEnvConfigurator`.
		
		Attributi di Classe Pubblici:
			- `PATH_PREFIX` (str) : Prefisso, di default, del percorso, interno al container docker, a cui verrà collegato il contenuto del progetto focale per renderlo accessibile al suo interno.
		
		La versione di `pylint` installata è specificata dai discendenti di questa classe astratta.
		La versione di `coverage.py` installata è specificata dai discendenti di questa classe astratta.
		Il pacchetto di software aggiuntivi installati, indipendenti dal progetto focale, è specificato
		dai discendenti di questa classe astratta
	"""
	
	_PYVERS_PATT: str = r"^[0-9]+\.[0-9]+(\.[0-9]+)?$"
	_LINUXPATH_PATT: str = r"^(?P<path_prefix>(/[\w.-]+/?)+)$"
	PATH_PREFIX: str = "/app"
	CONTTOOLS_ROOT: str = "/etc/container"
	
	def __init__(
			self,
			dockf_builder: ATransactDockfBuilder,
			gentests_dir: str,
			envconfig_dir: str,
			dockerfile_fname: str,
			python_vers_fname: str,
			deps_files: Tuple[str, str, str, str],
			tools_root: str,
			linttools_dir: str,
			conttools_path: str = None
	):
		"""
			Costruisce un nuovo _ABaseFocalEnvConfigurator associandolo:
				
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
					
				python_vers_fname: str
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
					
				conttools_path: str
					Opzionale. Default = `self.CONTTOOLS_ROOT`. Una stringa rappresentante la path, relativa
					all' ambiente focale, che contiene i tools da utilizzare all' interno di esso
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `dockf_builder` ha valore `None`
						- Il parametro `gentests_dir` ha valore `None` o è una stringa vuota
						- Il parametro `envconfig_dir` ha valore `None` o è una stringa vuota
						- Il parametro `dockerfile_fname` ha valore `None` o è una stringa vuota
						- Il parametro `python_vers_fname` ha valore `None` o è una stringa vuota
						- Il parametro `deps_files` ha valore `None`, è una tupla vuota; oppure uno dei suoi elementi è `None` o almeno uno è una stringa vuota
						- Il parametro `tools_root` ha valore `None, è una stringa vuota, oppure è una path invalida
						- Il parametro `linttools_dir` ha valore `None`, è una stringa vuota, oppure non esiste quella directory in `tools_root`
						- Il parametro `conttools_path` è una stringa vuota, oppure è una path Linux invalida
		"""
		self._check_initargs(
			dockf_builder,
			gentests_dir, envconfig_dir, dockerfile_fname, python_vers_fname, deps_files,
			tools_root, linttools_dir, conttools_path
		)
		
		self._project_set: bool = False
		self._def_pyvers_set: bool = False

		self._docker: DockerClient = docker_getclient()
		self._dockf_builder: ATransactDockfBuilder = dockf_builder
		self._dockf_fname: str = dockerfile_fname

		self._envconfig_dir: str = envconfig_dir
		self._gentests_dir: str = gentests_dir

		self._path_prefix: str = self.PATH_PREFIX

		# La Full Project Root Path reale
		self._orig_full_root: str = None
		# La Full Project Root Path all' interno del container
		self._full_root: str = None
		# La Focal Project Root Path all' interno del container
		self._focal_root: str = None
		# La Tests Project Root Path all' interno del container
		self._tests_root: str = None
		# La Env-config Project Root Path reale
		self._orig_envconfig_root: str = None
		# La Env-config Project Root Path all' interno del container
		self._envconfig_root: str = None
		# La Gen-tests Project Root Path all' interno del container
		self._gentests_root: str = None

		# File con Versione dell' Interprete Python
		self._py_vers_fname: str = python_vers_fname
		self._py_vers_path: str = None

		# File con lista di Dipendenze Esterne
		self._ext_deps_fname: str = deps_files[1]
		self._ext_deps_path: str = None

		# File ("requirements.txt"-like) con lista di Dipendenze Python
		self._py_deps_fname: str = deps_files[0]
		self._py_deps_path: str = None

		# Files Script Precedente e Successivo all' installazione delle Dipendenze Esterne
		self._prescr_fname: str = deps_files[2]
		self._prescr_path: str = None
		self._postscr_fname: str = deps_files[3]
		self._postscr_path: str = None
		
		# Path dei tools dell' ambiente reale
		self._tools_root: str = tools_root
		# Directory dei tools per la verifica di linting
		self._linttools_dir: str = linttools_dir
		
		# Path dei tools dell' ambiente all' interno del container
		self._conttools_root: str = self.CONTTOOLS_ROOT
		if conttools_path is not None:
			self._conttools_root = conttools_path
			
		self._linttools_dir: str = linttools_dir
	
	
	def set_default_pyversion(self, python_version: str):
		vers_found: Match[str] = reg_search(self._PYVERS_PATT, python_version)
		if vers_found is None:
			raise ValueError()
		
		self._def_pyvers = python_version
		self._def_pyvers_set = True
	
	
	def set_focal_project(self, full_root: str, focal_root: str, tests_root: str):
		full_dir: str = path_split(full_root)[1]
		focal_dir: str = path_split(focal_root)[1]
		tests_path: str = path_relative(tests_root, start=full_root)

		self._orig_full_root = full_root
		self._full_root: str = f"{self._path_prefix}/{full_dir}"
		self._focal_root: str = f"{self._full_root}/{focal_dir}"
		self._tests_root: str = f"{self._full_root}/{tests_path}"
		self._gentests_root: str = f"{self._full_root}/{self._gentests_dir}"
		self._envconfig_root: str = f"{self._full_root}/{self._envconfig_dir}"

		self._set_envc_entities()

		self._project_set = True
	
	
	def set_path_prefix(self, path_prefix: str):
		self._assert_inited()

		pathpref_found: Match[str] = reg_search(self._LINUXPATH_PATT, path_prefix)
		if pathpref_found.group("path_prefix") is None:
			raise ValueError()

		self._full_root = self._change_prefix_of_path(
			path_prefix,
			self._full_root,
		)
		self._focal_root = self._change_prefix_of_path(
			path_prefix,
			self._focal_root,
		)
		self._tests_root = self._change_prefix_of_path(
			path_prefix,
			self._tests_root,
		)
		self._gentests_root = self._change_prefix_of_path(
			path_prefix,
			self._gentests_root,
		)
		self._envconfig_root = self._change_prefix_of_path(
			path_prefix,
			self._envconfig_root,
		)

		self._change_prefix_envc_entities(path_prefix)

		self._path_prefix = path_prefix.rstrip("/")
	
	
	def build_image(
			self,
			post_steps: EImageBuiltOption = EImageBuiltOption.DOCKIGNORE
	) -> DockerImage:
		self._assert_inited()

		python_version: str = self._get_python_version()
		ext_deps: List[str] = self._get_ext_deps()

		# Impostazione della versione dell' interprete Python che verrà utilizzata
		self._dockf_builder.set_envvar("PYTHON_VERSION", python_version)

		# Installazione di `pyenv`
		self._configure_pyenv()

		# Configurazione delle variabili d'ambiente locali
		self._configure_local_envvars()
		
		# Configurazione dell' installazione delle dipendenze
		self._configure_deps_install(ext_deps)

		# Installazione di `coverage.py`
		self._dockf_builder.add_shellcmd(f'python3 -m pip install coverage=="{self._ap__covpy_version()}"')
		# Installazione di `pylint`
		self._dockf_builder.add_shellcmd(f'python3 -m pip install pylint=="{self._ap__pylint_version()}"')
		
		# TODO: Se necessario implementare i tools per il calcolo della coverage ||
		# Copia dei tools per il linting
		linttools_path: PosixPath = PosixPath(self._tools_root, self._linttools_dir)
		self._dockf_builder.add_copy(
			[str(linttools_path)],
			f"{self._conttools_root}/{self._linttools_dir}/"
		)
		
		# Impostazione della directory corrente sul path prefix
		self._dockf_builder.add_shellcmd(f"mkdir -p {self._path_prefix}")
		self._dockf_builder.add_workdir(self._path_prefix)
		
		dockerfile_path: str = f"{self._orig_full_root}/{self._dockf_fname}"
		self._dockf_builder.build_dockerfile(dockerfile_path)

		proj_image: DockerImage = self._docker.images.build(
			path=self._orig_full_root,
			dockerfile=self._dockf_fname
		)[0]

		match post_steps:
			case EImageBuiltOption.DOCKF_REMOVE:
				os_remove(dockerfile_path)
			case EImageBuiltOption.DOCKIGNORE:
				dockerignore_path: str = f"{self._orig_full_root}/.dockignore"
				with open(dockerignore_path, "w") as fdocki:
					fdocki.writelines(f"./{self._dockf_fname}")
					fdocki.flush()

		return proj_image
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__pylint_version(self) -> str:
		"""
			Restituisce la versione del software `pylint` da installare
			
			Returns
			-------
				str
					Una stringa rappresentante la versione di `pylint` da installare
		"""
		pass
	
	
	@abstractmethod
	def _ap__covpy_version(self) -> str:
		"""
			Restituisce la versione del software `coverage.py` da installare
			
			Returns
			-------
				str
					Una stringa rappresentante la versione di `coverage.py` da installare
		"""
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================
	
	
	def _assert_inited(self):
		"""
			Asserisce che questo _ABaseFocalEnvConfigurator sia stato inizializzato completamente
			impostando:
				- I dati di contesto del progetto focale di cui generare l' immagine docker
				- La versione dell' interprete Python da utilizzare come default

			Raises
			------
				FocalProjectNotSetError
					Se non è impostato un progetto focale prima di chiamare quest' operazione

				DefaultPythonVersionNotSetError
					Se non è stata impostata alcuna versione di default dell' interprete Python da utilizzare
					prima di chiamare quest' operazione
		"""
		if not self._project_set:
			raise FocalProjectNotSetError()
		if not self._def_pyvers_set:
			raise DefaultPythonVersionNotSetError()
	
	
	def _change_prefix_of_path(
			self,
			new_path_prefix: str,
			path_tochange: str
	) -> str:
		"""
			Cambia il path prefix da una path fornita come argomento

			Parameters
			----------
				new_path_prefix: str
					Una stringa contenente il nuovo path prefix con cui modificare la path

				path_tochange: str
					Una stringa contenente la path di cui cambiare il path prefix

			Returns
			-------
				str
					Una stringa contenente la path data con il path prefix aggiornato
		"""
		return path_join(
			new_path_prefix,
			path_relative(path_tochange, start=self._path_prefix)
		)
	
	
	def _change_prefix_envc_entities(
			self,
			new_path_prefix: str,
	):
		"""
			Cambia il path prefix di tutte le paths, relative al container, che corrispondono
			ai files nella Env-Config Project Root Path

			Parameters
			----------
				new_path_prefix: str
					Una stringa contenente il nuovo path prefix con cui modificare le paths
		"""
		if self._py_deps_path != "":
			self._py_deps_path = self._change_prefix_of_path(
				new_path_prefix,
				self._py_deps_path,
			)

		if os_fdexists(self._ext_deps_path):
			if self._prescr_path != "":
				self._py_deps_path = self._change_prefix_of_path(
					new_path_prefix,
					self._py_deps_path,
				)
			if self._postscr_path != "":
				self._postscr_path = self._change_prefix_of_path(
					new_path_prefix,
					self._postscr_path,
				)
	

	def _set_envc_entities(self):
		"""
			Imposta i valori degli attributi privati relativi ai files presenti nella
			Env-config Project Root Path
		"""
		self._orig_envconfig_root = f"{self._orig_full_root}/{self._envconfig_dir}"

		self._py_vers_path = self._set_envc_entity_ifexists(
			self._py_vers_fname
		)
		
		self._py_deps_path = self._set_envc_entity_ifexists(
			self._py_deps_fname
		)
		self._ext_deps_path = self._set_envc_entity_ifexists(
			self._ext_deps_path
		)

		if self._ext_deps_path != "":
			self._prescr_path = self._set_envc_entity_ifexists(
				self._prescr_fname
			)

			self._postscr_path = self._set_envc_entity_ifexists(
				self._postscr_fname
			)
			
			
	def _set_envc_entity_ifexists(
			self,
			entity_fname: str
	) -> str:
		"""
			Imposta il valore di un file della Env-config Project Root Path, da utilizzarsi
			all' interno dell' ambiente focale, se esiste realmente

			Parameters
			----------
				entity_fname: str
					Una stringa contenente il nome del file di cui impostare la path relativamente
					all' ambiente focale

			Returns
			-------
				str
					Una stringa contenente la path relativa al container del file dato
		"""
		orig_entity_path: str = f"{self._orig_envconfig_root}/{entity_fname}"
		if not os_fdexists(f"{orig_entity_path}"):
			return ""
		else:
			return f"{self._envconfig_root}/{entity_fname}"
		
		
	def _get_python_version(self) -> str:
		"""
			Restituisce la versione di Python da utilizzare nell' ambiente focale

			Returns
			-------
				str
					Una stringa contenente la versione dell' interprete Python da utilizzare
					all' interno dell' ambiente focale
		"""
		python_vers: str
		if self._py_vers_path != "":
			with open(self._py_vers_path, "r") as fp:
				python_vers = fp.read().strip("\n\t ")
		else:
			python_vers = self._def_pyvers
		return python_vers


	def _get_ext_deps(self) -> List[str]:
		"""
			Legge le dipendenze esterne dal file, relativamente al progetto focale impostato

			Returns
			-------
				List[str]
					Una lista di stringhe contenente un elemento per ogni dipendenza esterna da installare.
					Ogni dipendenza esterna è identificata dal nome del pacchetto da installare tramite `apt-get install`
		"""
		ext_deps: List[str] = []
		if self._ext_deps_path != "":
			with open(self._ext_deps_path, "r") as fp:
				ext_deps = fp.readlines()
			ext_deps = list(map(lambda x: x.strip("\n\t "), ext_deps))
		return ext_deps


	def _configure_pyenv(self):
		"""
			Configura il costruttore di dockerfiles per l' installazione di `pyenv` nelle immagini
			che verranno prodotte successivamente
		"""
		self._dockf_builder.begin_cmds_tran()
		self._dockf_builder.add_shellcmd_step("apt-get update")
		self._dockf_builder.add_shellcmd_step(
			"apt-get install -y "
			"build-essential curl git zlib1g-dev "
			"libssl-dev libreadline-dev "
			"libffi-dev libbz2-dev libsqlite3-dev"
		)
		self._dockf_builder.add_shellcmd_step("git clone https://github.com/pyenv/pyenv.git ~/.pyenv")
		self._dockf_builder.commit_cmds_tran()


	def _configure_local_envvars(self):
		"""
			Configura il costruttore di dockerfiles per definire le variabili d'ambiente locali nelle
			immagini che verranno prodotte successivamente
		"""
		self._dockf_builder.set_envvar("PYENV_ROOT", "/root/.pyenv")
		self._dockf_builder.set_envvar("PATH", "$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH")
		self._dockf_builder.set_envvar("FULL_ROOT", self._full_root)
		self._dockf_builder.set_envvar("FOCAL_ROOT", self._focal_root)
		self._dockf_builder.set_envvar("TESTS_ROOT", self._tests_root)
		self._dockf_builder.set_envvar("GENTESTS_ROOT", self._gentests_root)
		self._dockf_builder.set_envvar("CONTTOOLS_ROOT", self._conttools_root)
		self._dockf_builder.set_envvar("LINTTOOLS_DIRNAME", self._linttools_dir)


	def _configure_deps_install(
			self,
			ext_deps: List[str],
	):
		"""
			Configura il `DockerfileBuilder` per l' installazione delle dipendenze progettuali
			nelle immagini che verranno prodotte successivamente

			Parameters
			----------
				ext_deps: List[str]
					Una lista di stringhe contenente un elemento per ogni dipendenza esterna da installare.
					Ogni dipendenza esterna è identificata dal nome del pacchetto da installare tramite `apt-get install`
		"""
		self._dockf_builder.begin_cmds_tran()

		# Esecuzione dello script Pre-installazione delle dipendenze esterne
		if os_fdexists(self._ext_deps_path):
			self._dockf_builder.add_shellcmd_step(f"source {self._prescr_path}")

		# Installazione delle dipendenze esterne
		for ext_dep in ext_deps:
			self._dockf_builder.add_shellcmd_step(f"apt-get install -y {ext_dep}")

		# Esecuzione dello script Post-installazione delle dipendenze esterne
		if os_fdexists(self._ext_deps_path):
			self._dockf_builder.add_shellcmd_step(f"source {self._postscr_path}")

		# Installazione delle dipendenze (packages) Python
		self._dockf_builder.add_shellcmd_step(f"pip install -r {self._py_deps_path}")

		self._dockf_builder.commit_cmds_tran()
		
		
	@classmethod
	def _check_initargs(
			cls,
			dockf_builder: ATransactDockfBuilder,
			gentests_dir: str,
			envconfig_dir: str,
			dockerfile_fname: str,
			python_vers_fname: str,
			deps_files: Tuple[str, str, str, str],
			tools_root: str,
			linttools_dir: str,
			conttools_path: str = None
	):
		"""
			Verifica la validità degli argomenti del costruttore forniti.
			
			Se la verifica ha successo quest' operazione è equivalente ad una no-op
			
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `dockf_builder` ha valore `None`
						- Il parametro `gentests_dir` ha valore `None` o è una stringa vuota
						- Il parametro `envconfig_dir` ha valore `None` o è una stringa vuota
						- Il parametro `dockerfile_fname` ha valore `None` o è una stringa vuota
						- Il parametro `python_vers_fname` ha valore `None` o è una stringa vuota
						- Il parametro `deps_files` ha valore `None`, è una tupla vuota; oppure uno dei suoi elementi è `None` o almeno uno è una stringa vuota
						- Il parametro `tools_root` ha valore `None, è una stringa vuota, oppure è una path invalida
						- Il parametro `linttools_dir` ha valore `None`, è una stringa vuota, oppure non esiste quella directory in `tools_root`
						- Il parametro `conttools_path` è una stringa vuota, oppure è una path Linux invalida
		"""
		if (
			(dockf_builder is None) or
			(gentests_dir is None) or
			(envconfig_dir is None) or
			(dockerfile_fname is None) or
			(python_vers_fname is None) or
			(deps_files is None) or
			(tools_root is None) or
			(linttools_dir is None)
		):
			raise ValueError()

		if (
			(gentests_dir == "") or
			(envconfig_dir == "") or
			(dockerfile_fname == "") or
			(python_vers_fname == "") or
			(deps_files == tuple()) or
			(tools_root == "") or
			(conttools_path == "")
		):
			raise ValueError()
		
		for dep_file in deps_files:
			if (
				(dep_file is None) or
				(dep_file == "")
			):
				raise ValueError()