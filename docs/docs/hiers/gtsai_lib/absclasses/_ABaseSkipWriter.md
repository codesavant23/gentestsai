# Abstract class `_ABaseSkipWriter`
Represents a base `ISkipWriter` that contains the logic common to all `ISkipWriter`s.


!!! ext-points "Extension Points"
	
	- The file type for skipped tests is specified by the descendants of this abstract class.
	
	- The file format for skipped tests is specified by the descendants of this abstract class.
	

!!! abstract "Details"
	- **Fully-qualified Name**: `ptsuite_generation.core.tests_skipping._ABaseSkipWriter`
	
    - **Inherits from:**
		
		- ISkipWriter
		
	
	


## Public methods

- [**_p__file_extension**](../methods/_ABaseSkipWriter/_p__file_extension.md) `(self) -> str`

- [**_pf__get_skipdf_path**](../methods/_ABaseSkipWriter/_pf__get_skipdf_path.md) `(self) -> str`

- [**_P__objinit**](../methods/_ABaseSkipWriter/_P__objinit.md) `(self)`

- [**_ap__assert_skipdtests_file**](../methods/_ABaseSkipWriter/_ap__assert_skipdtests_file.md) `( self, skipdtests_path: str )`

- [**_ap__init_skipdtests_file**](../methods/_ABaseSkipWriter/_ap__init_skipdtests_file.md) `( self, skipdtests_path: str )`

- [**write_skipd_test**](../methods/_ABaseSkipWriter/write_skipd_test.md) `(self, entity_name: str)`


