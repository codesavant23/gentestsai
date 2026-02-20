from logic.ptsuite_generation.core.generation import EntityPtsuiteGenerator
from logic.ptsuite_generation.llm_access.llm_chat import ILlmChat

from logic.ptsuite_generation.cache_accessor import IPtsuiteCacheAccessor



def generate_ptsuite(
		project_name: str, model: str,
		full_prompt: str,
		ptsuite_gen: EntityPtsuiteGenerator,
		chat: ILlmChat,
		max_tries: int,
		resp_timeout: int,
		gen_cache: IPtsuiteCacheAccessor
) -> str:
	ptsuite_code: str = None
	try_num: int = 1
	
	while try_num < max_tries:
		if gen_cache.does_ptsuite_exists(project_name, full_prompt, model, try_num):
			ptsuite_code = gen_cache.get_ptsuite(project_name, full_prompt, model, try_num)
			break
		try_num += 1
	
	if ptsuite_code is None:
		ptsuite_gen.start_new_generation(resp_timeout)
		while not ptsuite_gen.has_gen_terminated():
			# Aggiunta della richiesta di generazione alla chat
			chat.add_prompt(full_prompt)
			# Esecuzione del tentativo di generazione
			ptsuite_gen.perform_gen_try()
		
		# Se la generazione ha avuto successo
		if ptsuite_gen.has_gen_succ():
			# Viene salvato il codice della test-suite parziale generata
			ptsuite_code, try_num = ptsuite_gen.get_lastgen()
			# e memorizzato nella cache di generazione
			gen_cache.register_ptsuite(project_name, full_prompt, model, try_num, ptsuite_code)

	return ptsuite_code