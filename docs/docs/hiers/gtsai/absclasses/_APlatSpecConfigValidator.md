# Abstract class `_APlatSpecConfigValidator`
Represents an `IConfigValidator` for configuration files whose scope defines fields related to a specific platform.


!!! ext-points "Extension Points"
	
	- The scope of the validated configuration file is specified by the descendants of this abstract class.
	
	- The specific inference platform is described by the descendants of this abstract class.
	

!!! abstract "Details"
	- **Fully-qualified Name**: `logic.configuration._APlatSpecConfigValidator`
	
    - **Inherits from:**
		
		- _ABaseConfigValidator
		
	
	


## Public methods

- [**validate_sem**](../methods/_APlatSpecConfigValidator/validate_sem.md) `(self)`

- [**_ap__assert_platspec**](../methods/_APlatSpecConfigValidator/_ap__assert_platspec.md) `(self, config_read: Dict[str, Any])`

- [**_ap__fields**](../methods/_APlatSpecConfigValidator/_ap__fields.md) `(self) -> Tuple[Set[str], Set[str]]`

- [**_ap__assert_mandatory**](../methods/_APlatSpecConfigValidator/_ap__assert_mandatory.md) `(self, config_read: Dict[str, Any])`

- [**_ap__assert_optional**](../methods/_APlatSpecConfigValidator/_ap__assert_optional.md) `(self, config_read: Dict[str, Any])`

- [**_ap__assert_purperrors**](../methods/_APlatSpecConfigValidator/_ap__assert_purperrors.md) `(self, config_read: Dict[str, Any])`


