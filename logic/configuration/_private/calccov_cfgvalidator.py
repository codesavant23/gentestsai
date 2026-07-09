from typing import Dict, Set, Any, Tuple
from config_io.config_validator._private._a_base_cfgvalidator import _ABaseConfigValidator

# ============ Path Utilities ============ #
from os.path import join as path_join
# ======================================== #
from path_validator import (
	EPathValidationErrorType,
	PathValidator
)

from config_io.config_validator.exceptions import InvalidConfigValueError



class CalcCovConfigValidator(_ABaseConfigValidator):
	"""
		Represents an `IConfigValidator` for the configuration file containing the options for calculating test suite coverage.
        
        The configuration file read is a dictionary containing:
		
			- "covconfig_dir" (str): The name of the directory (if any) corresponding to the Cov-config Project Root Path for each target project
            - "covrc_fname" (str): The name of the ".coveragerc" file that will be written by GenTestsAI for coverage.py
            - "pytargs_fname" (str): The name of the JSON file (if present) containing the list of arguments for `pytest`
            - "covargs_fname" (str): The name of the JSON file (if present) containing the list of arguments for `pytest`
            - "calccov_script" (str): The name of the Python script that will perform the coverage calculation within the focal environment
	"""
	
	_REQ_FIELDS: Set[str] = {
		"covconfig_dir",
		"covrc_fname",
		"pytargs_fname",
		"covargs_fname",
		"calccov_script"
	}
	
	_SYNT_ERROR: str = 'The path specified by the "{param}" parameter is invalid'
	_NOTEX_ERROR: str = 'The path specified by the "{param}" parameter does not exist'
	_PERM_ERROR: str = 'The path specified by the "{param}" parameter cannot be accessed'
	_UNRE_ERROR: str = 'The path specified by the "{param}" parameter cannot be reached'
	
	def __init__(
			self,
			config_dict: Dict[str, Any],
			covtools_root: str
	):
		"""
			Creates a new ProjectsConfigValidator by reading the configuration file at the specified path.
            
            Parameters
            ----------
				config_dict: Dict[str, Any]
                    A mixed dictionary, indexed by strings, representing
                    the configuration file read
					
				covtools_root: str
                    A string representing the path containing the coverage tools
                    to be used within the target environments

            Raises
            ------
                ValueError
                    Occurs if:
					
						- The `config_dict` parameter is `None`
                        - The `config_dict` parameter is an empty dictionary
                        - The `covtools_root` parameter is `None`
                        - The `covtools_root` parameter is an empty string
		"""
		super().__init__(config_dict)
		
		if (covtools_root is None) or (covtools_root == ""):
			raise ValueError()
		
		self._covtools_root: str = covtools_root
		self._pathval: PathValidator = PathValidator()
	
	
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		return (self._REQ_FIELDS, set())
	
	
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		covrc_fname: str = config_read["covrc_fname"]
		covconfig_dir: str = config_read["covconfig_dir"]
		pytargs_fname: str = config_read["pytargs_fname"]
		covargs_fname: str = config_read["covargs_fname"]
		calccov_script: str = config_read["calccov_script"]
		
		if covrc_fname == "":
			raise InvalidConfigValueError()
		if calccov_script == "":
			raise InvalidConfigValueError()
		if covconfig_dir == "":
			raise InvalidConfigValueError()
		if pytargs_fname == "":
			raise InvalidConfigValueError()
		if covargs_fname == "":
			raise InvalidConfigValueError()

		self._assert_path(
			path_join(self._covtools_root, calccov_script),
			"calccov_script"
		)


	def _ap__assert_optional(self, config_read: Dict[str, Any]):
		return


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