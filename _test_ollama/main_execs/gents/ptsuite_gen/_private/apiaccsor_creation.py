from typing import Dict, Any

from logic.ptsuite_generation.llm_access.llm_apiaccessor import (
	ILlmApiAccessor, LlmApiAccessorFactory
)

from logic.utils.logger import ATemporalFormattLogger



def inst_apiaccsor(
		platform_name: str,
		platf_options: Dict[str, Any],
		logger: ATemporalFormattLogger = None,
) -> ILlmApiAccessor:
	platform: ILlmApiAccessor = None
	match platform_name:
		case "ollama":
			platform = LlmApiAccessorFactory.for_ollama(
				platf_options["address"], platf_options["userpass_pair"],
				platf_options["connect_timeout"],
				logger, (True if logger else False)
			)
		case _:
			raise NotImplementedError("La piattaforma di inferenza richiesta non è implementata")
	
	return platform