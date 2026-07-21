# Interface `ISkipWriter`
Represents a writer of files containing skipped tests during the generation or correction
phase by an LLM.


!!! ext-points "Extension Points"
	
	- The file type of the skipped tests is specified by the descendants of this interface.
	
	- The file format of the skipped tests is specified by the descendants of this interface.
	

!!! abstract "Details"
	- **Fully-qualified Name**: `ptsuite_generation.core.tests_skipping.ISkipWriter`
	
	


## Public methods

- [**write_skipd_test**](../methods/ISkipWriter/write_skipd_test.md) `( self, entity_name: str )`


