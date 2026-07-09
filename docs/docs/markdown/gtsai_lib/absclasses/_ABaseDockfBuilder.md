# Abstract class `_ABaseDockfBuilder`
Represents a base `IDockfBuilder`, containing the control logic common
to every `IDockfBuilder`


!!! ext-points "Extension Points"
	
	- The implementation technology for storing instructions is specified by the descendants
	
	- of this abstract class
	

!!! abstract "Details"
	- **Fully-qualified Name**: `focalproj_configuration.dockerfile_builder._ABaseDockfBuilder`
	
    - **Inherits from:**
		
		- IDockfBuilder
		
	
	


## Public methods

- [**new_dockerfile**](../methods/_ABaseDockfBuilder/new_dockerfile.md) `(self)`

- [**set_base_image**](../methods/_ABaseDockfBuilder/set_base_image.md) `(self, base_image: str)`

- [**add_shell**](../methods/_ABaseDockfBuilder/add_shell.md) `(self, shell_touse: str, args: List[str] = None)`

- [**add_copy**](../methods/_ABaseDockfBuilder/add_copy.md) `(self, sources: List[str], dest: str)`

- [**set_global_args**](../methods/_ABaseDockfBuilder/set_global_args.md) `(self, global_args: Dict[str, str])`

- [**set_envvar**](../methods/_ABaseDockfBuilder/set_envvar.md) `(self, var_name: str, value: str)`

- [**add_shellcmd**](../methods/_ABaseDockfBuilder/add_shellcmd.md) `(self, shell_cmd: str)`

- [**add_workdir**](../methods/_ABaseDockfBuilder/add_workdir.md) `(self, dest: str)`

- [**set_entrypoint**](../methods/_ABaseDockfBuilder/set_entrypoint.md) `( self, entry_cmd: str, def_args: List[str] = None )`

- [**build_dockerfile**](../methods/_ABaseDockfBuilder/build_dockerfile.md) `( self, dockf_path: str )`

- [**_ap__new_dockerf_spec**](../methods/_ABaseDockfBuilder/_ap__new_dockerf_spec.md) `(self)`

- [**_ap__add_instr**](../methods/_ABaseDockfBuilder/_ap__add_instr.md) `(self, instr: str)`

- [**_ap__get_dockf_body**](../methods/_ABaseDockfBuilder/_ap__get_dockf_body.md) `(self) -> str`


