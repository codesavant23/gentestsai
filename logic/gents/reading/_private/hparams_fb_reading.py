from typing import Dict, Any

from llm_access.llm_hyperparam.id import ILlmHyperParamId
from llm_access.llm_hyperparam import (
	LlmHyperParamFactoryResolver,
	ILlmHyperParamFactory,
	ILlmHyperParam
)

from logic.utils.process_logger import ProcessLogger



def read_fb_hyperparams(
		platform_name: str,
		def_hparams: Dict[str, Any],
		logger: ProcessLogger = None,
) -> Dict[ILlmHyperParamId, ILlmHyperParam]:
	logger.process_start('Lettura degli iperparametri di fallback ...') \
		if logger is not None else None
	
	## ===== Recupero dei parametri di fallback per ogni modello =====
	platf_hparam_f: ILlmHyperParamFactory = LlmHyperParamFactoryResolver.resolve(platform_name)
	hparam: ILlmHyperParam
	hparams: Dict[ILlmHyperParamId, ILlmHyperParam] = dict()
	
	for param, value in def_hparams.items():
		hparam = platf_hparam_f.create(param)
		hparam.set_value(str(value))
		
		hparams[hparam.param_id()] = hparam
		
	logger.process_end() if logger is not None else None
	return hparams