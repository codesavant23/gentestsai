from typing import Dict, Set, Any, Tuple
from config_io.config_validator._private._a_base_cfgvalidator import _ABaseConfigValidator

from path_validator import (
	PathValidator,
	EPathValidationErrorType
)

from config_io.config_validator.exceptions import (
	InvalidConfigValueError
)



class CacheConfigValidator(_ABaseConfigValidator):
	"""
		Represents an `IConfigValidator` for the configuration file that specifies any caches to be used
        for the "Generation" and "Correction" processes of GenTestsAI.
		
		The configuration file read will consist of a dictionary containing:
            - "caches_type" (str): The implementation technology to use for storage caches
            - "cache_root" (str): The root path containing the caches that will be used
			- "gen_func_cache" (str): If present in the read file, the name of the file containing the cache associated with the "Generation" process (for functions only)
            - "gen_meth_cache" (str): If present in the read file, the name of the file containing the cache associated with the "Generation" process (for methods only)
			- "corr_synt_cache" (str): If present in the read file, the name of the file containing the cache associated with the "Syntax Correction" process
            - "corr_lint_cache" (str): If present in the read file, the name of the file containing the cache associated with the "Linting Correction" process
	"""
	_REQ_FIELDS: Set[str] = {"caches_type", "cache_root"}
	_OPT_FIELDS: Set[str] = {
		"gen_func_cache", "gen_meth_cache",
		"corr_synt_cache", "corr_lint_cache"
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
			Creates a new CacheConfigValidator by providing the path to the configuration file
            that will be associated with this reader
            
            Parameters
            ----------
				config_dict: Dict[str, Any]
                    A mixed dictionary, indexed by strings, representing the
                    read configuration file
			
			Raises
            ------
                ValueError
                    Occurs if:
                    
                        - The provided dictionary has a value of `None`
                        - The provided dictionary is empty
		"""
		super().__init__(config_dict)
		
		self._pathval: PathValidator = PathValidator()
	
	
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		return (self._REQ_FIELDS, self._OPT_FIELDS)
	
	
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		if "caches_type" not in config_read:
			raise InvalidConfigValueError()
		if "cache_root" not in config_read:
			raise InvalidConfigValueError()
		cache_root: str = config_read["cache_root"]
		
		self._assert_path("cache_root", cache_root)
	
	
	def _ap__assert_optional(self, config_read: Dict[str, Any]):
		genf_cache: str = config_read.get("gen_func_cache", None)
		if genf_cache is not None:
			if not isinstance(genf_cache, str):
				self._assert_path("gen_func_cache", genf_cache)
				
		genm_cache: str = config_read.get("gen_meth_cache", None)
		if genm_cache is not None:
			if not isinstance(genm_cache, str):
				self._assert_path("gen_meth_cache", genm_cache)
		
		corrs_cache: str = config_read.get("corr_synt_cache", None)
		if corrs_cache is not None:
			if not isinstance(corrs_cache, str):
				self._assert_path("corr_synt_cache", corrs_cache)
		
		corrl_cache: str = config_read.get("corr_lint_cache", None)
		if corrl_cache is not None:
			if not isinstance(corrl_cache, str):
				self._assert_path("corr_lint_cache", corrl_cache)
	
	
	def _ap__assert_purperrors(self, config_read: Dict[str, Any]):
		return
	

	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _assert_path(
			self,
			param: str,
			path_totest: str
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