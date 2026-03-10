from typing import Tuple, Dict

# ============ Path Utilities ============ #
from os.path import join as path_join
# ======================================== #

from logic.ptsuite_generation.cache_accessor import (
	IPtsuiteCacheAccessor,
	PtsuiteCacheAccessorFactory,
	ECacheAccessorType
)

from logic.utils.process_logger import ProcessLogger



def open_ptsuite_caches(
		caches_tech: str,
		caches_root: str,
		caches_names: Dict[str, str],
		logger: ProcessLogger = None
) -> Tuple[
	IPtsuiteCacheAccessor, IPtsuiteCacheAccessor,
	IPtsuiteCacheAccessor, IPtsuiteCacheAccessor
]:
	logger.process_start('Creazione/Apertura delle caches per le test-suites parziali ...') if logger is not None else None
	
	caches_tech: ECacheAccessorType = ECacheAccessorType[
		caches_tech.upper()
	]
	
	genf_cache: IPtsuiteCacheAccessor = None
	if caches_names.get("gen_func_cache", None) is not None:
		genf_cache = PtsuiteCacheAccessorFactory.create(
			caches_tech,
		    path_join(caches_root, caches_names["gen_func_cache"])
		)
		
	genm_cache: IPtsuiteCacheAccessor = None
	if caches_names.get("gen_meth_cache", None) is not None:
		genm_cache = PtsuiteCacheAccessorFactory.create(
			caches_tech,
		    path_join(caches_root, caches_names["gen_meth_cache"])
		)
		
	corrs_cache: IPtsuiteCacheAccessor = None
	if caches_names.get("corr_synt_cache", None) is not None:
		corrs_cache = PtsuiteCacheAccessorFactory.create(
			caches_tech,
		    path_join(caches_root, caches_names["corr_synt_cache"])
		)
		
	corrl_cache: IPtsuiteCacheAccessor = None
	if caches_names.get("corr_lint_cache", None) is not None:
		corrl_cache = PtsuiteCacheAccessorFactory.create(
			caches_tech,
		    path_join(caches_root, caches_names["corr_lint_cache"])
		)
		
	logger.process_end() if logger is not None else None
	return (genf_cache, genm_cache, corrs_cache, corrl_cache)