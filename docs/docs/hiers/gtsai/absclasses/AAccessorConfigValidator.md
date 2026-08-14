# Abstract class `AAccessorConfigValidator`
Represents an `IConfigValidator` for the configuration file of the inference platform to be used.

The configuration file read is a dictionary containing:

	- "platform" (str): The name of the inference platform to use
	- "platform_options" (Dict[str, Any]): A dictionary containing the inference platform parameters.
	  Its contents are specific to the inference platform and are specified by the subclasses
	  of this abstract class.
	- "response_timeout" (int): The maximum wait timeout for receiving a response (in milliseconds)


!!! ext-points "Extension Points"
	
	- The specific inference platform is described by the subclasses of this abstract class
	

!!! abstract "Details"
	- **Fully-qualified Name**: `logic.configuration.accessor_validators.AAccessorConfigValidator`
	
    - **Inherits from:**
		
		- _APlatSpecConfigValidator
		
	
	


## Public methods

- [**_ap__fields**](../methods/AAccessorConfigValidator/_ap__fields.md) `(self) -> Tuple[Set[str], Set[str]]`

- [**_ap__assert_mandatory**](../methods/AAccessorConfigValidator/_ap__assert_mandatory.md) `(self, config_read: Dict[str, Any])`

- [**_ap__assert_optional**](../methods/AAccessorConfigValidator/_ap__assert_optional.md) `(self, config_read: Dict[str, Any])`

- [**_ap__assert_platspec**](../methods/AAccessorConfigValidator/_ap__assert_platspec.md) `(self, config_read: Dict[str, Any])`

- [**_ap__assert_purperrors**](../methods/AAccessorConfigValidator/_ap__assert_purperrors.md) `(self, config_read: Dict[str, Any])`


