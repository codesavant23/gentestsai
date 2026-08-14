# Interface `IPlatSpecCfgValidatorFactory`
Represents a factory for each `IConfigValidator`, which represents
a configuration file associated with a specific inference platform


!!! ext-points "Extension Points"
	
	- The purpose of the validatable configuration file is specified by the descendants of this interface.
	

!!! abstract "Details"
	- **Fully-qualified Name**: `logic.configuration.IPlatSpecCfgValidatorFactory`
	
	


## Public methods

- [**create**](../methods/IPlatSpecCfgValidatorFactory/create.md) `( self, config_platf: EImplementedPlatform, config_dict: Dict[str, Any] ) -> IConfigValidator`


