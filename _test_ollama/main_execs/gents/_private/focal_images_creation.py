from typing import Tuple, Dict, Any

# ============ Path Utilities ============ #
from os.path import split as path_split
# ======================================== #
# ============== Docker SDK Utilities =============== #
from docker.models.images import Image as DockerImage
# =================================================== #
from logic.focalproj_configuration.dockerfile_builder import (
	ATransactDockfBuilder, SimpleTransactDockfBuilder
)
from logic.focalproj_configuration.focal_env.focalenv_configurator import (
	IFocalEnvConfigurator, V1FocalEnvConfigurator, EImageBuiltOption
)



def create_focal_images(
		projs_config: Dict[str, Dict[str, Any]],
		base_image: str,
		dockerfile_fname: str,
		gentests_dir: str, envconfig_dir: str,
		def_pyvers: str, py_vers_fname: str,
		deps_files: Tuple[str, str, str, str],
		tools_root: str, linttools_dir: str,
		path_prefix: str, conttools_root: str,
) -> Dict[str, DockerImage]:
	"""
		Crea le immagini che corrispondono agli ambienti focali dei progetti focali	
		con cui si intende testare le capacità dei LLMs
		
		Parameters
		----------
			projs_config: Dict[str, Dict[str, Any]]
				Un dizionario di dizionari variegati rappresentante il file di configurazione dei progetti
				focali
		
			base_image: str
				Una stringa contenente il nome dell' immagine base da utilizzare per ogni
				immagine di ambiente focale che verrà creata
		
			gentests_dir: str
				Una stringa contenente il nome della directory della Gen-tests Project Root Path di ogni progetto focale
			
			envconfig_dir: str
				Una stringa contenente il nome della directory della Env-Config Project Root Path di ogni progetto focale
			
			dockerfile_fname: str
				Una stringa contenente il nome del dockerfile che verrà generato per ogni immagine di ambiente focale
			
			def_pyvers: str
				Una stringa contenente la versione di default dell' interprete Python da utilizzare nel caso in cui per un
				determinato progetto non sia richiesta una versione specifica
			
			py_vers_fname: str
				Una stringa contenente il nome dell' eventuale file che contiene la versione specifica dell' interprete Python
				da utilizzare nell' ambiente focale
				
			deps_files : Tuple[str, str, str, str]
				Una 4-tupla di stringhe contenente:
				
					- [0]: Il nome dell' eventuale file che specifica le dipendenze Python del progetto focale
					- [1]: Il nome dell' eventuale file che specifica le dipendenze non-Python del progetto focale
					- [2]: Il nome dell' eventuale script che contiene il codice shell da eseguire prima l' installazione delle dipendenze esterne
					- [3]: Il nome dell' eventuale script che contiene il codice shell da eseguire dopo l' installazione delle dipendenze esterne
					
			tools_root: str
				Una stringa rappresentante la path che contiene i tools da utilizzare all' interno dell' ambiente focale
			
			linttools_dir: str
				Una stringa contenente il nome della directory, all' interno di `tools_root`, che contiene i tools
				per effettuare la verifica di linting
				
			path_prefix: str
				Una stringa rappresentante il path prefix da utilizzare negli ambienti focali prodotti
			
			conttools_root: str
				Una stringa rappresentante la path, relativa all' ambiente focale, che conterrà i tools
				da utilizzare all' interno di ognuno di essi

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
					- Il parametro `linttools_dir` ha valore `None`, è una stringa vuota, oppure non esiste quella directory in tools_root
					- Il parametro `conttools_root` è una stringa vuota, oppure è una path Linux invalida
	"""
	focal_envs: Dict[str, DockerImage] = dict()
	
	dockf_bder: ATransactDockfBuilder = SimpleTransactDockfBuilder()
	dockf_bder.new_dockerfile()
	
	fenv_confgor: IFocalEnvConfigurator = V1FocalEnvConfigurator(
		dockf_bder,
		gentests_dir, envconfig_dir,
		dockerfile_fname,
		py_vers_fname, deps_files,
		tools_root, linttools_dir, conttools_root,
		path_prefix
	)
	
	dockf_bder.set_base_image(base_image)
	fenv_confgor.set_default_pyversion(def_pyvers)
	
	full_root: str
	for proj_name, proj_info in projs_config.items():
		full_root = path_split(proj_info["focal_root"])[0]
		fenv_confgor.set_focal_project(
			full_root,
			proj_info["focal_root"],
			proj_info["tests_root"]
		)
		focal_envs[proj_name] = fenv_confgor.build_image(EImageBuiltOption.DOCKIGNORE)
	
	return focal_envs