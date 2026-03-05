from typing import Tuple, Dict, Any

# ============== OS Utilities ============== #
from os import makedirs as os_mkdirs
from shutil import rmtree as os_dremove
# ========================================== #
# ============ Path Utilities ============ #
from os.path import (
	join as path_join,
	sep as path_sep,
	altsep as path_altsep,
)
_PATH_SEPS: str = f"{path_sep}{path_altsep if path_altsep is not None else ''}"
# ======================================== #
# ============== Docker SDK Utilities =============== #
from docker.models.images import Image as DockerImage
from docker.errors import ImageNotFound
from docker.client import DockerClient
# =================================================== #
from logic.focalproj_configuration.focal_env.focalenv_configurator import (
	IFocalEnvConfigurator, V1FocalEnvConfigurator
)
from ..._private.getting_contmanager import retrieve_contmanager

from logic.utils.process_logger._private.process_logger import ProcessLogger



def create_focal_images(
		projs_config: Dict[str, Dict[str, Any]],
		image_prefix: str, image_tag: str,
		dockerfile_fname: str,
		shared_dirname: str,
		gentests_dir: str, envconfig_dir: str,
		py_vers_fname: str,
		deps_files: Tuple[str, str, str, str, str, str],
		tools_root: str,
		linttools_dir: str,
		covtools_dir: str,
		path_prefix: str,
		gents_logger: ProcessLogger
) -> Dict[str, DockerImage]:
	"""
		Crea/Ottiene le immagini che corrispondono agli ambienti focali dei progetti focali
		con cui si intende testare le capacità dei LLMs
		
		Parameters
		----------
			projs_config: Dict[str, Dict[str, Any]]
				Un dizionario di dizionari variegati rappresentante il file di configurazione dei progetti
				focali
		
			image_tag: str
				Una stringa contenente il tag dell' immagine base "python" da utilizzare per ogni
				immagine di ambiente focale che verrà creata
		
			gentests_dir: str
				Una stringa contenente il nome della directory della Gen-tests Project Root Path di ogni progetto focale
			
			envconfig_dir: str
				Una stringa contenente il nome della directory della Env-Config Project Root Path di ogni progetto focale
			
			dockerfile_fname: str
				Una stringa contenente il nome del dockerfile che verrà generato per ogni immagine di ambiente focale
				
			shared_dirname: str
				Una stringa contenente il nome della directory condivisa tra ogni ambiente focale
				e la Full Project Root Path del suo progetto focale
				
			image_prefix: str
				Una stringa contenente il prefisso da utilizzare per il tag delle immagini focali create
				(o da ottenere)
			
			py_vers_fname: str
				Una stringa rappresentante il nome dell' eventuale file che contiene il tag specifico
				dell' immagine "python" da utilizzarsi al posto di quella di fallback
				
			deps_files: Tuple[str, str, str, str, str, str]
					Una 6-tupla di stringhe contenente:
						
						- [0]: Il nome dell' eventuale file che specifica le dipendenze Python del progetto focale
						- [1]: Il nome dell' eventuale file che specifica le dipendenze non-Python del progetto focale
						- [2]: Il nome dell' eventuale script che contiene il codice shell da eseguire prima dell' installazione delle dipendenze esterne
						- [3]: Il nome dell' eventuale script che contiene il codice shell da eseguire dopo l' installazione delle dipendenze esterne
						- [4]: Il nome dell' eventuale script che contiene il codice shell da eseguire prima dell' installazione delle dipendenze Python
						- [5]: Il nome dell' eventuale script che contiene il codice shell da eseguire dopo l' installazione delle dipendenze Python
					
			tools_root: str
				Una stringa rappresentante la path che contiene i tools da utilizzare all' interno dell' ambiente focale
			
			linttools_dir: str
				Una stringa contenente il nome della directory, all' interno di `tools_root`, che contiene i tools
				per effettuare la verifica di linting
				
			covtools_dir: str
				Una stringa contenente il nome della directory, all' interno di `tools_root`, che contiene i tools
				per effettuare il calcolo della coverage
				
			path_prefix: str
				Una stringa rappresentante il path prefix da utilizzare negli ambienti focali prodotti
				
			gents_logger: ProcessLogger
				Un oggetto `ProcessLogger` rappresentante il logger da utilizzare per registrare gli steps
				del processo di creazione/ottenimento delle immagini di ogni progetto focale
				
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
					- Il parametro `tools_root` ha valore ``None`, è una stringa vuota, oppure è una path invalida
					- Il parametro `linttools_dir` ha valore `None`, è una stringa vuota, oppure non esiste quella directory in `tools_root`
					- Il parametro `path_prefix` è una stringa vuota, oppure è una path Linux invalida
					- Il parametro `gents_logger` ha valore `None`
	"""
	focal_envs: Dict[str, DockerImage] = dict()
	
	fenv_confgor: IFocalEnvConfigurator = V1FocalEnvConfigurator(
		image_prefix,
		gentests_dir, envconfig_dir,
		dockerfile_fname,
		py_vers_fname, deps_files,
		tools_root, linttools_dir, covtools_dir,
		path_prefix=path_prefix
	)
	
	fenv_confgor.set_default_pyversion(image_tag)
	
	cont_manager: DockerClient = retrieve_contmanager()
	
	full_root: str
	focal_root: str
	tests_root: str
	shared_path: str
	
	for proj_name, proj_info in projs_config.items():
		gents_logger.process_start(f'Progetto focale attuale: "{proj_name}" ... ')
		full_root = proj_info["full_root"].rstrip(_PATH_SEPS)
		
		shared_path = path_join(full_root, shared_dirname)
		os_dremove(shared_path, ignore_errors=True)
		os_mkdirs(shared_path)
		
		try:
			focal_envs[proj_name] = cont_manager.images.get(
				f"{image_prefix}_{proj_name}"
			)
			gents_logger.set_endmessage("OTTENUTA!")
		except ImageNotFound:
			
			focal_root = path_join(full_root, proj_info["focal_root"].rstrip(_PATH_SEPS))
			tests_root = path_join(full_root, proj_info["tests_root"].rstrip(_PATH_SEPS))
			
			fenv_confgor.set_focal_project(
				proj_name,
				full_root,
				focal_root,
				tests_root
			)
			focal_envs[proj_name] = fenv_confgor.build_image(True)
			gents_logger.set_endmessage("CREATA!")
		gents_logger.process_end()
	gents_logger.set_endmessage("OK!")
	
	return focal_envs