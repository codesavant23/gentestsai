from typing import List, Dict, Set, Any, Tuple
from config_io.config_validator._private._a_base_cfgvalidator import _ABaseConfigValidator

# ============= RegEx Utilities ============ #
from regex import (
	search as reg_search,
	Match,
)
# ========================================== #
# =========== RequestsForHumans Utilities =========== #
from requests import (
	get as req_get,
	Response as HttpResponse
)
# =================================================== #
# ============== OS Utilities ============== #
from os.path import exists as os_fdexists
# ========================================== #
# ============ Path Utilities ============ #
from os.path import join as path_join
# ======================================== #

from gtsai_lib.focalproj_configuration.focal_env.focalenv_configurator.buildcache_cleaner import \
	EContainerManager

from path_validator import (
	PathValidator,
	EPathValidationErrorType
)

from config_io.config_validator.exceptions import (
	ConfigExtraFieldsError,
	FieldDoesntExistsError,
	InvalidConfigValueError
)



class ProjsEnvironConfigValidator(_ABaseConfigValidator):
	"""
		Represents an `IConfigValidator` for the configuration file that lists information regarding
        the configuration of the target environment for each project for which the selected LLMs will generate tests.
		
		The configuration file read will consist of a dictionary containing the following required entries:
            - "envconfig_dir" (str): The name of the directory (if any) containing the configuration files for the focal environments
            - "image_tag" (str): The Docker 'base' image from which each focal environment image is derived
			- "images_prefix" (str): The prefix to be prepended to the tags of the focal environment images
            - "tools" (Dict[str, str]): A dictionary containing the paths/directories for the tools to be used in each focal environment. It contains:
            
                * "tools_root" (str): The root path containing the tools to be added within each focal environment
                * "linting" (str): The name of the directory containing the tools to perform linting checks within the focal environment
                * "coverage" (str): The name of the directory containing the tools to calculate code coverage within the focal environment
				
			- "environ" (Dict[str, str]): A dictionary containing parameters related to the focal environments. It contains:
			
				* "path_prefix" (str): The base path containing the Full Project Root Path of the focal project within each focal environment
                * "lint_executer" (str): The name of the script that will perform linting within each focal environment
				* "inputctr_dir" (str): The name of the directory, within the "path_prefix", that will be used for file sharing between the focal project and its environment
            
            - "project" (Dict[str, str]): Dictionary containing parameters related to each focal project. It contains:
			
				* "dockerfile" (str): The name of the Dockerfile, created by GenTestsAI, that will build the focal environment image
                * "pyversion_file" (str): The name of any text file (in "envconfig_dir") containing the Python interpreter version specific to the project
				* "ext_deps_file" (str): The name of any text file (in "envconfig_dir") containing the non-Python dependencies of the focal project
                * "python_deps_file" (str): The name of the text file (in "envconfig_dir"), if any, containing the Python dependencies of the target project
				* "pre_extdeps_script" (str): The name of the shell script (in "envconfig_dir"), if any, to be executed before installing the non-Python dependencies of the target project
				* "post_extdeps_script" (str): The name of any shell script (in "envconfig_dir") to be executed after the non-Python dependencies of the target project have been installed
                * "pre_pydeps_script" (str): The name of any shell script (in "envconfig_dir") to be executed before installing the Python dependencies of the target project
                * "post_pydeps_script" (str): The name of any shell script (in "envconfig_dir") to be executed after installing the Python dependencies of the target project
				
		and may optionally contain:
        
            - "pref_contman" (str): The name of the container manager (if any) to which GenTestsAI should be connected for managing the focal environments
	"""
	
	_OUTER_FIELDS: Set[str] = {
		"envconfig_dir",
		"images_prefix",
		"image_tag",
		"environ",
		"tools",
		"project"
	}
	_TOOLS_FIELDS: Set[str] = {
		"tools_root",
		"linting",
		"coverage"
	}
	_ENVIRON_FIELDS: Set[str] = {
		"path_prefix",
		"lint_executer",
		"inputctr_dir"
	}
	_1PROJ_FIELDS: Set[str] = {
		"dockerfile",
		"pyversion_file",
		"ext_deps_file", "python_deps_file",
		"pre_pydeps_script", "post_pydeps_script",
		"pre_extdeps_script", "post_extdeps_script"
	}
	_OPT_FIELDS: Set[str] = {
		"pref_contman"
	}
	
	_LINUXPATH_PATT: str = r"^(?P<linux_path>(/[\w.-]+/?)+)$"
	
	_SYNT_ERROR: str = 'The path specified by the "{param}" parameter is invalid'
	_NOTEX_ERROR: str = 'The path specified by the "{param}" parameter does not exist'
	_PERM_ERROR: str = 'The path specified by the "{param}" parameter cannot be accessed'
	_UNRE_ERROR: str = 'The path specified by the "{param}" parameter cannot be reached'
	
	def __init__(
			self,
			config_dict: Dict[str, Any],
			full_roots: List[str],
			docker_hub_vers: str = "v2"
	):
		"""
			Creates a new ProjsEnvironConfigValidator by passing it the Python configuration dictionary
            that will be associated with this validator
            
            Parameters
            ----------
				config_dict: Dict[str, Any]
                    A mixed dictionary, indexed by strings, representing the configuration file
                    that has been read
                    
                full_roots: List[str]
					A list of strings containing the Full Project Root Paths of the focal projects
                    for which to verify the existence of the Dockerfiles that generate the focal environments
                    
                docker_hub_vers: str
                    Optional. Default = `v2`. A string containing the version of the  "Docker Hub Container Image Library"
					(as per the endpoint) where to verify the existence of the base image specified in the configuration file of the focus environments
            
            Raises
            ------
                ValueError
                    Occurs if:
					
						- The provided dictionary is `None`
                        - The provided dictionary is empty
                        - The `full_roots` list is empty
                        - The provided "Docker Hub" version is "None"
                        - The provided "Docker Hub" version is an empty string
		"""
		super().__init__(config_dict)
		
		if len(full_roots) == 0:
			raise ValueError()
		if (docker_hub_vers is None) or (docker_hub_vers == ""):
			raise ValueError()
		
		self._full_roots: List[str] = full_roots
		self._dhub_vers: str = docker_hub_vers
		
		self._pathval: PathValidator = PathValidator()
	
	
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		return (self._OUTER_FIELDS, self._OPT_FIELDS)
	
	
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		imgs_prefix: str = config_read["images_prefix"]
		image_tag: str = config_read["image_tag"]
		project: Dict[str, str] = config_read["project"]
		tools: Dict[str, str] = config_read["tools"]
		environ: Dict[str, str] = config_read["environ"]
		
		proj_fields = set(project.keys())
		if proj_fields < self._1PROJ_FIELDS:
			raise FieldDoesntExistsError()
		if proj_fields > self._1PROJ_FIELDS:
			raise ConfigExtraFieldsError()
		
		tools_fields = set(tools.keys())
		if tools_fields < self._TOOLS_FIELDS:
			raise FieldDoesntExistsError()
		if tools_fields > self._TOOLS_FIELDS:
			raise ConfigExtraFieldsError()
		
		environ_fields = set(environ.keys())
		if environ_fields < self._ENVIRON_FIELDS:
			raise FieldDoesntExistsError()
		if environ_fields > self._ENVIRON_FIELDS:
			raise ConfigExtraFieldsError()
		
		if imgs_prefix == "":
			raise InvalidConfigValueError()
		
		tools_root: str = tools["tools_root"]
		linting_tools: str = path_join(tools_root, tools["linting"])
		cov_tools: str = path_join(tools_root, tools["coverage"])
		
		self._assert_path(tools_root, "tools.tools_root")
		self._assert_path(linting_tools, "tools.linting")
		self._assert_path(cov_tools, "tools.coverage")
		
		if not os_fdexists(path_join(linting_tools, environ["lint_executer"])):
			raise InvalidConfigValueError()

		linux_path_found: Match[str]
		linux_path_found = reg_search(self._LINUXPATH_PATT, environ["path_prefix"])
		if linux_path_found.group("linux_path") is None:
			raise ValueError()
		
		is_pyvers_valid: bool = reg_search(r"[0-9]+\.[0-9]+(\.[0-9]+)?", image_tag) is not None
		if not is_pyvers_valid:
			raise InvalidConfigValueError("Il tag di fallback dell' immagine Python è invalido")
		self._assert_base_image_exists("registry.hub.docker.com", "python", image_tag)
	
	
	def _ap__assert_optional(self, config_read: Dict[str, Any]):
		pref_contman: str = config_read.get("pref_contman", None)
		
		if pref_contman is not None:
			try:
				EContainerManager[pref_contman.upper()]
			except KeyError:
				raise InvalidConfigValueError()
	
	
	def _ap__assert_purperrors(self, config_read: Dict[str, Any]):
		return


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================
	
	
	def _assert_path(
			self,
			path_totest: str,
			param: str
	):
		"""
			Verifies that the provided path is:
                
                - Syntactically correct and exists on the operating system.
                - Reachable
                - Accessible
            
            Parameters
            ----------
				path_totest: str
                    A string containing the path to be checked for existence and syntactic correctness
                    
                param: str
                    A string containing the parameter for which the given path is to be checked
			
			Raises
            ------
                InvalidConfigValueError
                    Occurs if:
                    
                        - The path is not syntactically valid
                        - The provided path does not exist
                        - The provided path is inaccessible
		"""
		self._pathval.set_error_msg(
			EPathValidationErrorType.SYNTACTIC,
			self._SYNT_ERROR.format(param=param)
		)
		self._pathval.set_error_msg(
			EPathValidationErrorType.NOTEXISTS,
			self._NOTEX_ERROR.format(param=param)
		)
		self._pathval.set_error_msg(
			EPathValidationErrorType.PERMISSION,
			self._PERM_ERROR.format(param=param)
		)
		self._pathval.set_error_msg(
			EPathValidationErrorType.INACCESSIBLE,
			self._UNRE_ERROR.format(param=param)
		)
		
		try:
			self._pathval.assert_path(path_totest)
		except (NotADirectoryError,
		        FileNotFoundError,
		        PermissionError,
		        OSError):
			raise InvalidConfigValueError()


	def _assert_base_image_exists(
			self,
			registry: str,
			image: str,
			tag: str
	):
		"""
			Validates the "os_image" field.
            
            If the validation is successful, this operation is equivalent to a no-op.
            
            Parameters
            ----------
				registry: str
                    A string containing the registry from which the image originates
                    
                image: str
                    A string containing the name of the image
                    
                tag: str
                    A string containing the image tag
					
			Raises
            ------
                InvalidConfigValueError
                    Occurs if the image does not exist in the provided registry
		"""
		url = f"https://{registry}/{self._dhub_vers}/repositories/library/{image}/tags/{tag}/"
		response: HttpResponse = req_get(url, timeout=5)
		if not (response.status_code == 200):
			raise InvalidConfigValueError()