# Abstract class `AModelsConfigValidator`
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


!!! ext-points "Extension Points"
	
	- The specific inference platform is described by the descendants of this abstract class
	

!!! abstract "Details"
	- **Fully-qualified Name**: `logic.configuration.models_validators.AModelsConfigValidator`
	
    - **Inherits from:**
		
		- _APlatSpecConfigValidator
		
	
	


## Public methods

- [**_ap__fields**](../methods/AModelsConfigValidator/_ap__fields.md) `(self) -> Tuple[Set[str], Set[str]]`

- [**_p__efields_strict**](../methods/AModelsConfigValidator/_p__efields_strict.md) `(self) -> bool`

- [**_ap__assert_mandatory**](../methods/AModelsConfigValidator/_ap__assert_mandatory.md) `(self, config_read: Dict[str, Any])`

- [**_ap__assert_optional**](../methods/AModelsConfigValidator/_ap__assert_optional.md) `(self, config_read: Dict[str, Any])`

- [**_ap__assert_purperrors**](../methods/AModelsConfigValidator/_ap__assert_purperrors.md) `(self, config_read: Dict[str, Any])`

- [**_pf__assert_validtype**](../methods/AModelsConfigValidator/_pf__assert_validtype.md) `( self, param_name: str, param: Any, expected_type: type, model_name: str, )`

- [**_ap__assert_platspec**](../methods/AModelsConfigValidator/_ap__assert_platspec.md) `(self, config_read: Dict[str, Any])`


