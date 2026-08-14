# Class `PromptsConfigValidator`
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


!!! abstract "Details"
	- **Fully-qualified Name**: `logic.configuration.PromptsConfigValidator`
	
    - **Inherits from:**
		
		- _ABaseConfigValidator
		
	
	


## Public methods

- [**_ap__fields**](../methods/PromptsConfigValidator/_ap__fields.md) `(self) -> Tuple[Set[str], Set[str]]`

- [**_ap__assert_mandatory**](../methods/PromptsConfigValidator/_ap__assert_mandatory.md) `(self, config_read: Dict[str, Any])`

- [**_ap__assert_optional**](../methods/PromptsConfigValidator/_ap__assert_optional.md) `(self, config_read: Dict[str, Any])`

- [**_ap__assert_purperrors**](../methods/PromptsConfigValidator/_ap__assert_purperrors.md) `(self, config_read: Dict[str, Any])`


