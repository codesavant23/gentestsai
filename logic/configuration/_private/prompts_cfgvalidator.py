from typing import List, Dict, Set, Any, Tuple
from config_io.config_validator._private._a_base_cfgvalidator import _ABaseConfigValidator

# ============ Path Utilities ============ #
from os.path import join as path_join
# ======================================== #
# ============== OS Utilities ============== #
from os import walk as os_walk
# ========================================== #
# ============= RegEx Utilities ============ #
from regex import search as reg_search
# ========================================== #

from path_validator import (
	PathValidator,
	EPathValidationErrorType
)

from config_io.config_validator.exceptions import (
	InvalidConfigValueError
)



class PromptsConfigValidator(_ABaseConfigValidator):
	"""
		Represents an `IConfigValidator` for the configuration file that specifies the parameters related to prompts.
        It specifies both general prompt parameters and the prompts to be used for the "Generation"
        and "Correction" processes of GenTestsAI.
		
		The configuration file read is a dictionary containing:
        
            - "base_path" (str): The absolute base path containing the folders with the prompt templates to be used
            - "generic_dirname" (str): The name of the directory, within the "base_path", containing the prompt templates independent of the LLM
			- "file_names" (Dict[str, str]): A dictionary of the file names for each prompt template to be used. It contains:
    
        * "functional" (str): The name of the file containing the prompt template for functions
        * "methodal" (str): The name of the file containing the prompt template for methods
				* "correctional" (str): The name of the file containing the prompt template for corrections
            
            - "placeholders" (Dict[str, Any]): A dictionary containing the descriptions of the prompt placeholders. It contains:
                
                * "start_del" (str): The start delimiter for each placeholder
                * "end_del" (str): The end delimiter for each placeholder
                * "common" (Dict[str, str]): A dictionary of placeholders common to all categories (functional, methodal, correctional) of template prompts used. It contains:

					> "entity": The placeholder (without delimiters) for the entity (function/method)
                    > "module": The placeholder (without delimiters) for the name of the focal module
					> "project": The placeholder (without delimiters) for the name of the target project
                    > "module_path": The placeholder (without delimiters) for the path containing the target module
					> "tsuite_path": The placeholder (without delimiters) for the path containing the test suite
                
                * "correctional" (Dict[str, str]): Dictionary of placeholders for the correctional template prompts used. Contains:

					> "try_num": The placeholder (without delimiters) for the number of correction attempts
					> "error_name": The placeholder (without delimiters) for the name of the error to be corrected
					> "error_mess": The placeholder (without delimiters) for the message of the error to be corrected
					
				* "code" (str): The placeholder (without delimiters) for the focal code in the functional and methodal template prompts used
                * "class_name" (str): The placeholder (without delimiters) for the class name in the methodal template prompts used
	"""
	_PLACEH_PATT: str = r"[A-Za-z0-9_]+"
	
	_OUTER_FIELDS: Set[str] = {
		"base_path", "generic_dirname",
		"file_names", "placeholders"
	}
	_FNAMES_FIELDS: Set[str] = {
		"functional", "methodal", "correctional"
	}
	_PLACEHS_FIELDS: Set[str] = {
		"start_del", "end_del",
		"common", "correctional",
		"code", "class_name"
	}
	
	_COMMON_FIELDS: Set[str] = {
		"entity",
		"module", "project",
		"module_path", "tsuite_path"
	}
	_CORR_FIELDS: Set[str] = {
		"try_num", "error_name", "error_mess"
	}
	
	_SYNT_ERROR: str = 'The path specified by the "{param}" parameter is invalid'
	_NOTEX_ERROR: str = 'The path specified by the "{param}" parameter does not exist'
	_PERM_ERROR: str = 'The path specified by the "{param}" parameter cannot be accessed'
	_UNRE_ERROR: str = 'The path specified by the "{param}" parameter cannot be reached'

	def __init__(
			self,
			config_dict: Dict[str, Any]
	):
		"""
			Creates a new PromptsConfigValidator by providing it with the Python configuration dictionary
            that will be associated with this validator
            
            Parameters
            ----------
				config_dict: Dict[str, Any]
                    A mixed dictionary, indexed by strings, representing the configuration file
                    that was read
			
			Raises
            ------
                ValueError
                    Occurs if:
                    
                        - The provided dictionary is `None`
                        - The provided dictionary is empty
		"""
		super().__init__(config_dict)
		
		self._pathval: PathValidator = PathValidator()
	
	
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		return (self._OUTER_FIELDS, set())
	
	
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		base_path: str = config_read["base_path"]
		generic_dirname: str = config_read["generic_dirname"]
		
		file_names: Dict[str, str] = config_read["file_names"]
		func_fname: str = file_names["functional"]
		meth_fname: str = file_names["methodal"]
		corr_fname: str = file_names["correctional"]
	
		self._assert_path(base_path, "base_path")
		self._assert_path(
			path_join(base_path, generic_dirname),
			"<base_path>/<generic_dirname>"
		)
		
		base_subdirs: List[str] = next(os_walk(base_path, topdown=True))[1]
		for prompt_dir in base_subdirs:
			self._assert_templates(
				path_join(base_path, prompt_dir),
				func_fname, meth_fname, corr_fname
			)
			
		self._assert_placehs(config_read["placeholders"])
	
	
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
	
		
	def _assert_templates(
			self,
			base_path: str,
			func_fname: str,
			meth_fname: str,
			corr_fname: str,
	):
		"""
			Verifies that the prompt template files exist on the operating system
            
            Parameters
            ----------
                base_path: str
                    A string containing the path to the prompts to be verified
					
				func_fname: str
                    A string containing the name of the file with the function prompt template
                    
                meth_fname: str
                    A string containing the name of the file with the method prompt template
					
				corr_fname: str
                    A string containing the name of the file with the prompt template for corrections
            
            Raises
            ------
                InvalidConfigValueError
                    Occurs if, in at least one directory, at least one of the prompt template files
                    does not exist
		"""
		self._assert_path(
			path_join(base_path, func_fname),
			"func_fname"
		)
		self._assert_path(
			path_join(base_path, meth_fname),
			"meth_fname"
		)
		self._assert_path(
			path_join(base_path, corr_fname),
			"corr_fname"
		)
		
		
	@classmethod
	def _assert_placehs(cls, placeholders: Dict[str, Any]):
		placeh_names: List[str] = (list(placeholders["common"].values()) +
		                           list(placeholders["correctional"].values()))
		placeh_names.append(placeholders["code"])
		placeh_names.append(placeholders["class_name"])
		
		if len(set(placeh_names)) != len(placeh_names):
			raise InvalidConfigValueError()
		
		for placeh_name in placeh_names:
			cls._assert_placeh(placeh_name)
		
		
	@classmethod
	def _assert_placeh(cls, placeholder: str):
		"""
			Checks whether a placeholder is a valid string.
            
            If the check succeeds, this operation is equivalent to a no-op.
            
            Raises:
            ------
                InvalidConfigValueError
                    Occurs if the placeholder contains invalid characters
		"""
		is_placeh_valid: bool = reg_search(cls._PLACEH_PATT, placeholder) is not None
		if not is_placeh_valid:
			raise InvalidConfigValueError()