from typing import Tuple, Dict

from logic.utils.prompt_builder import PromptBuilder
from logic.ptsuite_generation.llm_access.llm_chat import ILlmChat

from logic.ptsuite_generation.core.checking.lint_checker import LintingChecker
from logic.ptsuite_generation.core.correction.lint_corrector import PtsuiteLintingCorrector

from logic.ptsuite_generation.cache_accessor import IPtsuiteCacheAccessor

from logic.utils.logger import ATemporalFormattLogger



def correct_lintically(
		project_name: str, cache_modname: str,
		model: str,
		entityname_comps: Tuple[str, str],
		wrong_ptsuite_code: str,
		entity_corr_pbder: PromptBuilder,
		error_placehs: Tuple[str, str, str],
		lintcorr_comps: Tuple[PtsuiteLintingCorrector, LintingChecker],
		chat: ILlmChat,
		max_tries: int,
		resp_timeout: int,
		corr_cache: IPtsuiteCacheAccessor,
		logger: ATemporalFormattLogger,
		cache_entprefix: str = "",
):
	entity, entity_placeh = entityname_comps
	name_placeh, message_placeh, trynum_placeh = error_placehs
	lint_corr, lint_chker = lintcorr_comps
	
	error: Dict[str, str]
	error_mess: str = "{error_mess} (at line {line} and column {column})"
	full_prompt: str
	
	line: str
	column: str
	
	try_num: int = 1
	tries_incache: int = 0
	
	ptsuite_code: str = wrong_ptsuite_code
	
	# Ricerca di una test-suite parziale corretta a livello di linting nella cache
	while try_num < max_tries:
		if corr_cache.does_ptsuite_exists(
				project_name,
				cache_modname, f"{cache_entprefix}{entity}", model, try_num
		):
			ptsuite_code = corr_cache.get_ptsuite(
				project_name, cache_modname, f"{cache_entprefix}{entity}", model, try_num
			)
			logger.log(f"Test-suite parziale trovata nella cache "
			           f"(Tentativo di correzione: {try_num}/{max_tries})")
			
			error = lint_chker.check_lintically(ptsuite_code)
			if len(error) == 0:
				logger.log(f"Test-suite parziale corretta a livello di linting ottenuta! "
			           f"(Tentativo funzionante: {try_num}/{max_tries})")
				return ptsuite_code
			tries_incache += 1
		try_num += 1
	
	# Se non si è trovata una test-suite parziale corretta nella cache
	is_corr_success: bool = False
	try_num = 1
	lint_corr.start_new_correction(wrong_ptsuite_code, resp_timeout)
	while (
		   (not lint_corr.has_corr_terminated()) and
	       (try_num <= (max_tries-tries_incache)) and
	       (not is_corr_success)
	):
		error = lint_chker.check_lintically(ptsuite_code)
		# Se si sono ci sono errori di correttezza a livello di linting
		if len(error) > 0:
			# Impostazione dell' errore nel prompt
			line, column = error["except_pos"].split(";")
			entity_corr_pbder.set_placeholder(name_placeh, error["except_name"])
			entity_corr_pbder.set_placeholder(
				message_placeh, error_mess.format(
					error_mess=error["except_mess"],
					line=line,
					column=column
				),
			)
			entity_corr_pbder.set_placeholder(trynum_placeh, str(try_num+tries_incache))
				
			# Calcolo del full prompt
			full_prompt = entity_corr_pbder.build_prompt()
			
			# Aggiunta della richiesta di correzione alla chat
			chat.add_prompt(full_prompt)
			# Esecuzione del tentativo di correzione
			ptsuite_code = lint_corr.perform_corr_try()
			
			# Registrazione del tentativo nella cache di correzione
			logger.log("Salvataggio nella cache ... ")
			corr_cache.register_ptsuite(
				project_name,
				cache_modname, f"{cache_entprefix}{entity}", model, try_num+tries_incache,
				ptsuite_code
			)
			logger.log("Test-suite parziale salvata!")
			
			try_num += 1
		else:
			is_corr_success = True
			break
	
	# Se la serie di tentativi del correttore di linting non è terminata
	# (perchè il max numero di tentativi sono stati in parte effettuati tramite cache)
	if not lint_corr.has_corr_terminated():
		lint_corr.stop_correction()
	else:
		# Se invece tutti i tentativi sono stati effettuati dal correttore di linting
		# allora si và a conoscere lo stato di successo della serie di tentativi terminata
		is_corr_success = lint_corr.has_corr_succ()
	
	# Se la correzione ha avuto successo
	if is_corr_success:
		# allora viene restituito il codice della test-suite parziale corretta
		return ptsuite_code
	else:
		return None