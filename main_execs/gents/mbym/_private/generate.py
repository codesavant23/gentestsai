from logic.ptsuite_generation.core.generation import EntityPtsuiteGenerator
from logic.ptsuite_generation.core.exceptions import WrongResponseFormatError

from logic.ptsuite_generation.llm_access.llm_chat import ILlmChat

from logic.ptsuite_generation.cache_accessor import IPtsuiteCacheAccessor

from logic.utils.logger import ATemporalFormattLogger



def generate_ptsuite(
		project_name: str, cache_modname: str,
		model: str,
		entity: str,
		full_prompt: str,
		ptsuite_gen: EntityPtsuiteGenerator,
		chat: ILlmChat,
		max_tries: int,
		resp_timeout: int,
		gen_cache: IPtsuiteCacheAccessor,
		logger: ATemporalFormattLogger,
		cache_entprefix: str = "",
) -> str:
	ptsuite_code: str = None
	try_num: int = max_tries
	tries_incache: int
	
	# Ricerca di una test-suite parziale generata senza errori nella richiesta
	while (try_num >= 1):
		if gen_cache.does_ptsuite_exists(
				project_name,
				cache_modname, f"{cache_entprefix}{entity}", model, try_num
		):
			ptsuite_code = gen_cache.get_ptsuite(
				project_name, cache_modname, f"{cache_entprefix}{entity}", model, try_num
			)
			
			logger.log(f"Test-suite parziale trovata nella cache "
			           f"(Tentativo di generazione: {try_num}/{max_tries})")
			
			if ptsuite_code != "":
				return ptsuite_code
		try_num -= 1
	
	tries_incache = max_tries - try_num
	try_num = 1
	ptsuite_gen.start_new_generation(resp_timeout)
	while (
			(not ptsuite_gen.has_gen_terminated()) and
			(try_num <= (max_tries-tries_incache))
	):
		# Aggiunta della richiesta di generazione alla chat
		chat.add_prompt(full_prompt)
		# Esecuzione del tentativo di generazione
		try:
			ptsuite_code = ptsuite_gen.perform_gen_try()
		except WrongResponseFormatError:
			ptsuite_code = None
		
		# Se c'è stato un errore legato alla richiesta al LLM
		# allora si imposta una test-suite parziale vuota
		if ptsuite_code is None:
			ptsuite_code = ""

		# Registrazione del tentativo nella cache di correzione
		logger.log("Salvataggio nella cache ... ")
		gen_cache.register_ptsuite(
			project_name,
			cache_modname, f"{cache_entprefix}{entity}", model, try_num+tries_incache,
			ptsuite_code
		)
		logger.log("Test-suite parziale salvata!")
		
		try_num += 1
		
	if not ptsuite_gen.has_gen_terminated():
		ptsuite_gen.stop_generation()
		
	if ptsuite_code == "":
		ptsuite_code = None

	return ptsuite_code