from typing import Dict, Tuple, List

# ============ Path Utilities ============ #
from os.path import (
	join as path_join,
	split as path_split,
	splitext as path_split_ext,
)
# ======================================== #

from main_execs.gents.mbym import generate_correct_ebye

from logic.ptsuite_generation.cache_accessor import IPtsuiteCacheAccessor

from logic.ptsuite_generation.decls_extraction.moddecls_extractor import AMutableModuleDeclsExtractor
from logic.ptsuite_generation.decls_extraction.classdecls_extractor import IClassDeclsExtractor

from logic.utils.prompt_builder import PromptBuilder

from logic.ptsuite_generation.llm_access.llm_apiaccessor import ILlmApiAccessor
from logic.ptsuite_generation.llm_access.llm_chat import ILlmChat
from logic.ptsuite_generation.core.generation import EntityPtsuiteGenerator

from logic.ptsuite_generation.core.checking.synt_checker import ISyntacticChecker
from logic.ptsuite_generation.core.correction.synt_corrector import PtsuiteSyntacticCorrector

from logic.ptsuite_generation.core.checking.lint_checker import LintingChecker
from logic.ptsuite_generation.core.correction.lint_corrector import PtsuiteLintingCorrector

from logic.ptsuite_generation.core.tests_skipping import (
	ISkipWriter,
	SkipWriterFactory, ESkippedTestsFtypeFormat
)

from logic.utils.logger import ATemporalFormattLogger
from logic.utils.process_logger import ProcessLogger



def generate_correct_mbym(
		project_name: str, model: str,
		module_path: str,
		moddecl_extr: AMutableModuleDeclsExtractor,
		gen_comps: Tuple[
			EntityPtsuiteGenerator,
			ILlmApiAccessor, ILlmChat
		],
		corr_comps: Tuple[PtsuiteSyntacticCorrector, PtsuiteLintingCorrector],
		chk_comps: Tuple[ISyntacticChecker, LintingChecker],
		max_tries: Tuple[int, int],
		resp_timeout: int,
		prompting: Tuple[
			Tuple[PromptBuilder, PromptBuilder, PromptBuilder],
			Dict[str, str]
		],
		gen_caches: Tuple[IPtsuiteCacheAccessor, IPtsuiteCacheAccessor],
		corr_caches: Tuple[IPtsuiteCacheAccessor, IPtsuiteCacheAccessor],
		skipping: Tuple[
			str, Tuple[str, str, str, str]
		],
		gents_logger: ProcessLogger,
		logger: ATemporalFormattLogger,
):
	"""
		TODO: Contract ||
	"""
	module_dirpath, module_fname = path_split(module_path)
	module_name: str = path_split_ext(module_fname)[0]
	ptsuite_gen, platform, chat = gen_comps
	prompt_bders, placehs = prompting
	func_pbder, meth_pbder, corr_pbder = prompt_bders
	
	genf_cache, genm_cache = gen_caches
	corrs_cache, corrl_cache = corr_caches
	
	# ===== Creazione degli scrittori dei tests saltati =====
	skipd_ftype, skipd_fnames = skipping
	(skipd_genf_fname, skipd_genm_fname,
	 skipd_corrf_fname, skipd_corrm_fname) = skipd_fnames
	skipd_ftype_e: ESkippedTestsFtypeFormat = ESkippedTestsFtypeFormat[
		skipd_ftype.replace("-","_").upper()
	]
	genf_skipw: ISkipWriter = SkipWriterFactory.create(skipd_ftype_e, path_join(module_dirpath, skipd_genf_fname))
	genm_skipw: ISkipWriter = SkipWriterFactory.create(skipd_ftype_e, path_join(module_dirpath, skipd_genm_fname))
	corrf_skipw: ISkipWriter = SkipWriterFactory.create(skipd_ftype_e, path_join(module_dirpath, skipd_corrf_fname))
	corrm_skipw: ISkipWriter = SkipWriterFactory.create(skipd_ftype_e, path_join(module_dirpath, skipd_corrm_fname))
	
	gents_logger.process_start(f"Inizio fenerazione test-suite del modulo \"{module_name}\" ...")
	logger.set_messages_sep("\n\t\t\t\t")
	gents_logger.process_start(f"Estrazione del codice focale del modulo ...")
	# ===== Lettura ed estrazione del codice focale =====
	with open(module_path, "r") as fmodule:
		moddecl_extr.set_module_code(fmodule.read())
	func_names: List[str] = moddecl_extr.extract_funcs()
	clss: List[IClassDeclsExtractor] = moddecl_extr.extract_classes()
	gents_logger.process_end()
	
	ptsuite_code: str
	
	func_pbder.set_placeholder(placehs["project"], project_name)
	func_pbder.set_placeholder(placehs["module"], module_name)
	
	# ===== Processo di "Generazione e Correzione delle test-suite parziali delle funzioni" =====
	logger.log("Inizio generazione delle test-suites parziali delle funzioni ...")
	logger.set_messages_sep("\n\t\t\t\t\t")
	generate_correct_ebye(
		project_name, model,
		module_dirpath,
		func_names,
		(func_pbder, corr_pbder),
		placehs["entity"],
		(placehs["error_name"], placehs["error_mess"], placehs["try_num"]),
		ptsuite_gen,
		corr_comps, chk_comps,
		chat,
		max_tries, resp_timeout,
		(genf_skipw, corrf_skipw),
		(genf_cache, corrs_cache, corrl_cache),
	)
	logger.set_messages_sep("\n\t\t\t\t")
	logger.log("Fine generazione delle test-suites parziali delle funzioni")
	
	# ===== Processo di "Generazione e Correzione delle test-suite parziali dei metodi" =====
	meth_pbder.set_placeholder(placehs["project"], project_name)
	meth_pbder.set_placeholder(placehs["module"], module_name)
	logger.log(f"Inizio generazione delle test-suites parziali dei metodi ...")
	logger.set_messages_sep("\n\t\t\t\t\t")
	for cls in clss:
		logger.log(f"Classe: {cls.class_name()}")
		logger.set_messages_sep("\n\t\t\t\t\t\t")
		meth_pbder.set_placeholder(placehs["class_name"], cls.class_name())
		generate_correct_ebye(
			project_name, model,
			module_dirpath,
			cls.method_names(),
			(meth_pbder, corr_pbder),
			placehs["entity"],
			(placehs["error_name"], placehs["error_mess"], placehs["try_num"]),
			ptsuite_gen,
			corr_comps, chk_comps,
			chat,
			max_tries, resp_timeout,
			(genm_skipw, corrm_skipw),
			(genm_cache, corrs_cache, corrl_cache),
			entityprefix_comps=(cls.class_name(), "$", ".")
		)
		logger.set_messages_sep("\n\t\t\t\t\t")
	logger.set_messages_sep("\n\t\t\t\t")
	logger.log("Fine generazione delle test-suites parziali dei metodi")
	
	logger.set_messages_sep("\n\t\t\t")
	logger.log(f"Fine generazione test-suite del modulo \"{module_name}\" ...")