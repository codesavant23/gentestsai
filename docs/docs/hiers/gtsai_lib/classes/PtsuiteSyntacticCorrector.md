# Class `PtsuiteSyntacticCorrector`
Represents an object capable of performing correction attempts syntactic correction
on partial test suites by requesting it from an LLM.

Public Class Attributes:
	- `GENCODE_PATT` (str) : Represents the default regex pattern to be used to identify the code in the response of a correction attempt


!!! abstract "Details"
	- **Fully-qualified Name**: `ptsuite_generation.core.correction.synt_corrector.PtsuiteSyntacticCorrector`
	
	


## Public methods

- [**has_corr_terminated**](../methods/PtsuiteSyntacticCorrector/has_corr_terminated.md) `(self) -> bool`

- [**has_corr_succ**](../methods/PtsuiteSyntacticCorrector/has_corr_succ.md) `(self) -> bool`

- [**get_lastcorr**](../methods/PtsuiteSyntacticCorrector/get_lastcorr.md) `(self) -> str`

- [**start_new_correction**](../methods/PtsuiteSyntacticCorrector/start_new_correction.md) `( self, ptsuite_code: str, resp_timeout: int )`

- [**perform_corr_try**](../methods/PtsuiteSyntacticCorrector/perform_corr_try.md) `(self) -> str`

- [**stop_correction**](../methods/PtsuiteSyntacticCorrector/stop_correction.md) `(self)`


