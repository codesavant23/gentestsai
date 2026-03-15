from typing import Tuple

from logic.utils.prompt_builder import PromptBuilder
from logic.ptsuite_generation.llm_access.llm_chat import ILlmChat

from logic.ptsuite_generation.core.checking.synt_checker import ISyntacticChecker
from logic.ptsuite_generation.core.correction.synt_corrector import PtsuiteSyntacticCorrector

from logic.ptsuite_generation.cache_accessor import IPtsuiteCacheAccessor

from logic.utils.logger import ATemporalFormattLogger



def correct_syntactically(
		project_name: str, cache_modname: str,
		model: str,
		entityname_comps: Tuple[str, str],
		wrong_ptsuite_code: str,
		entity_corr_pbder: PromptBuilder,
		error_placehs: Tuple[str, str, str],
		syntcorr_comps: Tuple[PtsuiteSyntacticCorrector, ISyntacticChecker],
		chat: ILlmChat,
		max_tries: int,
		resp_timeout: int,
		corr_cache: IPtsuiteCacheAccessor,
		logger: ATemporalFormattLogger,
		cache_entprefix: str = ""
):
	entity, entity_placeh = entityname_comps
	name_placeh, message_placeh, trynum_placeh = error_placehs
	synt_corr, synt_chker = syntcorr_comps
	
	error: Tuple[str, str]
	full_prompt: str
	
	try_num: int = 1
	tries_incache: int = 0
	
	ptsuite_code: str = wrong_ptsuite_code
	
	# Ricerca di una test-suite parziale corretta sintatticamente nella cache
	while try_num <= max_tries:
		if corr_cache.does_ptsuite_exists(
				project_name,
				cache_modname, f"{cache_entprefix}{entity}", model, try_num
		):
			ptsuite_code = corr_cache.get_ptsuite(
				project_name, cache_modname, f"{cache_entprefix}{entity}", model, try_num
			)
			logger.log(f"Test-suite parziale trovata nella cache "
			           f"(Tentativo di correzione: {try_num}/{max_tries})")
			
			error = synt_chker.check_synt(ptsuite_code)
			# Se la richiesta di quella test-suite parziale non aveva fallito
			# e la test-suite parziale è corretta
			if (len(error) == 0) and (ptsuite_code != ""):
				logger.log(f"Test-suite parziale corretta sintatticamente ottenuta! "
			           f"(Tentativo funzionante: {try_num}/{max_tries})")
				return ptsuite_code
			tries_incache += 1
		try_num += 1
	
	# Se non si è trovata una test-suite parziale corretta nella cache
	is_corr_success: bool = False
	try_num = 1
	synt_corr.start_new_correction(wrong_ptsuite_code, resp_timeout)
	while (
			(not synt_corr.has_corr_terminated()) and
	        (try_num <= (max_tries-tries_incache)) and
			(not is_corr_success)
	):
		error = synt_chker.check_synt(ptsuite_code)
		
		# Se si sono ci sono errori di correttezza sintattica
		if len(error) > 0:
			# Impostazione dell' errore nel prompt
			entity_corr_pbder.set_placeholder(name_placeh, error[0])
			entity_corr_pbder.set_placeholder(message_placeh, error[1])
			entity_corr_pbder.set_placeholder(trynum_placeh, str(try_num+tries_incache))
			
			# Calcolo del full prompt
			full_prompt = entity_corr_pbder.build_prompt()
			
			# Aggiunta della richiesta di correzione alla chat
			chat.add_prompt(full_prompt)
			# Esecuzione del tentativo di correzione
			ptsuite_code = synt_corr.perform_corr_try()
			
			# Se c'è stato un errore legato alla richiesta al LLM
			# allora si imposta una test-suite parziale vuota
			if ptsuite_code is None:
				ptsuite_code = ""
			
			# Registrazione del tentativo nella cache di correzione
			logger.log("Salvataggio nella cache ... ")
			corr_cache.register_ptsuite(
				project_name,
				cache_modname, f"{cache_entprefix}{entity}", model, (try_num+tries_incache),
				ptsuite_code
			)
			logger.log("Test-suite parziale salvata!")
			
			try_num += 1
		else:
			is_corr_success = True
			break
			
	# Se la serie di tentativi del correttore sintattico non è terminata
	# (perchè il max numero di tentativi sono stati in parte effettuati tramite cache)
	if not synt_corr.has_corr_terminated():
		synt_corr.stop_correction()
	else:
		# Se invece tutti i tentativi sono stati effettuati dal correttore sintattico
		# allora si và a conoscere lo stato di successo della serie di tentativi terminata
		is_corr_success = synt_corr.has_corr_succ()
	
	# Se la correzione ha avuto successo
	if is_corr_success:
		# allora viene restituito il codice della test-suite parziale corretta
		return ptsuite_code
	else:
		return None