# Abstract class `_ABasePtsuiteCacheAccessor`
Represents a base `IPtsuiteCacheAccessor`, meaning it contains the logic common to all
`IPtsuiteCacheAccessor` instances.


!!! ext-points "Extension Points"
	
	- The cache implementation technology is specified by the subclasses of this abstract class.
	
	- The purpose of the cache is specified by the subclasses of this abstract class.
	

!!! abstract "Details"
	- **Fully-qualified Name**: `ptsuite_generation.cache_accessor._ABasePtsuiteCacheAccessor`
	
    - **Inherits from:**
		
		- IPtsuiteCacheAccessor
		
	
	


## Public methods

- [**close**](../methods/_ABasePtsuiteCacheAccessor/close.md) `(self)`

- [**create_projspace**](../methods/_ABasePtsuiteCacheAccessor/create_projspace.md) `(self, proj_name: str)`

- [**register_ptsuite**](../methods/_ABasePtsuiteCacheAccessor/register_ptsuite.md) `( self, proj_name: str, module_name: str, entity: str, model: str, try_num: int, ptsuite_code: str )`

- [**get_ptsuite**](../methods/_ABasePtsuiteCacheAccessor/get_ptsuite.md) `( self, proj_name: str, module_name: str, entity: str, model: str, try_num: int ) -> str`

- [**_pf__get_cache_path**](../methods/_ABasePtsuiteCacheAccessor/_pf__get_cache_path.md) `(self) -> str`

- [**_p__file_extension**](../methods/_ABasePtsuiteCacheAccessor/_p__file_extension.md) `(self) -> str`

- [**_P__objinit**](../methods/_ABasePtsuiteCacheAccessor/_P__objinit.md) `(self)`

- [**_ap__read_project_spaces**](../methods/_ABasePtsuiteCacheAccessor/_ap__read_project_spaces.md) `(self) -> Set[str]`

- [**_ap__create_new_cache**](../methods/_ABasePtsuiteCacheAccessor/_ap__create_new_cache.md) `(self, cache_path: str)`

- [**_ap__assert_cache_type**](../methods/_ABasePtsuiteCacheAccessor/_ap__assert_cache_type.md) `(self, cache_path: str)`

- [**_ap__create_projspace_spec**](../methods/_ABasePtsuiteCacheAccessor/_ap__create_projspace_spec.md) `(self, proj_name: str)`

- [**_ap__register_ptsuite_spec**](../methods/_ABasePtsuiteCacheAccessor/_ap__register_ptsuite_spec.md) `(self, proj_name: str, module_name: str, entity: str, model: str, try_num: int, ptsuite_code: str )`

- [**_ap__get_ptsuite_spec**](../methods/_ABasePtsuiteCacheAccessor/_ap__get_ptsuite_spec.md) `( self, proj_name: str, module_name: str, entity: str, model: str, try_num: int ) -> str`

- [**does_ptsuite_exists**](../methods/_ABasePtsuiteCacheAccessor/does_ptsuite_exists.md) `( self, proj_name: str, module_name: str, entity: str, model: str, try_num: int ) -> bool`


