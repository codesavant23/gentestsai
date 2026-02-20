from typing import List, Tuple

from logic.utils.prompt_builder import PromptBuilder
from logic.ptsuite_generation.llm_access.llm_chat import ILlmChat

from logic.ptsuite_generation.core.generation import EntityPtsuiteGenerator

from logic.ptsuite_generation.core.checking.synt_checker import ISyntacticChecker
from logic.ptsuite_generation.core.correction.synt_corrector import ISyntCorrector

from logic.ptsuite_generation.core.checking.lint_checker import LintingChecker
from logic.ptsuite_generation.core.correction.lint_corrector import PtsuiteLintingCorrector

from logic.ptsuite_generation.core.tests_skipping import ISkipWriter
from logic.ptsuite_generation.cache_accessor import IPtsuiteCacheAccessor

from .calculating_ptsuite_name import calculate_ptsuite_name
from .generate import generate_ptsuite
from .synt_correction import correct_syntactically
from .lint_correction import correct_lintically



def generate_correct_ebye(
		project_name: str, model: str,
		module_path: str,
		entities_name: List[str],
		prompt_builders: Tuple[PromptBuilder, PromptBuilder],
		entity_placeh: str,
		corr_placehs: Tuple[str, str, str],
		ptsuite_gen: EntityPtsuiteGenerator,
		ptsuite_corrs: Tuple[ISyntCorrector, PtsuiteLintingCorrector],
		ptsuite_chkers: Tuple[ISyntacticChecker, LintingChecker],
		chat: ILlmChat,
		max_tries: Tuple[int, int], resp_timeout: int,
		skipd_writers: Tuple[ISkipWriter, ISkipWriter],
		caches: Tuple[IPtsuiteCacheAccessor, IPtsuiteCacheAccessor, IPtsuiteCacheAccessor],
		entityprefix_comps: Tuple[str, str, str] = tuple()
):
	entity_gen_pbder, entity_corr_pbder = prompt_builders
	synt_corr, lint_corr = ptsuite_corrs
	synt_chker, lint_chker = ptsuite_chkers
	max_gen_tries, max_corr_tries = max_tries
	ent_gen_skipw, ent_corr_skipw = skipd_writers
	gen_cache, corrs_cache, corrl_cache = caches
	entity_prefix: str = ""
	entity_promptsep: str = ""
	entity_filesep: str = ""
	if len(entityprefix_comps) != 0:
		entity_prefix, entity_promptsep, entity_filesep = entityprefix_comps
	
	entity_name: str
	ptsuite_code: str
	ptsuite_fname: str
	
	i: int = 0
	while i < len(entities_name):
		entity_name = entities_name[i]
		# Calcolo del nome della test-suite parziale
		ptsuite_fname = calculate_ptsuite_name(entity_name, f"{entity_prefix}{entity_filesep}")
		
		# ===== Processo di "Generazione della test-suite parziale" =====
		entity_gen_pbder.set_placeholder(entity_placeh, entity_name)
		ptsuite_code = generate_ptsuite(
			project_name, model,
		    entity_gen_pbder.build_prompt(),
			ptsuite_gen, chat,
			max_gen_tries, resp_timeout,
			gen_cache
		)
		# Se la generazione non ha avuto successo
		if ptsuite_code is None:
			# si dichiara saltata l' entità
			ent_gen_skipw.write_skipd_test(entity_name)
			# e si passa alla prossima entità
			i += 1
			continue
		
		# ===== Processo di "Correzione Sintattica della test-suite parziale" =====
		entity_corr_pbder.set_placeholder(entity_placeh, entity_name)
		ptsuite_code = correct_syntactically(
			project_name, model,
			(entity_name, entity_placeh),
			ptsuite_code,
			entity_corr_pbder,
			corr_placehs,
			(synt_corr, synt_chker), chat,
			max_corr_tries, resp_timeout,
			corrs_cache,
			cache_entprefix = f"{entity_prefix}{entity_promptsep}"
		)
		# Se la correzione sintattica non ha avuto successo
		if ptsuite_code is None:
			# si dichiara saltata l' entità
			ent_corr_skipw.write_skipd_test(entity_name)
			# e si passa alla prossima entità
			i += 1
			continue
		
		# ===== Processo di "Correzione a livello di Linting della test-suite parziale" =====
		ptsuite_code = correct_lintically(
			project_name, model,
			(entity_name, entity_placeh),
			ptsuite_code,
			entity_corr_pbder,
			corr_placehs,
			(lint_corr, lint_chker), chat,
			max_corr_tries, resp_timeout,
			corrl_cache,
			cache_entprefix = f"{entity_prefix}{entity_promptsep}"
		)
		# Se la correzione a livello di linting non ha avuto successo
		if ptsuite_code is None:
			# si dichiara saltata l' entità
			ent_corr_skipw.write_skipd_test(entity_name)
			# e si passa alla prossima entità
			i += 1
			continue
			
		# Sennò se nessuno dei casi precedenti è avvenuto allora la test-suite parziale
		# è stata generata e viene dichiarata corretta.
		# Viene quindi scritta all' interno del suo file che la rappresenta
		with(f"{module_path}/{ptsuite_fname}", "w") as fptsuite:
			fptsuite.write(ptsuite_code)
			fptsuite.flush()
		
		i += 1