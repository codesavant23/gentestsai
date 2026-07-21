# Interface `ISyntacticChecker`
Represents an object capable of verifying the syntactic correctness of a partial test suite
using a verification tool.


!!! ext-points "Extension Points"
	
	- The verification tool is specified by the descendants of this interface.
	

!!! abstract "Details"
	- **Fully-qualified Name**: `ptsuite_generation.core.checking.synt_checker.ISyntacticChecker`
	
	


## Public methods

- [**check_synt**](../methods/ISyntacticChecker/check_synt.md) `( self, ptsuite_code: str ) -> Tuple[str, str]`

- [**clear_resources**](../methods/ISyntacticChecker/clear_resources.md) `(self)`


