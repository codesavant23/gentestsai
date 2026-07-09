from typing import Dict, Set, Tuple, Any
from abc import abstractmethod
from .._a_platspec_cfgvalidator import _APlatSpecConfigValidator

from config_io.config_validator.exceptions import InvalidConfigValueError



class AModelsConfigValidator(_APlatSpecConfigValidator):
	"""
		Represents an `IConfigValidator` for the configuration file that lists the Large Language Models
        used in the generation and correction evaluation of the tests.
        
        The configuration file read is a dictionary containing:
        
            -   A dictionary entry for each model, where the key is the model's name.
				The dictionary optionally contains:
            
                    * "temperature" (float): The value for the "Temperature" parameter for that model
                    * "gen_seed" (int): The generation seed value for that model
					* "top-k" (int): The value of the "Top-K" parameter for that model
                    * "top-p" (float): The value of the "Top-P" parameter for that model
                    * "context_window" (int): The value for the context window size of that model
					* "think" (bool): The value specifying whether to use the model's thinking (if it has one)
                    * The other keys depend on the specific inference platform to which it relates
                
        The specific inference platform is described by the descendants of this abstract class
	"""
	
	_OPT_FIELDS_NOPLAT: Set[str] = {
		"temperature", "gen_seed",
		"top-k", "top-p",
		"context_window",
		"think",
	}
	
	def __init__(
			self,
			config_dict: Dict[str, Any]
	):
		"""
			Creates a new AModelsConfigValidator by providing it with the Python configuration
			dictionary that will be associated with this validator
            
            Parameters
            ----------
				config_dict: Dict[str, Any]
                    A mixed dictionary, indexed by strings, representing the read
                    configuration file
			
			Raises
            ------
                ValueError
                    Occurs if:
                    
                        - The provided dictionary has a value of `None`
                        - The provided dictionary is empty
		"""
		super().__init__(config_dict)
	
	
	def _ap__fields(self) -> Tuple[Set[str], Set[str]]:
		return (set(), set())
	
	
	def _p__efields_strict(self) -> bool:
		return False
	
	
	def _ap__assert_mandatory(self, config_read: Dict[str, Any]):
		return
	
	
	def _ap__assert_optional(self, config_read: Dict[str, Any]):
		temp: float
		gen_seed: int
		top_k: int
		top_p: float
		ctx_window: int
		think: bool
		
		for llm_name, llm_params in config_read.items():
			temp = llm_params.get("temperature", None)
			self._pf__assert_validtype("temperature", temp, float, llm_name)
			
			gen_seed = llm_params.get("gen_seed", None)
			self._pf__assert_validtype("gen_seed", gen_seed, int, llm_name)
			
			top_k = llm_params.get("top-k", None)
			self._pf__assert_validtype("top-k", top_k, int, llm_name)
			
			top_p = llm_params.get("top-p", None)
			self._pf__assert_validtype("top-p", top_p, float, llm_name)
			
			ctx_window = llm_params.get("context_window", None)
			self._pf__assert_validtype("context_window", ctx_window, int, llm_name)
			
			think = llm_params.get("think", None)
			self._pf__assert_validtype("think", think, bool, llm_name)
	
	
	def _ap__assert_purperrors(self, config_read: Dict[str, Any]):
		return
	
	
	def _pf__assert_validtype(
			self,
			param_name: str,
			param: Any,
			expected_type: type,
			model_name: str,
	):
		"""
			Checks whether a model parameter is of the correct type.
            
            If the check succeeds, this operation is equivalent to a no-op.
            
            Parameters
            ----------
				param_name: str
                    A string containing the parameter name in the Python configuration dictionary
            
                param: Any
                    Any value representing the parameter to be tested
                    the type
					
				expected_type: type
                    A type representing the expected type of the provided parameter
                    
                model_name: str
                    A string containing the name of the model to which the parameter belongs
		"""
		if (param is not None) and (not isinstance(param, expected_type)):
			raise InvalidConfigValueError(
				f"The type of the {param_name} parameter is invalid (contained in the {model_name} template)"
			)
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__assert_platspec(self, config_read: Dict[str, Any]):
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================