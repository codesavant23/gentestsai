# Class `OllamaAccessorConfigValidator`
Represents an `AAccessorConfigValidator` for the inference platform
named "Ollama".

The platform-specific fields are:

	- In "platform_options":

		* "api_addr" (str): The address (as a pair, separated by ":", with port) of the Ollama server to use
		* "userpass_pair" (str): The username and password pair (separated by ":") to use on the Ollama server
		* "connect_timeout" (int): The maximum wait timeout for connecting to the Ollama server (in milliseconds)


!!! abstract "Details"
	- **Fully-qualified Name**: `logic.configuration.accessor_validators.OllamaAccessorConfigValidator`
	
    - **Inherits from:**
		
		- AAccessorConfigValidator
		
	
	


## Public methods

- [**_ap__assert_purperrors**](../methods/OllamaAccessorConfigValidator/_ap__assert_purperrors.md) `(self, config_read: Dict[str, Any])`

- [**_ap__assert_platspec**](../methods/OllamaAccessorConfigValidator/_ap__assert_platspec.md) `( self, config_read: Dict[str, Any] )`


