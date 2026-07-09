# Class `Sqlite3CacheAccessor`
Represents an `IPtsuiteCacheAccessor` that uses a local
SQLite3 database as its cache


!!! abstract "Details"
	- **Fully-qualified Name**: `ptsuite_generation.cache_accessor.Sqlite3CacheAccessor`
	
    - **Inherits from:**
		
		- _ABasePtsuiteCacheAccessor
		
	
	


## Public methods

- [**close**](../methods/Sqlite3CacheAccessor/close.md) `(self)`

- [**does_ptsuite_exists**](../methods/Sqlite3CacheAccessor/does_ptsuite_exists.md) `( self, proj_name: str, module_name: str, entity: str, model: str, try_num: int ) -> bool`

- [**_ap__create_new_cache**](../methods/Sqlite3CacheAccessor/_ap__create_new_cache.md) `(self, cache_path: str)`

- [**_ap__read_project_spaces**](../methods/Sqlite3CacheAccessor/_ap__read_project_spaces.md) `(self) -> Set[str]`

- [**_ap__create_projspace_spec**](../methods/Sqlite3CacheAccessor/_ap__create_projspace_spec.md) `(self, proj_name: str)`

- [**_ap__register_ptsuite_spec**](../methods/Sqlite3CacheAccessor/_ap__register_ptsuite_spec.md) `( self, proj_name: str, module_name: str, entity: str, model: str, try_num: int, ptsuite_code: str )`

- [**_ap__get_ptsuite_spec**](../methods/Sqlite3CacheAccessor/_ap__get_ptsuite_spec.md) `(self, proj_name: str, module_name: str, entity: str, model: str, try_num: int) -> str`

- [**_ap__assert_cache_type**](../methods/Sqlite3CacheAccessor/_ap__assert_cache_type.md) `(self, cache_path: str)`


