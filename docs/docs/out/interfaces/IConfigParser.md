# Interface `IConfigParser`

Represents a parser of GenTestsAI configuration files written in a specific type and format.

The category of configuration files that can be read by each IConfigParser are configuration files that can be represented as a Python dictionary (with any-type values) indexed by strings.



!!! ext-points "Extension Points"
	
	- The type of the configuration file read (e.g. JSON, XML, etc.).
	


!!! abstract "Details"
	- **Fully-qualified Name**: `configuration.config_parser.IConfigParser`
	
	
	
	



	

## Public methods

- [**read_config**](../methods/IConfigParser/read_config.md) `(self, cfgfile_path: str) -> Dict[str, Any]`




