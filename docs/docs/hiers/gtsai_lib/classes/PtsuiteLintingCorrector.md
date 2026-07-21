# Class `PtsuiteLintingCorrector`
Represents an object capable of performing correction attempts
on partial test suites, after verifying the correctness of their code
at the linting level.

Public Class Attributes:
	- `GENCODE_PATT` (str) : Represents the default regex pattern to be used to identify the code in the response of a correction attempt


!!! abstract "Details"
	- **Fully-qualified Name**: `ptsuite_generation.core.correction.lint_corrector.PtsuiteLintingCorrector`
	
	


## Public methods

- [**has_corr_terminated**](../methods/PtsuiteLintingCorrector/has_corr_terminated.md) `(self) -> bool`

- [**has_corr_succ**](../methods/PtsuiteLintingCorrector/has_corr_succ.md) `(self) -> bool`

- [**get_lastcorr**](../methods/PtsuiteLintingCorrector/get_lastcorr.md) `(self) -> Tuple[str, int]`

- [**start_new_correction**](../methods/PtsuiteLintingCorrector/start_new_correction.md) `( self, ptsuite_code: str, resp_timeout: int )`

- [**perform_corr_try**](../methods/PtsuiteLintingCorrector/perform_corr_try.md) `(self) -> str`

- [**stop_correction**](../methods/PtsuiteLintingCorrector/stop_correction.md) `(self)`


