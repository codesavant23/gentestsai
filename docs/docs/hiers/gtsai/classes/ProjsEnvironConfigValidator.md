# Class `ProjsEnvironConfigValidator`
Represents an `IConfigValidator` for the configuration file that lists information regarding
the configuration of the target environment for each project for which the selected LLMs will generate tests.

The configuration file read will consist of a dictionary containing the following required entries:

	- "envconfig_dir" (str): The name of the directory (if any) containing the configuration files for the focal environments
	- "image_tag" (str): The Docker 'base' image from which each focal environment image is derived
	- "images_prefix" (str): The prefix to be prepended to the tags of the focal environment images
	- "tools" (Dict[str, str]): A dictionary containing the paths/directories for the tools to be used in each focal environment. It contains:

		* "tools_root" (str): The root path containing the tools to be added within each focal environment
		* "linting" (str): The name of the directory containing the tools to perform linting checks within the focal environment
		* "coverage" (str): The name of the directory containing the tools to calculate code coverage within the focal environment

	- "environ" (Dict[str, str]): A dictionary containing parameters related to the focal environments. It contains:

		* "path_prefix" (str): The base path containing the Full Project Root Path of the focal project within each focal environment
		* "lint_executer" (str): The name of the script that will perform linting within each focal environment
		* "inputctr_dir" (str): The name of the directory, within the "path_prefix", that will be used for file sharing between the focal project and its environment

	- "project" (Dict[str, str]): Dictionary containing parameters related to each focal project. It contains:

		* "dockerfile" (str): The name of the Dockerfile, created by GenTestsAI, that will build the focal environment image
		* "pyversion_file" (str): The name of any text file (in "envconfig_dir") containing the Python interpreter version specific to the project
		* "ext_deps_file" (str): The name of any text file (in "envconfig_dir") containing the non-Python dependencies of the focal project
		* "python_deps_file" (str): The name of the text file (in "envconfig_dir"), if any, containing the Python dependencies of the target project
		* "pre_extdeps_script" (str): The name of the shell script (in "envconfig_dir"), if any, to be executed before installing the non-Python dependencies of the target project
		* "post_extdeps_script" (str): The name of any shell script (in "envconfig_dir") to be executed after the non-Python dependencies of the target project have been installed
		* "pre_pydeps_script" (str): The name of any shell script (in "envconfig_dir") to be executed before installing the Python dependencies of the target project
		* "post_pydeps_script" (str): The name of any shell script (in "envconfig_dir") to be executed after installing the Python dependencies of the target project

and may optionally contain:

	- "pref_contman" (str): The name of the container manager (if any) to which GenTestsAI should be connected for managing the focal environments


!!! abstract "Details"
	- **Fully-qualified Name**: `logic.configuration.ProjsEnvironConfigValidator`
	
    - **Inherits from:**
		
		- _ABaseConfigValidator
		
	
	


## Public methods

- [**_ap__fields**](../methods/ProjsEnvironConfigValidator/_ap__fields.md) `(self) -> Tuple[Set[str], Set[str]]`

- [**_ap__assert_mandatory**](../methods/ProjsEnvironConfigValidator/_ap__assert_mandatory.md) `(self, config_read: Dict[str, Any])`

- [**_ap__assert_optional**](../methods/ProjsEnvironConfigValidator/_ap__assert_optional.md) `(self, config_read: Dict[str, Any])`

- [**_ap__assert_purperrors**](../methods/ProjsEnvironConfigValidator/_ap__assert_purperrors.md) `(self, config_read: Dict[str, Any])`


