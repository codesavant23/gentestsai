from typing import Tuple

from logic.utils.prompt_builder import PromptBuilder
from logic.ptsuite_generation.llm_access.llm_chat import ILlmChat

from logic.ptsuite_generation.core.checking.synt_checker import ISyntacticChecker
from logic.ptsuite_generation.core.correction.synt_corrector import PtsuiteSyntacticCorrector

from logic.ptsuite_generation.cache_accessor import IPtsuiteCacheAccessor



def correct_syntactically(
		project_name: str, model: str,
		entityname_comps: Tuple[str, str],
		wrong_ptsuite_code: str,
		entity_corr_pbder: PromptBuilder,
		error_placehs: Tuple[str, str, str],
		syntcorr_comps: Tuple[PtsuiteSyntacticCorrector, ISyntacticChecker],
		chat: ILlmChat,
		max_tries: int,
		resp_timeout: int,
		corr_cache: IPtsuiteCacheAccessor,
		cache_entprefix: str = ""
):
	entity_name, entity_placeh = entityname_comps
	name_placeh, message_placeh, trynum_placeh = error_placehs
	synt_corr, synt_chker = syntcorr_comps
	
	error: Tuple[str, str]
	full_prompt: str
	
	try_num: int = 1
	llm_trynum: int = 1
	ptsuite_code: str = wrong_ptsuite_code
	
	synt_corr.start_new_correction(wrong_ptsuite_code, resp_timeout)
	while (not synt_corr.has_corr_terminated()) and (try_num <= max_tries):
		error = synt_chker.check_synt(ptsuite_code)
		# Se si sono ci sono errori di correttezza sintattica
		if len(error) > 0:
			# Impostazione dell' errore nel prompt
			entity_corr_pbder.set_placeholder(name_placeh, error[0])
			entity_corr_pbder.set_placeholder(message_placeh, error[1])
			entity_corr_pbder.set_placeholder(trynum_placeh, str(llm_trynum))
			
			# Se il tentativo di correzione non è mai stato effettuato
			entity_corr_pbder.set_placeholder(entity_placeh, f"{cache_entprefix}{entity_name}")
			full_prompt = entity_corr_pbder.build_prompt()
			if not corr_cache.does_ptsuite_exists(project_name, full_prompt, model, try_num):
				
				# Si re-imposta il nome dell' entità nel prompt
				entity_corr_pbder.set_placeholder(entity_placeh, entity_name)
				full_prompt = entity_corr_pbder.build_prompt()
				
				# Aggiunta della richiesta di correzione alla chat
				chat.add_prompt(full_prompt)
				# Esecuzione del tentativo di correzione
				ptsuite_code = synt_corr.perform_corr_try()
				
				# Registrazione del tentativo nella cache di correzione
				# (si antepone il prefisso dell' entità nella cache)
				entity_corr_pbder.set_placeholder(entity_placeh, f"{cache_entprefix}{entity_name}")
				full_prompt = entity_corr_pbder.build_prompt()
				corr_cache.register_ptsuite(project_name, full_prompt, model, try_num, ptsuite_code)
				
				# Incremento dei tentativi da parte del LLM
				llm_trynum += 1
			else:
				# Recupero del tentativo di correzione dalla cache di test-suites parziali
				ptsuite_code = corr_cache.get_ptsuite(project_name, full_prompt, model, try_num)
			try_num += 1
		else:
			break
	
	# Se la serie di tentativi di correzione ha avuto successo (essendo stata effettuata)
	# o se è stata recuperata dalla cache una test-suite parziale sintatticamente corretta
	is_corr_success: bool = (synt_corr.has_corr_succ()) or (synt_chker.check_synt(ptsuite_code))
	if is_corr_success:
		# allora viene restituito il codice della test-suite parziale
		# sintatticamente corretta
		return ptsuite_code
	else:
		return None