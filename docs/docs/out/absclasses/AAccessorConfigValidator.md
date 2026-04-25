# Abstract class `AAccessorConfigValidator`

Represents an IConfigValidator for the inference platform configuration file to be used.

The configuration file read is a dictionary containing:

* _platform_ (`str`): The name of the inference platform to be used.
* _platform\_options_ (`Dict[str, Any]`): Dictionary containing the inference platform parameters. The contents are related to the inference platform and are specified by the descendants of this abstract class.
* _response\_timeout_ (`int`): The maximum response timeout (in milliseconds).



!!! ext-points "Extension Points"
	
	- The specific inference platform is described by the descendants of this abstract class.
	


!!! abstract "Details"
	- **Fully-qualified Name**: `configuration.config_validator.AAccessorConfigValidator`
	
	
    - **Inherits from:**
		
		- [`IConfigValidator`](../interfaces/IConfigValidator.md)
		
	
	
	



	

## Public methods

- [**\_\_init\_\_**](../methods/IConfigValidator/AAccessorConfigValidator_con.md) `(config_dict: Dict[str, Any]) -> Dict[str, Any]`





## Protected methods

- [**\_ap\_\_assert_purperrors**](../methods/IConfigValidator/_ap__assert_purperrors.md) `(config_dict: Dict[str, Any]) -> Dict[str, Any]`

- [**\_ap\_\_assert_platspec**](../methods/IConfigValidator/_ap__assert_platspec.md) `(config_dict: Dict[str, Any]) -> Dict[str, Any]`

