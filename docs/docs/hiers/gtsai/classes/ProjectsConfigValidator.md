# Class `ProjectsConfigValidator`
Represents an `IConfigValidator` for the configuration file of the focal projects for which tests will be generated.

The configuration file read is a dictionary containing:

	-   A dictionary entry for each focal project, whose key is the project name.
		Each dictionary must contain:

			* "full_root" (str): The Full Project Root Path of the project (as an absolute path)
			* "focal_root" (str): The Focal Project Root Path of the project (as a path relative to the Full Project Root Path)
			* "tests_root" (str): The Tests Project Root Path of the project (as a path relative to the Full Project Root Path)

		and may optionally contain:

			* "focal_excluded" (List[str]): A list of paths relative to the Focal Project Root Path, which should not be considered part of the focal code
			* "tests_excluded" (List[str]): A list of paths relative to the Tests Project Root Path, which should not be considered part of the entire project's test suite


!!! abstract "Details"
	- **Fully-qualified Name**: `logic.configuration.ProjectsConfigValidator`
	
    - **Inherits from:**
		
		- _ABaseConfigValidator
		
	
	


## Public methods

- [**_p__efields_strict**](../methods/ProjectsConfigValidator/_p__efields_strict.md) `(self) -> bool`

- [**_ap__fields**](../methods/ProjectsConfigValidator/_ap__fields.md) `(self) -> Tuple[Set[str], Set[str]]`

- [**_ap__assert_mandatory**](../methods/ProjectsConfigValidator/_ap__assert_mandatory.md) `(self, config_read: Dict[str, Any])`

- [**_ap__assert_optional**](../methods/ProjectsConfigValidator/_ap__assert_optional.md) `(self, config_read: Dict[str, Any])`

- [**_ap__assert_purperrors**](../methods/ProjectsConfigValidator/_ap__assert_purperrors.md) `(self, config_read: Dict[str, Any])`


