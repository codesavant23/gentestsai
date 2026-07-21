# Abstract class `_ABaseFocalEnvConfigurator`
Represents a basic `IFocalEnvConfigurator`, containing the logic common
to every `IFocalEnvConfigurator`.

Public Class Attributes:
	- `PATH_PREFIX` (str): The default prefix of the path, within the Docker container, to which the contents of the focal project will be mounted to make it accessible within the container.


!!! ext-points "Extension Points"
	
	- The installed version of `pylint` is specified by the descendants of this abstract class.
	
	- The installed version of `coverage.py` is specified by the descendants of this abstract class.
	
	- The package of additional software installed, independent of the focal project, is specified
	
	- by the descendants of this abstract class
	

!!! abstract "Details"
	- **Fully-qualified Name**: `focalproj_configuration.focal_env.focalenv_configurator._ABaseFocalEnvConfigurator`
	
    - **Inherits from:**
		
		- IFocalEnvConfigurator
		
	
	


## Public methods

- [**set_default_pyversion**](../methods/_ABaseFocalEnvConfigurator/set_default_pyversion.md) `(self, python_version: str)`

- [**set_focal_project**](../methods/_ABaseFocalEnvConfigurator/set_focal_project.md) `( self, proj_name: str, full_root: str, focal_root: str, tests_root: str )`

- [**set_path_prefix**](../methods/_ABaseFocalEnvConfigurator/set_path_prefix.md) `(self, path_prefix: str)`

- [**build_image**](../methods/_ABaseFocalEnvConfigurator/build_image.md) `( self, wants_dockign: bool = True ) -> DockerImage`

- [**_ap__pylint_version**](../methods/_ABaseFocalEnvConfigurator/_ap__pylint_version.md) `(self) -> str`

- [**_ap__covpy_version**](../methods/_ABaseFocalEnvConfigurator/_ap__covpy_version.md) `(self) -> str`

- [**_p__install_extra_softws**](../methods/_ABaseFocalEnvConfigurator/_p__install_extra_softws.md) `(self, dockf_builder: ATransactDockfBuilder)`


