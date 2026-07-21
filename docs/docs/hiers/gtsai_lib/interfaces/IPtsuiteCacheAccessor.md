# Interface `IPtsuiteCacheAccessor`
Represents an object that provides access to a cache of partial test suites resulting
from a process that uses Large Language Models.
Each entry in the cache is an attempt to generate, using an LLM, a working partial test suite.

Every `IPtsuiteCacheAccessor` supports Python's "Context Manager".


!!! ext-points "Extension Points"
	
	- The cache implementation technology is specified by the descendants of this interface.
	

!!! abstract "Details"
	- **Fully-qualified Name**: `ptsuite_generation.cache_accessor.IPtsuiteCacheAccessor`
	
	


## Public methods

- [**close**](../methods/IPtsuiteCacheAccessor/close.md) `(self)`

- [**create_projspace**](../methods/IPtsuiteCacheAccessor/create_projspace.md) `(self, proj_name: str)`

- [**register_ptsuite**](../methods/IPtsuiteCacheAccessor/register_ptsuite.md) `( self, proj_name: str, module_name: str, entity: str, model: str, try_num: int, ptsuite_code: str )`

- [**does_ptsuite_exists**](../methods/IPtsuiteCacheAccessor/does_ptsuite_exists.md) `( self, proj_name: str, module_name: str, entity: str, model: str, try_num: int, ) -> bool`

- [**get_ptsuite**](../methods/IPtsuiteCacheAccessor/get_ptsuite.md) `( self, proj_name: str, module_name: str, entity: str, model: str, try_num: int ) -> str`


