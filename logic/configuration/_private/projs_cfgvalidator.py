from typing import List, Dict, Set, Any, Tuple
from config_io.config_validator._private._a_base_cfgvalidator import _ABaseConfigValidator

# ============ Path Utilities ============ #
from os.path import (
	sep as path_sep,
	altsep as path_altsep,
	join as path_join
)
_PATH_SEPS: str = f"{path_sep}{path_altsep if path_altsep is not None else ''}"
# ======================================== #
from path_validator import (
	EPathValidationErrorType,
	PathValidator
)

from config_io.config_validator.exceptions import (
	FieldDoesntExistsError,
	ConfigExtraFieldsError,
	InvalidConfigValueError
)



class ProjectsConfigValidator(_ABaseConfigValidator):
	"""
		Represents an `IConfigValidator` for the configuration file of the focal projects for which tests will be generated.
		
		The configuration file read is a dictionary containing:
        
            -   A dictionary entry for each focal project, whose key is the project name.
                Each dictionary must contain:
                
                    * "full_root" (str): The Full Project Root Path of the project (as an absolute path)
					* "focal_root" (str): The Focal Project Root Path of the project (as a path relative to the Full Project Root Path)
                    * "tests_root" (str): The Tests Project Root Path of the project (as a path relative to the Full Project Root Path)
                    
                and may optionally contain:
					
					* "focal_excluded" (List[str]): A list of paths relative to the Focal Project Root Path, which should not be considered part of the focal code
                    * "tests_excluded" (List[str]): A list of paths relative to the Tests Project Root Path, which should not be considered part of the entire project's test suite
	"""
	
	_REQ_FIELDS: Set[str] = {"full_root", "focal_root", "tests_root"}
	_OPT_FIELDS: Set[str] = {"focal_excluded", "tests_excluded"}
	
	_SYNT_ERROR: str = 'The path specified by the "{param}" parameter is invalid (project "{proj_name}")")'
	_NOTEX_ERROR: str = 'The path specified by the "{param}" parameter does not exist (project "{proj_name}")")'
	_PERM_ERROR: str = 'The path specified by the "{param}" parameter cannot be accessed (project "{proj_name}")")'
	_UNRE_ERROR: str = 'The path specified by the "{param}" parameter cannot be reached (project "{proj_name}")")'
	
	def __init__(
			self,
			config_dict: Dict[str, Any]
	):
		"""
			Creates a new ProjectsConfigValidator by reading the configuration file at the specified path.
            
            Parameters
            ----------
				config_dict: Dict[str, Any]
                    A mixed dictionary, indexed by strings, representing the configuration file that was read

			Raises
            ------
                ValueError
                    Occurs if:
                    
                        - The provided dictionary has a value of `None`
                        - The provided dictionary is empty
		"""
		super().__init__(config_dict)
		
		self._pathval: PathValidator = PathValidator()
	
	
	def _p__efields_strict(self) -> bool:
		return False
	
	
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		return (set(), set())
	
	
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		full_root: str
		focal_root: str
		tests_root: str
		focal_excl: List[str]
		
		for proj_name, project in config_read.items():
			config_fields = set(project.keys())
			
			if config_fields < self._REQ_FIELDS:
				raise FieldDoesntExistsError()
			
			full_root = project["full_root"].rstrip(_PATH_SEPS)
			focal_root = project["focal_root"].rstrip(_PATH_SEPS)
			tests_root = project["tests_root"].rstrip(_PATH_SEPS)
			
			self._assert_path(full_root, proj_name, "full_root")
			self._assert_path(path_join(full_root, focal_root), proj_name, "focal_root")
			self._assert_path(path_join(full_root, tests_root), proj_name, "tests_root")

	
	def _ap__assert_optional(self, config_read: Dict[str, Any]):
		focal_excluded: List[str]
		tests_excluded: List[str]
		
		full_root: str
		focal_root: str
		tests_root: str
		
		for proj_name, project in config_read.items():
			config_fields = set(project.keys())
			
			extra_fields = (
				config_fields.difference(self._REQ_FIELDS).union(
				self._REQ_FIELDS.difference(config_fields))
			)
			if extra_fields.difference(self._OPT_FIELDS) != set():
				raise ConfigExtraFieldsError()
			
			full_root = project["full_root"].rstrip(_PATH_SEPS)
			focal_root = path_join(full_root, project["focal_root"].rstrip(_PATH_SEPS))
			tests_root = path_join(full_root, project["tests_root"].rstrip(_PATH_SEPS))
			
			focal_excluded = project.get("focal_excluded", None)
			if focal_excluded is not None:
				self._assert_excluded_paths(
					focal_root,
					focal_excluded,
					proj_name,
					"focal_excluded"
				)
				
			tests_excluded = project.get("tests_excluded", None)
			if tests_excluded is not None:
				self._assert_excluded_paths(
					tests_root,
					tests_excluded,
					proj_name,
					"tests_excluded"
				)
	
	
	def _ap__assert_purperrors(self, config_read: Dict[str, Any]):
		return
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _assert_path(
			self,
			path_totest: str,
			proj_name: str,
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
                    A string containing the path to verify for existence and syntactic correctness
					
				proj_name: str
                    A string containing the name of the target project whose path is to be tested
                    
                param: str
                    A string containing the parameter for which the given path is to be verified
			
			Raises:
            ------
                InvalidConfigValueError
                    Occurs if:
                    
                        - The path is not syntactically valid
                        - The provided path does not exist
                        - The provided path is inaccessible
		"""
		self._pathval.set_error_msg(
			EPathValidationErrorType.SYNTACTIC,
			self._SYNT_ERROR.format(param=param, proj_name=proj_name)
		)
		self._pathval.set_error_msg(
			EPathValidationErrorType.NOTEXISTS,
			self._NOTEX_ERROR.format(param=param, proj_name=proj_name)
		)
		self._pathval.set_error_msg(
			EPathValidationErrorType.PERMISSION,
			self._PERM_ERROR.format(param=param, proj_name=proj_name)
		)
		self._pathval.set_error_msg(
			EPathValidationErrorType.INACCESSIBLE,
			self._UNRE_ERROR.format(param=param, proj_name=proj_name)
		)
		
		try:
			self._pathval.assert_path(path_totest)
		except (NotADirectoryError,
		        FileNotFoundError,
		        PermissionError,
		        OSError):
			raise InvalidConfigValueError()


	def _assert_excluded_paths(
			self,
			root: str,
			excluded_list: List[str],
			proj_name: str,
			param: str
	):
		"""
			Verifies the validity of the fields related to the excluded paths.
            
            If the verification is successful, this operation is equivalent to a no-op.
            
            Parameters
            ----------
				root: str
                    A string containing the root path to which the provided excluded paths refer
            
                excluded_list: List[str]
                    A list of strings containing the relative excluded paths
					
				proj_name: str
                    A string containing the name of the project whose excluded paths are being checked
                    
                param: str
                    A string containing the name of the field being checked
			
			Raises
            ------
                InvalidConfigValueError
                    Occurs if at least one of the excluded paths is invalid
		"""
		for path in excluded_list:
			self._assert_path(path_join(root, path), proj_name, param)