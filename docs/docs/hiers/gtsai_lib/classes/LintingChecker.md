# Class `LintingChecker`
Represents an object capable of performing linting-level validity checks on partial test suites
using a verification tool installed within the focal environment.

Public Class Attributes:
	- `LINTING_TEMP_DIR` (str) : Represents the default name of the temporary directory within the container where files used temporarily during code verification will be stored
	- `LINTING_SCRIPT` (str): Represents the default name of the Python script, located in the directory containing the linting verification tools, which will perform the verification in the focal project environment using the selected tools


!!! abstract "Details"
	- **Fully-qualified Name**: `ptsuite_generation.core.checking.lint_checker.LintingChecker`
	
	


## Public methods

- [**set_focal_project**](../methods/LintingChecker/set_focal_project.md) `( self, project_name: str, full_root: str, env_image: DockerImage, path_prefix: str )`

- [**check_lintically**](../methods/LintingChecker/check_lintically.md) `( self, ptsuite_code: str ) -> Dict[str, str]`

- [**clear_resources**](../methods/LintingChecker/clear_resources.md) `(self, stop_fenv: bool=False)`


