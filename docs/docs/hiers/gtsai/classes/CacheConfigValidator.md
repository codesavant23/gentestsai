# Class `CacheConfigValidator`
Represents an `IConfigValidator` for the configuration file that specifies any caches to be used
for the "Generation" and "Correction" processes of GenTestsAI.

The configuration file read will consist of a dictionary containing:

	- "caches_type" (str): The implementation technology to use for storage caches
	- "cache_root" (str): The root path containing the caches that will be used
	- "gen_func_cache" (str): If present in the read file, the name of the file containing the cache associated with the "Generation" process (for functions only)
	- "gen_meth_cache" (str): If present in the read file, the name of the file containing the cache associated with the "Generation" process (for methods only)
	- "corr_synt_cache" (str): If present in the read file, the name of the file containing the cache associated with the "Syntax Correction" process
	- "corr_lint_cache" (str): If present in the read file, the name of the file containing the cache associated with the "Linting Correction" process


!!! abstract "Details"
	- **Fully-qualified Name**: `logic.configuration.CacheConfigValidator`
	
    - **Inherits from:**
		
		- _ABaseConfigValidator
		
	
	


## Public methods

- [**_ap__fields**](../methods/CacheConfigValidator/_ap__fields.md) `(self) -> Tuple[Set[str], Set[str]]`

- [**_ap__assert_mandatory**](../methods/CacheConfigValidator/_ap__assert_mandatory.md) `(self, config_read: Dict[str, Any])`

- [**_ap__assert_optional**](../methods/CacheConfigValidator/_ap__assert_optional.md) `(self, config_read: Dict[str, Any])`

- [**_ap__assert_purperrors**](../methods/CacheConfigValidator/_ap__assert_purperrors.md) `(self, config_read: Dict[str, Any])`


