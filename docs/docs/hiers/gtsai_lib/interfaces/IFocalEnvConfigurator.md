# Interface `IFocalEnvConfigurator`
Represents an object capable of configuring an environment for the execution/testing of a
focus project.

Each focus environment is primarily used for:

	- Verifying the correctness, at the linting level, of the partial test suites of the specific focus project to which the image is linked
	- Calculating the coverage of both sets of test suites (human and LLM)


!!! ext-points "Extension Points"
	
	- The installed version of `pylint` is specified by the descendants of this abstract class.
	
	- The installed version of `coverage.py` is specified by the descendants of this abstract class.
	

!!! abstract "Details"
	- **Fully-qualified Name**: `focalproj_configuration.focal_env.focalenv_configurator.IFocalEnvConfigurator`
	
	


## Public methods

- [**set_default_pyversion**](../methods/IFocalEnvConfigurator/set_default_pyversion.md) `(self, python_version: str)`

- [**set_focal_project**](../methods/IFocalEnvConfigurator/set_focal_project.md) `( self, proj_name: str, full_root: str, focal_root: str, tests_root: str )`

- [**set_path_prefix**](../methods/IFocalEnvConfigurator/set_path_prefix.md) `(self, path_prefix: str)`

- [**build_image**](../methods/IFocalEnvConfigurator/build_image.md) `( self, wants_dockign: bool = True ) -> DockerImage`


