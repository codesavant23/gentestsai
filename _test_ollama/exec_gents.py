# TODO: (Secondario) Finire di sistemare tutti gli Spazi con i TAB in ogni file
from typing import Dict, List, Tuple, Set, Any

# =========== ArgParse Utilities =========== #
from argparse import Namespace as ArgumentsList
# ========================================== #
# ============ Path Utilities ============ #
from os.path import (
	sep as path_sep,
	altsep as path_altsep,
	join as path_join,
	split as path_split,
	dirname as path_getdir,
	abspath as path_absolute,
	relpath as path_relative,
	commonpath as path_intersect
)
# ======================================== #
# ============== OS Utilities ============== #
from sys import stdout as os_stdout
from os import (
	walk as os_walk,
	makedirs as os_mkdirs
)
from os.path import (
	exists as os_fdexists
)
from shutil import rmtree as os_dremove
# ========================================== #
# ============== Docker SDK Utilities =============== #
from docker.models.images import Image as DockerImage
# =================================================== #

from logic.variability import EImplementedPlatform, ESpecLlmImpl
from logic.variability.combinatorial import EPlatformCombo

from main_execs.gents import read_arguments
from main_execs.gents.mbym import (
	calculate_prompt_relpaths,
	generate_correct_mbym
)

from main_execs.gents.reading import read_fallback_templprompts, read_1model_templprompts
from main_execs.gents import normalize_llmname

from main_execs import read_config_files
from logic.configuration.config_parser import (
	IConfigParser,
	ConfigParserFactory, EParserFiletype
)

from logic.utils.prompt_builder import PromptBuilder

from logic.ptsuite_generation.decls_extraction.moddecls_extractor import (
	AMutableModuleDeclsExtractor, TreeSitterModuleDeclsExtractor
)

from main_execs.gents.reading import read_fb_hyperparams
from logic.ptsuite_generation.llm_access.llm_hyperparam import (
	LlmHyperParamFactoryResolver,
	ILlmHyperParamFactory,
	ILlmHyperParam
)

from logic.ptsuite_generation.llm_access.llm_specimpl import (
	ILlmSpecImpl,
	ILlmSpecImplFactory, LlmSpecImplFactoryResolver
)

from logic.ptsuite_generation.llm_access.llm_chat import (
	ILlmChat, LlmChatFactory, ELlmChatApis
)

from main_execs.gents.ptsuite_gen import inst_apiaccsor
from logic.ptsuite_generation.llm_access.llm_apiaccessor import ILlmApiAccessor

from main_execs.gents.ptsuite_gen import create_eptsuite_generator
from logic.ptsuite_generation.core.generation import EntityPtsuiteGenerator

from logic.ptsuite_generation.core.checking.synt_checker import (
	ISyntacticChecker,
	SyntacticCheckerFactory, ESyntCheckerTool
)
from logic.ptsuite_generation.core.checking.lint_checker import LintingChecker
from logic.ptsuite_generation.core.correction.synt_corrector import PtsuiteSyntacticCorrector
from logic.ptsuite_generation.core.correction.lint_corrector import PtsuiteLintingCorrector

from main_execs.gents import create_focal_images

from main_execs.gents.ptsuite_gen import open_ptsuite_caches

from logic.utils.logger import (
	ATemporalFormattLogger, ConsoleTemporalFormattLogger
)
from logic.utils.process_logger import ProcessLogger


SCRIPT_PATH: str = path_getdir(path_absolute(__file__))
LOG_FORMAT: str = "{message} ({day}/{month}/{year} {hour}:{min}:{second})"



if __name__ == "__main__":
	gents_args: ArgumentsList = read_arguments(SCRIPT_PATH)
	
	## =================================================
	## ===== Processo di "Configurazione iniziale" =====
	## =================================================
	
	## ===== Creazione del logger da utilizzare per la generazione delle test-suites =====
	console_logger: ATemporalFormattLogger = ConsoleTemporalFormattLogger(os_stdout)
	console_logger.set_messages_sep("\n")
	console_logger.set_format(LOG_FORMAT)
	logger: ProcessLogger = ProcessLogger(console_logger, "\n")

	console_logger.log('Software "exec_gents.py" avviato')
	
	## ===== Lettura dei files di configurazione =====
	logger.process_start('Lettura dei files di configurazione ...')
	
	config_parser: IConfigParser = ConfigParserFactory.create(
		EParserFiletype[gents_args.config_type.upper()]
	)
	configs: Dict[str, Dict[str, Any]] = read_config_files(
		gents_args.config_root,
		config_parser,
		EImplementedPlatform[gents_args.platform.upper()],
		file_names=(
			gents_args.platform_config,
			gents_args.general_config,
			gents_args.models_config,
			gents_args.projects_config,
			gents_args.projsenv_config,
			gents_args.prompts_config
		)
	)
	platf_config: Dict[str, Any] = configs["platform"]
	general_config: Dict[str, Any] = configs["general"]
	models_config: Dict[str, Any] = configs["models"]
	projs_config: Dict[str, Any] = configs["projects"]
	projsenv_config: Dict[str, Any] = configs["environ"]
	prompts_config: Dict[str, Any] = configs["prompts"]
	caches_config: Dict[str, Any] = configs["caches"]
	
	logger.process_end()
	
	## ===== Creazione/Stabilimento delle caches di memorizzazione delle test-suites parziali =====
	keys_topick: Set[str] = {"gen_func_cache", "gen_meth_cache", "corr_synt_cache", "corr_lint_cache"}
	keys_topick = keys_topick.intersection(caches_config.keys())
	caches_names: Dict[str, str] = {key: caches_config[key] for key in keys_topick}
	
	genf_cache, genm_cache, corrs_cache, corrl_cache = open_ptsuite_caches(
		caches_config["caches_type"],
		caches_config["cache_root"], caches_names,
		logger
	)
	
	## ===== Creazione delle immagini per gli ambienti focali =====
	logger.process_start('Creazione delle immagini docker come ambienti focali ...')
	
	projenv_config: Dict[str, str] = projsenv_config["project"]
	tools_config: Dict[str, str] = projsenv_config["tools"]
	environ_config: Dict[str, str] = projsenv_config["environ"]
	
	focal_envs: Dict[str, DockerImage] = create_focal_images(
		projs_config,
		projsenv_config["os_image"],
		projsenv_config["dockerfile"],
		general_config["gen_tests_dir"],
		projsenv_config["envconfig_dir"],
		projsenv_config["python_version"],
		projenv_config["pyversion_file"],
		(
			projenv_config["python_deps_file"],
			projenv_config["ext_deps_file"],
			projenv_config["pre_extdeps_script"],
			projenv_config["post_extdeps_script"],
		),
		tools_config["tools_root"],
		tools_config["linting"],
		environ_config["path_prefix"],
		environ_config["tools_root"]
	)
	
	logger.process_end()
	
	## ===== Lettura dei templates dei prompts (di fallback) =====
	logger.process_start('Lettura dei template prompts di fallback ...')
	start_del: str = prompts_config["placeholders"]["start_del"]
	end_del: str = prompts_config["placeholders"]["end_del"]
	fallback_path: str = path_join(prompts_config["base_path"], prompts_config["generic_dirname"])
	fback_prompts: Dict[str, str] = read_fallback_templprompts(
		fallback_path,
		prompts_config["file_names"]
	)
	logger.process_end()
	
	## ===== Lettura dei placeholders dei template prompts =====
	placehs: Dict[str, str] = prompts_config["placeholders"]["common"]
	placehs.update(prompts_config["correctional"])
	placehs["code"] = prompts_config["code"]
	placehs["class_name"] = prompts_config["class_name"]
	
	## ===== Lettura degli iperparametri (di fallback) =====
	hparams: List[ILlmHyperParam] = read_fb_hyperparams(
		platf_config["platform"],
		general_config["def_model_params"],
		logger
	)
	
	# ===== Creazione della chat (specifica della piattaforma di inferenza) =====
	chat: ILlmChat = LlmChatFactory.create(
		ELlmChatApis[platf_config["platform"].upper()]
	)
	
	# ===== Creazione dell' accessor per la piattaforma di inferenza =====
	logger.process_start('Preparazione dell\' accessor alla piattaforma di inferenza ...')
	# Creazione dell' oggetto accessor
	platform: ILlmApiAccessor = inst_apiaccsor(
		platf_config["platform"], platf_config["platform_options"],
		console_logger
	)
	# Associazione dell' oggetto chat all' accessor
	platform.set_chat(chat)
	logger.process_end()
	
	## ===== Creazione del generatore delle test-suites parziali =====
	ptsuite_gen: EntityPtsuiteGenerator = create_eptsuite_generator(
		platform, general_config["max_gen_times"],
		console_logger
	)
	
	## ===== Creazione dei verificatori di correttezza delle test-suites parziali =====
	synt_chker: ISyntacticChecker = SyntacticCheckerFactory.create(ESyntCheckerTool.PYCOMPILE)
	lint_chker: LintingChecker = LintingChecker(
		tools_config["linting"], environ_config["lint_executer"],
		logger=console_logger
	)
	
	## ===== Creazione dei correttori delle test-suites parziali =====
	synt_corr: PtsuiteSyntacticCorrector = PtsuiteSyntacticCorrector(
		general_config["max_corr_times"], platform,
		synt_chker,
		logger=console_logger
	)
	lint_corr: PtsuiteLintingCorrector = PtsuiteLintingCorrector(
		general_config["max_corr_times"], platform,
		lint_chker,
		logger=console_logger
	)
	
	# Stabilimento della configurazione dei tests saltati
	skipdtests_config: Dict[str, str] = general_config["skipped_tests"]
		
	## ========================================================================
	## ===== Processo di "Generazione delle Test-suites per ogni modello" =====
	## ========================================================================
	project_names: List[str] = list(projs_config.keys())
	
	curr_prompts: Dict[str, str]
	func_bder: PromptBuilder = PromptBuilder(init_del=start_del, end_del=end_del)
	meth_bder: PromptBuilder = PromptBuilder(init_del=start_del, end_del=end_del)
	corr_bder: PromptBuilder = PromptBuilder(init_del=start_del, end_del=end_del)
	prompt_builders: Tuple[PromptBuilder, PromptBuilder, PromptBuilder]
	
	llmname_hashalg: str = general_config["model_names"]["hashing_alg"]
	digest_len: int = general_config["model_names"]["digest_len"]
	modelname_norm: str
	
	llm_specimpl_f: ILlmSpecImplFactory = LlmSpecImplFactoryResolver.resolve(
		EPlatformCombo[platf_config["platform"].upper()]
	)
	llm_specimpl: ILlmSpecImpl
	
	llmplat_hparam_f: ILlmHyperParamFactory
	llmplat_combo: str
	lst_id: int
	
	project_info: Dict[str, Any]
	full_root: str
	focal_root: str
	tests_root: str
	gentests_root: str
	focal_excluded: List[str]
	moddecl_extr: AMutableModuleDeclsExtractor = TreeSitterModuleDeclsExtractor("pass")
	
	is_py_file: bool
	module_path: str
	tsuite_path: str
	module_relpath: str
	tsuite_relpath: str
	
	llmmodel_cname: str
	
	# ===== Scorrimento dei Large Language Models scelti =====
	console_logger.log('Inizio del processo di "Generazione delle test-suites per ogni modello"')
	console_logger.set_messages_sep("\n\t")
	for llm_model, llm_specparams in models_config.items():
		console_logger.log(f'Inizio generazione delle test-suites per il modello "{llm_model}"')
		console_logger.set_messages_sep("\n\t\t")
		
		llmmodel_cname = llm_model.replace("-", "_").upper()
		curr_prompts = fback_prompts
		
		# ===== Conversione del nome del LLM in implementazione specifica =====
		# Creazione dell' oggetto di implementazione specifica
		llm_specimpl = llm_specimpl_f.create(
			ESpecLlmImpl[llmmodel_cname]
		)
		# Impostazione dell' implementazione specifica nell' accessor della piattaforma
		platform.select_model(llm_specimpl)
		
		# ===== Stabilimento della factory di iperparametri relativamente alla combo modello/piattaforma =====
		llmplat_combo = f'{platf_config["platform"]};{llm_model}'
		try:
			llmplat_hparam_f = LlmHyperParamFactoryResolver.resolve(llmplat_combo)
		except NotImplementedError:
			# Se non è presente una factory per la combo modello/piattaforma
			# uso quella della piattaforma
			llmplat_hparam_f = LlmHyperParamFactoryResolver.resolve(platf_config["platform"])
			
		# ===== Conversione degli iperparametri specifici per il modello =====
		for hparam_name, hparam_val in llm_specparams.items():
			# Creazione dell' oggetto iperparametro
			hparam = llmplat_hparam_f.create(hparam_name)
			hparam.set_value(str(hparam_val))
			try:
				# Eventuale sostituzione dell' iperparametro di fallback con quello specifico
				# richiesto dal LLM
				lst_id = hparams.index(hparam)
				hparams[lst_id] = hparam
			except ValueError:
				# Sennò aggiunta agli altri iperparametri
				hparams.append(hparam)
		
		# ===== Impostazione di ogni iperparametro nell' accessor della piattaforma =====
		for hparam in hparams:
			platform.add_hyperparam(hparam)
				
		# ===== Lettura degli eventuali prompt specifici del modello =====
		model_prompts = read_1model_templprompts(
			prompts_config["base_path"],
			llm_model,
			llmname_hashalg,
			digest_len,
			prompts_config["file_names"]
		)
		curr_prompts.update(model_prompts)
		func_bder.set_template_prompt(curr_prompts["functional"])
		meth_bder.set_template_prompt(curr_prompts["methodal"])
		corr_bder.set_template_prompt(curr_prompts["correctional"])
		
		# ===== Calcolo nome della directory delle test-suites generate dal modello =====
		# Normalizzazione del nome del LLM
		modelname_norm = normalize_llmname(llm_model, llmname_hashalg, digest_len)
		# Composizione del nome della directory
		gentest_dirname = path_join(general_config["gen_tests_dir"], modelname_norm)
		
		##
		## ===== Scorrimento dei progetti focali =====
		##
		for project_name in project_names:
			console_logger.log(f'Inizio generazione per il progetto "{project_name}"')
			console_logger.set_messages_sep("\n\t\t\t")
			
			# ===== Ottenimento delle informazioni del progetto focale =====
			project_info = projs_config[project_name]
			# Ottenimento della Focal Project Root Path
			focal_root = project_info["focal_root"].rstrip(path_sep).rstrip(path_altsep)
			# Calcolo della Full Project Root Path
			full_root = path_split(focal_root)[0].rstrip(path_sep).rstrip(path_altsep)
			# Ottenimento della Tests Project Root Path
			tests_root = project_info["tests_root"].rstrip(path_sep).rstrip(path_altsep)
			# Ottenimento della lista di paths/files esclusi dal codice focale
			focal_excluded = project_info.get("focal_excluded", [])
			
			# Impostazione dell' immagine dell' ambiente focale nel verificatore di linting
			lint_chker.set_focal_project(
				project_name, full_root,
				focal_envs[project_name],
				environ_config["path_prefix"]
			)
			
			# ===== Creazione degli spazi di memorizzazione per il progetto nelle caches =====
			genf_cache.create_projspace(project_name)
			genm_cache.create_projspace(project_name)
			corrs_cache.create_projspace(project_name)
			corrl_cache.create_projspace(project_name)
			
			# Calcolo della Gen-tests Project Root Path relativa al modello corrente
			gentests_root = path_join(
				path_split(focal_root)[0],
				gentest_dirname
			)
			
			# Azzeramento della Gen-Tests Project Root Path relativa al modello corrente
			if os_fdexists(gentests_root):
				os_dremove(gentests_root)
			os_mkdirs(gentests_root)
			
			focal_excluded.append(general_config["always_excluded"])
			# ===== Processo di "Generazione delle Test-suites per progetto focale" =====
			for curr_path, dirs, file_names in os_walk(focal_root):
				# Se la directory non è esclusa dal codice focale
				if not curr_path in focal_excluded:
					for file_name in file_names:
						is_py_file = file_name.endswith(".py")
		
						# Se il file non è escluso dal codice focale
						# ed è un modulo Python (ha estensione ".py")
						if ((is_py_file) and (not (file_name in focal_excluded))):
							module_path = path_join(curr_path, file_name)
							
							# Calcolo della directory che conterrà la test-suite del modulo
							common_path: str = path_intersect([curr_path, focal_root])
							tsuite_path = path_relative(curr_path, start=common_path)
							tsuite_path = path_join(
								path_join(gentests_root, tsuite_path), file_name
							)
						
							# Creazione/sovrascrittura della directory test-suite
							if os_fdexists(tsuite_path):
								os_dremove(tsuite_path)
							os_mkdirs(tsuite_path)
						
							# Calcolo delle paths relative (da utilizzare nei prompts)
							tsuite_relpath, module_relpath  \
								= calculate_prompt_relpaths(focal_root, tsuite_path, module_path)
							
							prompt_builders = (func_bder, meth_bder, corr_bder)
							for prompt_bder in prompt_builders:
								prompt_bder.set_placeholder(placehs["module_path"], module_relpath)
								prompt_bder.set_placeholder(placehs["tsuite_path"], tsuite_relpath)
							
							# Generazione della test-suite del module-file attuale
							generate_correct_mbym(
								project_name, llm_model,
								module_path,
								moddecl_extr,
								(ptsuite_gen, platform, chat),
								(synt_corr, lint_corr),
								platf_config["response_timeout"],
								(general_config["max_gen_times"], general_config["max_corr_times"]),
								platf_config["response_timeout"],
								(prompt_builders, placehs),
								(genf_cache, genm_cache),
								(corrs_cache, corrl_cache),
								(
									skipdtests_config["file_format"],
									(skipdtests_config["funcs_gen"], skipdtests_config["funcs_corr"],
									 skipdtests_config["meth_gen"], skipdtests_config["meth_corr"])
								),
								logger, console_logger
							)
							
							# Azzeramento dei prompts
							func_bder.unset_placeholders()
							meth_bder.unset_placeholders()
							corr_bder.unset_placeholders()
							
							# Pulizia delle risorse utilizzate dai verificatori
							synt_chker.clear_resources()
							lint_chker.clear_resources()
							
							# Pulizia della chat
							chat.clear()
							
			console_logger.set_messages_sep("\n\t\t")
			console_logger.log(f'Generazione per il progetto "{project_name}" terminata!')
		console_logger.set_messages_sep("\n\t")
		console_logger.log(f'Generazione per il modello "{llm_model}" terminata!')
	console_logger.set_messages_sep("\n")
	logger.process_start("Chiusura delle caches di test-suite parziali ...")
	
	genf_cache.close() if genf_cache else None
	genm_cache.close() if genm_cache else None
	corrs_cache.close() if corrs_cache else None
	corrl_cache.close() if corrl_cache else None
	
	logger.process_end()
	console_logger.log("Esecuzione di \"exec_gents.py\" terminata!")