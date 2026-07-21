# Class `EntityPtsuiteGenerator`
Represents an object capable of instructing an LLM to generate a partial test suite,
relating to a single autonomous entity.

Public Class Attributes:
	- `GENCODE_PATT` (str) : Represents the default regex pattern to be used to identify the code in the response to a generation attempt


!!! abstract "Details"
	- **Fully-qualified Name**: `ptsuite_generation.core.generation.EntityPtsuiteGenerator`
	
	


## Public methods

- [**has_gen_terminated**](../methods/EntityPtsuiteGenerator/has_gen_terminated.md) `(self) -> bool`

- [**has_gen_succ**](../methods/EntityPtsuiteGenerator/has_gen_succ.md) `(self) -> bool`

- [**get_lastgen**](../methods/EntityPtsuiteGenerator/get_lastgen.md) `(self) -> Tuple[str, int]`

- [**start_new_generation**](../methods/EntityPtsuiteGenerator/start_new_generation.md) `( self, resp_timeout: int )`

- [**perform_gen_try**](../methods/EntityPtsuiteGenerator/perform_gen_try.md) `(self) -> str`

- [**stop_generation**](../methods/EntityPtsuiteGenerator/stop_generation.md) `(self)`


