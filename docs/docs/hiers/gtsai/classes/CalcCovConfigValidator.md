# Class `CalcCovConfigValidator`
Represents an `IConfigValidator` for the configuration file containing the options for calculating test suite coverage.

The configuration file read is a dictionary containing:

	- "covconfig_dir" (str): The name of the directory (if any) corresponding to the Cov-config Project Root Path for each target project
	- "covrc_fname" (str): The name of the ".coveragerc" file that will be written by GenTestsAI for coverage.py
	- "pytargs_fname" (str): The name of the JSON file (if present) containing the list of arguments for `pytest`
	- "covargs_fname" (str): The name of the JSON file (if present) containing the list of arguments for `pytest`
	- "calccov_script" (str): The name of the Python script that will perform the coverage calculation within the focal environment


!!! abstract "Details"
	- **Fully-qualified Name**: `logic.configuration.CalcCovConfigValidator`
	
    - **Inherits from:**
		
		- _ABaseConfigValidator
		
	
	


## Public methods

- [**_ap__fields**](../methods/CalcCovConfigValidator/_ap__fields.md) `(self) -> Tuple[Set[str], Set[str]]`

- [**_ap__assert_mandatory**](../methods/CalcCovConfigValidator/_ap__assert_mandatory.md) `(self, config_read: Dict[str, Any])`

- [**_ap__assert_optional**](../methods/CalcCovConfigValidator/_ap__assert_optional.md) `(self, config_read: Dict[str, Any])`

- [**_ap__assert_purperrors**](../methods/CalcCovConfigValidator/_ap__assert_purperrors.md) `(self, config_read: Dict[str, Any])`


