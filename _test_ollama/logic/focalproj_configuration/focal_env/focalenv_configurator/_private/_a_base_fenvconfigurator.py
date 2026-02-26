from typing import List, Tuple, Dict
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
# ============== OS Utilities ============== #
from os import (
	remove as os_remove,
	environ as os_getenv
)
from shutil import rmtree as os_dremove
from os.path import exists as os_fdexists
# ========================================== #
# ============ Path Utilities ============ #
from os.path import (
	join as path_join,
	split as path_split,
	sep, altsep
)
from pathlib import (
	Path as SystemPath,
	PosixPath
)
from shutil import (
	copytree as os_dcopy
)
# ======================================== #
# ============== JSON Utilities ============== #
from json import JSONDecoder
# ============================================ #

from ....dockerfile_builder import ATransactDockfBuilder

from ....exceptions import (
	FocalProjectNotSetError,
	DefaultPythonVersionNotSetError
)


_PATH_SEPS: str = f"{sep}{altsep if altsep is not None else ''}"



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
	
	def __init__(
			self,
			dockf_builder: ATransactDockfBuilder,
			tag_prefix: str,
			gentests_dir: str,
			envconfig_dir: str,
			dockerfile_fname: str,
			py_vers_fname: str,
			deps_files: Tuple[str, str, str, str, str],
			tools_root: str,
			linttools_dir: str,
			covtools_dir: str,
			path_prefix: str = None
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
					
				tag_prefix: str
					Una stringa contenente il prefisso da apporre al tag di ogni immagine
					che verrà costruita
					
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
					
				deps_files: Tuple[str, str, str, str, str]
					Una 5-tupla di stringhe contenente:
						
						- [0]: Il nome dell' eventuale file che specifica le dipendenze Python del progetto focale
						- [1]: Il nome dell' eventuale file che specifica le dipendenze non-Python del progetto focale
						- [2]: Il nome dell' eventuale script che contiene il codice shell da eseguire prima l' installazione delle dipendenze esterne
						- [3]: Il nome dell' eventuale script che contiene il codice shell da eseguire dopo l' installazione delle dipendenze esterne
						- [4]: Il nome dell' eventuale script che contiene il codice shell da eseguire dopo l' installazione delle dipendenze Python
			
				tools_root: str
					Una stringa rappresentante la path che contiene i tools da utilizzare all' interno
					dell' ambiente focale
					
				linttools_dir: str
					Una stringa contenente il nome della directory, all' interno di `tools_root`,
					che contiene i tools per effettuare la verifica di linting
					
				covtools_dir: str
					Una stringa contenente il nome della directory, all' interno di `tools_root`,
					che contiene i tools per effettuare il calcolo della coverage
					
				path_prefix: str
					Opzionale. Default = `None`. Una stringa rappresentante l' eventuale primo path prefix
					da utilizzare per le immagini prodotte con questo IFocalEnvConfigurator
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `dockf_builder` ha valore `None`
						- Il parametro `tag_prefix` ha valore `None` o è una stringa vuota
						- Il parametro `gentests_dir` ha valore `None` o è una stringa vuota
						- Il parametro `envconfig_dir` ha valore `None` o è una stringa vuota
						- Il parametro `dockerfile_fname` ha valore `None` o è una stringa vuota
						- Il parametro `py_vers_fname` ha valore `None` o è una stringa vuota
						- Il parametro `deps_files` ha valore `None`, è una tupla vuota; oppure uno dei suoi elementi è `None` o almeno uno è una stringa vuota
						- Il parametro `tools_root` ha valore `None, è una stringa vuota, oppure è una path invalida
						- Il parametro `linttools_dir` ha valore `None`, è una stringa vuota, oppure non esiste quella directory in `tools_root`
		"""
		self._check_initargs(
			dockf_builder, tag_prefix,
			gentests_dir, envconfig_dir, dockerfile_fname, py_vers_fname, deps_files,
			tools_root, linttools_dir
		)
		
		self._json_dec: JSONDecoder = JSONDecoder()
		
		self._project_set: bool = False
		self._def_pyvers_set: bool = False

		self._docker: DockerClient = None
		try:
			docker_host: str = os_getenv["DOCKER_HOST"]
			self._docker = DockerClient(base_url=docker_host)
		except KeyError:
			self._docker = docker_getclient()
		
		self._dockf_builder: ATransactDockfBuilder = dockf_builder
		self._dockf_fname: str = dockerfile_fname
		self._tag_prefix: str = tag_prefix

		self._envconfig_dir: str = envconfig_dir
		self._gentests_dir: str = gentests_dir

		self._path_prefix: str = self.PATH_PREFIX
		if path_prefix is not None:
			self._path_prefix = path_prefix.rstrip("/")

		# Il nome del progetto focale impostato
		self._proj_name: str = None
		# La Full Project Root Path reale
		self._orig_full_root: str = None
		# La Full Project Root Path all' interno del container
		self._full_root: str = None
		# La Focal Project Root Path all' interno del container
		self._focal_root: str = None
		# La Tests Project Root Path all' interno del container
		self._tests_root: str = None
		# La Env-config Project Root Path all' interno del container
		self._envconfig_root: str = None
		# La Gen-tests Project Root Path all' interno del container
		self._gentests_root: str = None

		# File con Versione dell' Interprete Python
		self._py_vers_fname: str = py_vers_fname
		self._py_vers_path: str = None

		# File (json di dizionari) con lista di Dipendenze Python
		self._py_deps_fname: str = deps_files[0]
		self._py_deps_path: str = None

		# File con lista di Dipendenze Esterne
		self._ext_deps_fname: str = deps_files[1]
		self._ext_deps_path: str = None

		# Files Script Precedente e Successivo all' installazione delle Dipendenze Esterne
		self._prescr_fname: str = deps_files[2]
		self._prescr_path: str = None
		self._postscr_fname: str = deps_files[3]
		self._postscr_path: str = None
		self._postscrpy_fname: str = deps_files[4]
		self._postscrpy_path: str = None
		
		# Path dei tools dell' ambiente reale
		self._tools_root: str = tools_root.rstrip(_PATH_SEPS)
		# Directory dei tools per il calcolo della coverage
		self._covtools_dir: str = covtools_dir
		# Directory dei tools per la verifica di linting
		self._linttools_dir: str = linttools_dir
	
	
	def set_default_pyversion(self, python_version: str):
		vers_found: Match[str] = reg_search(self._PYVERS_PATT, python_version)
		if vers_found is None:
			raise ValueError()
		
		self._def_pyvers = python_version
		self._def_pyvers_set = True
	
	
	def set_focal_project(
			self,
			proj_name: str,
	        full_root: str,
			focal_root: str,
			tests_root: str
	):
		if (proj_name is None) or (proj_name == ""):
			raise ValueError()
		if (full_root is None) or (full_root == ""):
			raise ValueError()
		if (focal_root is None) or (focal_root == ""):
			raise ValueError()
		if (tests_root is None) or (tests_root == ""):
			raise ValueError()
		
		full_dirname: str = path_split(full_root)[1]
		focal_dirname: str = path_split(focal_root)[1]
		tests_relpath: str = SystemPath(tests_root).relative_to(full_root).as_posix()
		self._proj_name = proj_name
		self._orig_full_root = full_root
		
		self._full_root: str = f"{self._path_prefix}/{full_dirname}"
		self._focal_root: str = f"{self._full_root}/{focal_dirname}"
		self._tests_root: str = f"{self._full_root}/{tests_relpath}"
		self._gentests_root: str = f"{self._full_root}/{self._gentests_dir}"
		self._envconfig_root: str = f"{self._full_root}/{self._envconfig_dir}"
		
		self._set_envconfig_entities()

		self._project_set = True
	
	
	def set_path_prefix(self, path_prefix: str):
		self._assert_inited()

		pathpref_found: Match[str] = reg_search(self._LINUXPATH_PATT, path_prefix)
		if pathpref_found.group("path_prefix") is None:
			raise ValueError()
		
		path_prefix_strpd: str = path_prefix.rstrip("/")

		self._full_root = self._change_prefix_of_path(
			path_prefix_strpd,
			self._full_root,
		)
		self._focal_root = self._change_prefix_of_path(
			path_prefix_strpd,
			self._focal_root,
		)
		self._tests_root = self._change_prefix_of_path(
			path_prefix_strpd,
			self._tests_root,
		)
		self._gentests_root = self._change_prefix_of_path(
			path_prefix_strpd,
			self._gentests_root,
		)
		self._envconfig_root = self._change_prefix_of_path(
			path_prefix_strpd,
			self._envconfig_root,
		)

		self._change_prefix_envc_entities(path_prefix_strpd)

		self._path_prefix = path_prefix_strpd
	
	
	def build_image(
			self,
			post_steps: EImageBuiltOption = EImageBuiltOption.DOCKIGNORE
	) -> DockerImage:
		self._assert_inited()

		python_version: str = self._get_python_version()
		ext_deps: List[str] = self._get_ext_deps()
		
		# Impostazione di BASH come shell per l' esecuzione dei comandi
		self._dockf_builder.set_shell("/bin/sh", ["-c"])

		# Impostazione della versione dell' interprete Python che verrà utilizzata
		self._dockf_builder.set_envvar("PYTHON_VERSION", python_version)
		
		# Creazione del path prefix e impostazione della directory corrente su di esso
		self._dockf_builder.add_shellcmd(f"mkdir -p {self._path_prefix}")
		self._dockf_builder.add_workdir(self._path_prefix)
		
		self._dockf_builder.begin_cmds_tran()
		
		# Installazione di `pip` e del comando `yes` (utilizzato per le installazioni silenziose)
		self._dockf_builder.add_shellcmd_step("apt-get update && apt install -y coreutils python3-pip")

		# Installazione di `pyenv`
		self._configure_pyenv()

		# Configurazione delle variabili d'ambiente locali
		self._configure_local_envvars()
		
		# Configurazione dell' installazione delle dipendenze
		self._configure_deps_install(ext_deps)

		# Installazione di `coverage.py`
		self._dockf_builder.add_shellcmd_step(f'python3 -m pip install coverage=="{self._ap__covpy_version()}"')
		# Installazione di `pylint`
		self._dockf_builder.add_shellcmd_step(f'python3 -m pip install pylint=="{self._ap__pylint_version()}"')
		
		self._dockf_builder.end_cmds_tran()
		
		# Copia dei tools per la coverage
		covtools_path: SystemPath = SystemPath(self._tools_root, self._covtools_dir)
		self._copy_tool_subroot_infullroot(str(covtools_path))
		
		# Copia dei tools per il linting
		linttools_path: SystemPath = SystemPath(self._tools_root, self._linttools_dir)
		self._copy_tool_subroot_infullroot(str(linttools_path))
		
		# Impostazione della directory corrente sul path prefix
		self._dockf_builder.add_workdir(self._path_prefix)
		
		dockerfile_path: str = f"{self._orig_full_root}/{self._dockf_fname}"
		self._dockf_builder.build_dockerfile(dockerfile_path)

		proj_image: DockerImage = self._docker.images.build(
			path=self._orig_full_root,
			dockerfile=self._dockf_fname,
			tag=f"{self._tag_prefix}_{self._proj_name}"
		)[0]

		match post_steps:
			case EImageBuiltOption.DOCKF_REMOVE:
				os_remove(dockerfile_path)
			case EImageBuiltOption.DOCKIGNORE:
				dockerignore_path: str = f"{self._orig_full_root}/.dockignore"
				with open(dockerignore_path, "a") as fdocki:
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
		return PosixPath(
			new_path_prefix,
			PosixPath(path_tochange).relative_to(self._path_prefix)
		).as_posix()
	
	
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
				self._prescr_path = self._change_prefix_of_path(
					new_path_prefix,
					self._prescr_path,
				)
			if self._postscr_path != "":
				self._postscr_path = self._change_prefix_of_path(
					new_path_prefix,
					self._postscr_path,
				)
				
		if self._postscrpy_path != "":
			self._postscrpy_path = self._change_prefix_of_path(
				new_path_prefix,
				self._postscrpy_path,
			)

			
	def _set_envconfig_entities(self):
		"""
			Imposta le paths degli elementi della Env-config Project Root Path
			(in base alla loro esistenza)
		"""
		orig_envconfig_root = path_join(self._orig_full_root, self._envconfig_dir)
		
		self._py_vers_path = self._set_envc_entity_ifexists(
			orig_envconfig_root,
			self._py_vers_fname,
		)
		
		self._py_deps_path = self._set_envc_entity_ifexists(
			orig_envconfig_root,
			self._py_deps_fname,
		)
		self._ext_deps_path = self._set_envc_entity_ifexists(
			orig_envconfig_root,
			self._ext_deps_fname,
		)
		
		if self._ext_deps_path != "":
			self._prescr_path = self._set_envc_entity_ifexists(
				orig_envconfig_root,
				self._prescr_fname,
				container=True
			)

			self._postscr_path = self._set_envc_entity_ifexists(
				orig_envconfig_root,
				self._postscr_fname,
				container=True
			)
			
		self._postscrpy_path = self._set_envc_entity_ifexists(
			orig_envconfig_root,
			self._postscrpy_fname,
			container=True
		)
		
		
	def _set_envc_entity_ifexists(
			self,
			envconfig_root: str,
			entity_fname: str,
			container: bool = False
	) -> str:
		"""
			Imposta il valore di un file della Env-config Project Root Path, da utilizzarsi
			all' interno dell' ambiente focale, se esiste realmente

			Parameters
			----------
				envconfig_root: str
					Una stringa contenente la Env-Config Project Root Path reale
			
				entity_fname: str
					Una stringa contenente il nome del file di cui impostare la path relativamente
					all' ambiente focale
					
				container: bool
					Opzionale. Default = `False`. Un booleano che indica se la path che deve essere
					ritornata è relativa al container.
					Nel caso in cui questo flag sia `False` la path che viene ritornata è la path reale
					dell' oggetto della Env-config Project Root Path fornito

			Returns
			-------
				str
					Una stringa contenente la path (relativa al container) del file dato
		"""
		orig_entity_path: str = path_join(envconfig_root, entity_fname)
		if not os_fdexists(orig_entity_path):
			return ""
		else:
			if container:
				return f"{self._envconfig_root}/{entity_fname}"
			else:
				return orig_entity_path
		
		
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
	
	
	def _get_py_deps(self) -> List[Dict[str, str]]:
		"""
			Legge le dipendenze python dal file, relativamente al progetto focale impostato.

			Returns
			-------
				List[Dict[str, str]]
					Una lista di dizionari contenente un elemento per ogni dipendenza python da installare.
					Ogni dizionario contiene:
						- "r": La dipendenza/e da installare con `pip` (se più di una si separano con gli spazi)
						- Ogni altra chiave è un flag per il comando `pip` (ed eventuale valore, oppure None)
		"""
		py_deps: List[Dict[str, str]]
		if self._py_deps_path != "":
			with open(self._py_deps_path, "r") as fp:
				py_deps = self._json_dec.decode(fp.read())
			return py_deps
		return list()
		

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
		self._dockf_builder.add_shellcmd_step(
			"apt-get install -y "
			"build-essential curl git zlib1g-dev "
			"libssl-dev libreadline-dev "
			"libffi-dev libbz2-dev libsqlite3-dev"
		)
		self._dockf_builder.add_shellcmd_step("git clone https://github.com/pyenv/pyenv.git ~/.pyenv")


	def _configure_local_envvars(self):
		"""
			Configura il costruttore di dockerfiles per definire le variabili d'ambiente locali nelle
			immagini che verranno prodotte successivamente
		"""
		self._dockf_builder.set_envvar("PYENV_ROOT", "/root/.pyenv")
		self._dockf_builder.set_envvar(
			"PATH",
		    "$HOME/.local/bin:$HOME/bin:$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
		)
		self._dockf_builder.set_envvar("FULL_ROOT", self._full_root)
		self._dockf_builder.set_envvar("FOCAL_ROOT", self._focal_root)
		self._dockf_builder.set_envvar("TESTS_ROOT", self._tests_root)
		self._dockf_builder.set_envvar("GENTESTS_ROOT", self._gentests_root)
		self._dockf_builder.set_envvar("LINTTOOLS_DIRNAME", self._linttools_dir)
		self._dockf_builder.set_envvar("COVTOOLS_DIRNAME", self._covtools_dir)


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
		# Esecuzione dello script Pre-installazione delle dipendenze esterne
		if os_fdexists(self._ext_deps_path):
			if self._prescr_path != "":
				self._dockf_builder.add_shellcmd_step(f". {self._prescr_path}")

		# Installazione delle dipendenze esterne
		for ext_dep in ext_deps:
			self._dockf_builder.add_shellcmd_step(f"apt-get install -y {ext_dep}")

		# Esecuzione dello script Post-installazione delle dipendenze esterne
		if os_fdexists(self._ext_deps_path):
			if self._postscr_path != "":
				self._dockf_builder.add_shellcmd_step(f". {self._postscr_path}")

		# Installazione delle dipendenze (packages) Python
		py_packs: str
		pip_flags: str
		for pydep_dict in self._get_py_deps():
			pip_flags = ""
			py_packs = pydep_dict.pop("r")
			for flag, value in pydep_dict.items():
				pip_flags += f"{flag}"
				if value is not None:
					pip_flags += f" {value}"
					
			self._dockf_builder.add_shellcmd_step(
				f"yes | pip install -q -q -q {pip_flags} \"{py_packs}\""
			)
			
		# Esecuzione dello script Post-installazione delle dipendenze Python
		if os_fdexists(self._postscrpy_path):
			self._dockf_builder.add_shellcmd_step(f". {self._postscrpy_path}")
		
		
	def _copy_tool_subroot_infullroot(self, tool_subroot: str):
		"""
			Copia la sotto-root dei tools per l' ambiente focale specificata
			all' interno della Full Project Root Path del progetto focale corrente.
			Ciò viene utilizzato per permettere le operazioni di `COPY` durante il build
			delle immagini degli ambienti focali.
			
			Parameters
			----------
				tool_subroot: str
					Una stringa contenente la sotto-root da copiare all' interno della
					Full Project Root Path del progetto focale impostato
		"""
		tooldest_path: str = path_join(
			self._orig_full_root, path_split(tool_subroot)[1]
		)
		if os_fdexists(tooldest_path):
			os_dremove(tooldest_path)
		
		os_dcopy(
			tool_subroot,
			tooldest_path,
			dirs_exist_ok=False
		)
		
		
	@classmethod
	def _check_initargs(
			cls,
			dockf_builder: ATransactDockfBuilder,
			tag_prefix: str,
			gentests_dir: str,
			envconfig_dir: str,
			dockerfile_fname: str,
			py_vers_fname: str,
			deps_files: Tuple[str, str, str, str, str],
			tools_root: str,
			linttools_dir: str,
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
						- Il parametro `py_vers_fname` ha valore `None` o è una stringa vuota
						- Il parametro `deps_files` ha valore `None`, è una tupla vuota; oppure uno dei suoi elementi è `None` o almeno uno è una stringa vuota
						- Il parametro `tools_root` ha valore `None, è una stringa vuota, oppure è una path invalida
						- Il parametro `linttools_dir` ha valore `None`, è una stringa vuota, oppure non esiste quella directory in `tools_root`
		"""
		if (
			(dockf_builder is None) or
			(tag_prefix is None) or
			(gentests_dir is None) or
			(envconfig_dir is None) or
			(dockerfile_fname is None) or
			(py_vers_fname is None) or
			(deps_files is None) or
			(tools_root is None) or
			(linttools_dir is None)
		):
			raise ValueError()

		if (
			(tag_prefix == "") or
			(gentests_dir == "") or
			(envconfig_dir == "") or
			(dockerfile_fname == "") or
			(py_vers_fname == "") or
			(deps_files == tuple()) or
			(tools_root == "")
		):
			raise ValueError()
		
		for dep_file in deps_files:
			if (
				(dep_file is None) or
				(dep_file == "")
			):
				raise ValueError()