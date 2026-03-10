from logic.ptsuite_generation.llm_access.llm_apiaccessor import (
	ILlmApiAccessor
)
from logic.ptsuite_generation.core.generation import EntityPtsuiteGenerator

from logic.utils.logger import ATemporalFormattLogger



def create_eptsuite_generator(
		platform: ILlmApiAccessor,
		max_gen_tries: int,
		console_logger: ATemporalFormattLogger = None,
) -> EntityPtsuiteGenerator:
	
	ptsuite_gen: EntityPtsuiteGenerator = EntityPtsuiteGenerator(
		max_gen_tries,
		platform,
		console_logger
	)
	
	return ptsuite_gen