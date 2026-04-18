from typing import List, Tuple, Set, Dict, Literal, Any

# =========== ArgParse Utilities =========== #
from argparse import Namespace as ArgumentsList
# ========================================== #
# ============ Path Utilities ============ #
from os.path import (
	sep as path_sep,
	altsep as path_altsep,
	normpath as os_normpath,
	join as path_join,
	split as path_split,
	splitext as path_splitext,
	dirname as path_getdir,
	commonpath as path_intersect,
	abspath as path_absolute,
	relpath as path_relative
)
from pathlib import Path as SystemPath
_PATH_SEPS: str = f"{path_sep}{path_altsep if path_altsep is not None else ''}"
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

from logic.variability import EImplementedPlatform

from main_execs import normalize_llmname
from main_execs.gents import read_arguments
from main_execs.gents.mbym._private.calculating_ptsuite_name import calculate_ptsuite_fname

from main_execs import read_gents_configfiles
from logic.configuration.config_parser import (
	IConfigParser,
	ConfigParserFactory, EParserFiletype
)

from logic.decls_extraction.moddecls_extractor import (
	AMutableModuleDeclsExtractor, TreeSitterModuleDeclsExtractor
)
from logic.decls_extraction.classdecls_extractor import IClassDeclsExtractor

from logic.ptsuite_generation.cache_accessor import (
	PtsuiteCacheAccessorFactory, ECacheAccessorType,
	IPtsuiteCacheAccessor
)
from logic.ptsuite_generation.cache_accessor.exceptions import (
	EntryNotExistsError
)

from logic.variability import ESkippedTestsFtypeFormat
from logic.ptsuite_generation.core.tests_skipping import (
	ISkipWriter,
	SkipWriterFactory
)


SCRIPT_PATH: str = path_getdir(path_absolute(__file__))
	


if __name__ == "__main__":
	gents_args: ArgumentsList = read_arguments(SCRIPT_PATH)
	
	config_parser: IConfigParser = ConfigParserFactory.create(
		EParserFiletype[gents_args.config_type.upper()]
	)
	configs: Dict[str, Dict[str, Any]] = read_gents_configfiles(
		gents_args.config_root,
		config_parser,
		EImplementedPlatform[gents_args.platform.upper()],
		file_names=(
			gents_args.platform_config,
			gents_args.general_config,
			gents_args.models_config,
			gents_args.projects_config,
			gents_args.projsenv_config,
			gents_args.prompts_config,
			gents_args.caches_config
		)
	)
	
	models_config: Dict[str, Any] = configs["models"]
	general_config: Dict[str, Any] = configs["general"]
	projs_config: Dict[str, Any] = configs["projects"]
	
	llmname_hashalg: str = general_config["model_names"]["hashing_alg"]
	digest_len: int = general_config["model_names"]["digest_len"]
	modelname_norm: str
	
	project_names: List[str] = list(projs_config.keys())
	
	skipd_genf_fname: str = general_config["skipped_tests"]["funcs_gen"]
	skipd_genm_fname: str = general_config["skipped_tests"]["meths_gen"]
	genf_skipw: ISkipWriter
	genm_skipw: ISkipWriter
	
	caches_root: str = input("Caches Root >:  ")
	
	funcs_cache_name: str
	meths_cache_name: str
	funcs_cache: IPtsuiteCacheAccessor
	meths_cache: IPtsuiteCacheAccessor

	for llm_model, llm_specparams in models_config.items():
		llmmodel_cname = (llm_model
		    .replace("-", "_")
			.replace(".", "_")
		    .upper()
		)
		
		# ===== Calcolo nome della directory delle test-suites generate dal modello =====
		# Normalizzazione del nome del LLM
		modelname_norm = normalize_llmname(llm_model, llmname_hashalg, digest_len)
		# Composizione del nome della directory
		gentest_dirname = path_join(general_config["gen_tests_dir"], modelname_norm)
		
		moddecls_extr: AMutableModuleDeclsExtractor = TreeSitterModuleDeclsExtractor("pass")
		
		funcs_cache_name = "gen_funcs.db"
		meths_cache_name = "gen_meths.db"
		funcs_cache = PtsuiteCacheAccessorFactory.create(ECacheAccessorType.SQLITE3, path_join(caches_root, llm_model, funcs_cache_name))
		meths_cache = PtsuiteCacheAccessorFactory.create(ECacheAccessorType.SQLITE3, path_join(caches_root, llm_model, meths_cache_name))
		
		ptsuite_code: str
		ptsuite_fname: str
		ptsuite_path: str
		methods: List[str]
		
		# ===== Ottenimento delle informazioni del progetto focale =====
		project_info = projs_config["detectron2"]
		# Ottenimento della Full Project Root Path
		full_root = project_info["full_root"].rstrip(_PATH_SEPS)
		# Ottenimento della Focal Project Root Path
		focal_root = project_info["focal_root"].rstrip(_PATH_SEPS)
		focal_root = path_join(full_root, focal_root)
		# Ottenimento della Tests Project Root Path
		tests_root = project_info["tests_root"].rstrip(_PATH_SEPS)
		tests_root = path_join(full_root, tests_root)
		# Ottenimento della lista di paths/files esclusi dal codice focale
		focal_excluded = project_info.get("focal_excluded", [])
		for i, focal_excl in enumerate(focal_excluded):
			focal_excluded[i] = path_join(focal_root, focal_excl)
			
		# Calcolo della Gen-tests Project Root Path relativa al modello corrente
		gentests_root = path_join(
			path_split(focal_root)[0],
			gentest_dirname
		)
		# Azzeramento della Gen-Tests Project Root Path relativa al modello corrente
		if os_fdexists(gentests_root):
			os_dremove(gentests_root)
		os_mkdirs(gentests_root)
		
		# ===== Processo di "Generazione delle Test-suites per progetto focale" =====
		for curr_path, dirs, file_names in os_walk(focal_root):
			# Se la directory non è esclusa dal codice focale
			if curr_path not in focal_excluded:
				curr_path = os_normpath(curr_path)
				for file_name in file_names:
					is_py_file = file_name.endswith(".py")
					
					# Se il file non è escluso dal codice focale
					# ed è un modulo Python (ha estensione ".py")
					if (
						(is_py_file) and
						(file_name not in general_config["always_excluded"])
					):
						module_path = path_join(curr_path, file_name)
						module_name = path_splitext(file_name)[0]
						
						# Calcolo della directory che conterrà la test-suite del modulo
						common_path: str = path_intersect([curr_path, focal_root])
						tsuite_dirpath = path_relative(curr_path, start=common_path)
						tsuite_dirpath = os_normpath(path_join(
							path_join(gentests_root, tsuite_dirpath),
							f"mod__{path_splitext(file_name)[0]}"
						))
					
						# Creazione/sovrascrittura della directory test-suite
						if os_fdexists(tsuite_dirpath):
							os_dremove(tsuite_dirpath)
						os_mkdirs(tsuite_dirpath)
					
						with open(module_path, "r") as fmodule:
							module_code = fmodule.read()
							moddecls_extr.set_module_code(module_code)
							
						func_names: List[str] = moddecls_extr.extract_funcnames()
						clss: List[IClassDeclsExtractor] = moddecls_extr.extract_classes()
						
						# ===== Calcolo del `module_name` per le caches =====
						module_pathobj: SystemPath = SystemPath(
							path_relative(module_path.rstrip(".py"), start=focal_root)
						)
						module_path_parts: List[str] = list(module_pathobj.parts)
						cache_modname: str = ".".join(module_path_parts)
						
						genf_skipw = SkipWriterFactory.create(
							ESkippedTestsFtypeFormat.JSON,
							path_join(tsuite_dirpath, skipd_genf_fname)
						)
						genm_skipw = SkipWriterFactory.create(
							ESkippedTestsFtypeFormat.JSON,
							path_join(tsuite_dirpath, skipd_genm_fname)
						)
						
						for func_name in func_names:
							for try_num in range(1, 11+1):
								if try_num < 11:
									try:
										ptsuite_fname = calculate_ptsuite_fname(func_name)
										ptsuite_code = funcs_cache.get_ptsuite("detectron2", cache_modname, func_name, llm_model, try_num)
										
										if ptsuite_code != "":
											ptsuite_path = path_join(tsuite_dirpath, ptsuite_fname)
											with open(ptsuite_path, "w") as fptsuite:
												fptsuite.write(ptsuite_code)
												fptsuite.flush()
									except EntryNotExistsError:
										genf_skipw.write_skipd_test(func_name)
								else:
									genf_skipw.write_skipd_test(func_name)
						
						for cls in clss:
							methods = cls.method_names()
							for meth_name in methods:
								for try_num in range(1, 11+1):
									if try_num < 11:
										try:
											ptsuite_fname = calculate_ptsuite_fname(meth_name, f"{cls.class_name()}$")
											ptsuite_code = funcs_cache.get_ptsuite(
												"detectron2", cache_modname,
												f"{cls.class_name()}.{meth_name}",
												llm_model, try_num
											)
											
											if ptsuite_code != "":
												ptsuite_path = path_join(tsuite_dirpath, ptsuite_fname)
												with open(ptsuite_path, "w") as fptsuite:
													fptsuite.write(ptsuite_code)
													fptsuite.flush()
										except EntryNotExistsError:
											genm_skipw.write_skipd_test(f"{cls.class_name()}.{meth_name}")
									else:
										genm_skipw.write_skipd_test(f"{cls.class_name()}.{meth_name}")