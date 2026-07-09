# Abstract class `ATransactDockfBuilder`
Represents a "transactional" `IDockfBuilder`, meaning it allows you to write
shell command transactions (multiple shell commands executed within a single `RUN` layer).


!!! ext-points "Extension Points"
	
	- The implementation technology for storing instructions is specified by the
	
	- descendants of this abstract class
	

!!! abstract "Details"
	- **Fully-qualified Name**: `focalproj_configuration.dockerfile_builder.ATransactDockfBuilder`
	
    - **Inherits from:**
		
		- _ABaseDockfBuilder
		
	
	


## Public methods

- [**begin_cmds_tran**](../methods/ATransactDockfBuilder/begin_cmds_tran.md) `(self)`

- [**add_shellcmd_step**](../methods/ATransactDockfBuilder/add_shellcmd_step.md) `( self, shell_cmd: str )`

- [**commit_cmds_tran**](../methods/ATransactDockfBuilder/commit_cmds_tran.md) `(self)`

- [**build_dockerfile**](../methods/ATransactDockfBuilder/build_dockerfile.md) `(self, dockf_path: str)`

- [**_ap__new_dockerf_spec**](../methods/ATransactDockfBuilder/_ap__new_dockerf_spec.md) `(self)`

- [**_ap__add_instr**](../methods/ATransactDockfBuilder/_ap__add_instr.md) `(self, instr: str)`

- [**_ap__get_dockf_body**](../methods/ATransactDockfBuilder/_ap__get_dockf_body.md) `(self) -> str`


