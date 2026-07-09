# Interface `IDockfBuilder`
Represents an object capable of building Dockerfiles incrementally.
Upon instantiation of each IDockfBuilder, it is already initialized to begin the
incremental construction of the first Dockerfile.


!!! ext-points "Extension Points"
	
	- The implementation technology for storing instructions is specified by the
	
	- implementers of this interface
	

!!! abstract "Details"
	- **Fully-qualified Name**: `focalproj_configuration.dockerfile_builder.IDockfBuilder`
	
	


## Public methods

- [**new_dockerfile**](../methods/IDockfBuilder/new_dockerfile.md) `(self)`

- [**set_base_image**](../methods/IDockfBuilder/set_base_image.md) `(self, base_image: str)`

- [**set_envvar**](../methods/IDockfBuilder/set_envvar.md) `(self, var_name: str, value: str)`

- [**add_shell**](../methods/IDockfBuilder/add_shell.md) `( self, shell_touse: str, args: List[str]=None )`

- [**add_shellcmd**](../methods/IDockfBuilder/add_shellcmd.md) `(self, shell_cmd: str)`

- [**set_global_args**](../methods/IDockfBuilder/set_global_args.md) `(self, global_args: Dict[str, str])`

- [**add_copy**](../methods/IDockfBuilder/add_copy.md) `(self, sources: List[str], dest: str)`

- [**add_workdir**](../methods/IDockfBuilder/add_workdir.md) `(self, dest: str)`

- [**set_entrypoint**](../methods/IDockfBuilder/set_entrypoint.md) `( self, entry_cmd: str, def_args: List[str]=None )`

- [**build_dockerfile**](../methods/IDockfBuilder/build_dockerfile.md) `( self, dockf_path: str, )`


