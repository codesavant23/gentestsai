from typing import List, Dict, Any

# =========== ArgParse Utilities =========== #
from argparse import (
	Namespace as ArgumentsList,
	ZERO_OR_MORE,
	ONE_OR_MORE,
)
ARGP_0_PLUS = ZERO_OR_MORE
ARGP_1_PLUS = ONE_OR_MORE
ARGP_POS_OPT = "?"
# ========================================== #
# ============== OS Utilities ============== #
from os.path import exists as os_fdexists
from sys import stdout as os_stdout
# ========================================== #
# ============ Path Utilities ============ #
from os.path import (
	join as path_join,
	split as path_split,
	splitext as path_splitext,
	dirname as path_getdir,
	abspath as path_absolute,
)
from pathlib import PosixPath
# ======================================== #
# ============== Docker SDK Utilities =============== #
from docker import DockerClient
from docker.models.images import Image as DockerImage
# =================================================== #

from logic.variability import EImplementedPlatform
from logic.configuration.config_parser import (
	IConfigParser,
	ConfigParserFactory, EParserFiletype
)

from logic.focalproj_configuration.focal_container import FocalContainer

from logic.calc_coverage import CoverageRcWriter

from main_execs import (
	read_general_config, read_projs_config, read_projsenv_config, read_models_config, read_calccov_config,
	normalize_llmname,
	create_focal_images
)
from main_execs.calc_cov import (
	read_arguments,
	write_file_intofenv, write_dir_intofenv,
	write_covrc
)

from logic.utils.logger import (
	ATemporalFormattLogger, ConsoleTemporalFormattLogger
)
from logic.utils.process_logger import ProcessLogger


SCRIPT_PATH: str = path_getdir(path_absolute(__file__))
LOG_FORMAT: str = "{message} ({day}/{month}/{year} {hour}:{min}:{second})"



def calculate_coverage():
	args: ArgumentsList = read_arguments(SCRIPT_PATH)
	
	covrc_writer: CoverageRcWriter = CoverageRcWriter()
	
	console_logger: ATemporalFormattLogger = ConsoleTemporalFormattLogger(os_stdout)
	console_logger.set_messages_sep("\n")
	console_logger.set_format(LOG_FORMAT)
	logger: ProcessLogger = ProcessLogger(console_logger, "\n")
	
	console_logger.log('Software "exec_calc_coverage.py" avviato')
	
	# ===== Lettura dei files di configurazione =====
	logger.process_start('Lettura dei files di configurazione ...')
	
	platform: EImplementedPlatform = EImplementedPlatform[args.platform.upper()]
	cfg_parser: IConfigParser = ConfigParserFactory().create(
		EParserFiletype[args.config_type.upper()]
	)
	
	general_cfg: Dict[str, Any] = read_general_config(
		args.config_root, args.general_config,
		cfg_parser, platform
	)
	
	models_cfg: Dict[str, Any] = read_models_config(
		args.config_root, args.models_config,
		cfg_parser, platform
	)
	models_list: List[str] = list(models_cfg.keys())
	
	projs_cfg: Dict[str, Any] = read_projs_config(
		args.config_root, args.projects_config,
		cfg_parser
	)
	
	projsenv_cfg: Dict[str, Any] = read_projsenv_config(
		args.config_root, args.projsenv_config,
		cfg_parser, projs_cfg,"v2"
	)
	projenv_cfg: Dict[str, str] = projsenv_cfg["project"]
	
	tools_dict: Dict[str, str] = projsenv_cfg["tools"]
	calcov_cfg: Dict[str, Any] = read_calccov_config(
		args.config_root, args.calccov_config,
		cfg_parser,
		path_join(tools_dict["tools_root"], tools_dict["coverage"])
	)
	
	logger.process_end()
	
	# ===== Ottenimento del manager di containerizzazione =====
	path_prefix: str = projsenv_cfg["environ"]["path_prefix"]
	
	console_logger.log('Preparazione delle immagini docker come ambienti focali ...')
	console_logger.set_messages_sep("\n\t")

	focal_envs: Dict[str, DockerImage] = create_focal_images(
		projs_cfg,
		projsenv_cfg["images_prefix"], projsenv_cfg["image_tag"],
		projenv_cfg["dockerfile"],
		general_cfg["gen_tests_dir"], projsenv_cfg["envconfig_dir"],
		projenv_cfg["pyversion_file"],
		(
			projenv_cfg["python_deps_file"],
			projenv_cfg["ext_deps_file"],
			projenv_cfg["pre_extdeps_script"],
			projenv_cfg["post_extdeps_script"],
			projenv_cfg["pre_pydeps_script"],
			projenv_cfg["post_pydeps_script"]
		),
		tools_root=projsenv_cfg["tools"]["tools_root"],
		linttools_dir=projsenv_cfg["tools"]["linting"],
		covtools_dir=projsenv_cfg["tools"]["coverage"],
		path_prefix=path_prefix,
		logger=console_logger,
		pref_contman=projsenv_cfg.get("pref_contman", None)
	)
	
	console_logger.set_messages_sep("\n")
	console_logger.log("Ambienti focali pronti!")

	proj_fenv_img: DockerImage
	proj_fenv: FocalContainer

	full_root: str
	eff_full_root: str
	
	focal_dirname: str
	focal_root: str

	tests_dirname: str
	tests_root: str

	gentests_dirname: str
	gentests_root: str

	covconfig_dirname: str = calcov_cfg["covconfig_dir"]

	pytargs_fname: str = calcov_cfg["pytargs_fname"]
	covargs_fname: str = calcov_cfg["covargs_fname"]
	pytest_args_path: str
	coverage_args_path: str

	covconfig_root: str

	pytest_args: Dict[str, str]
	coverage_args: Dict[str, List[str]]

	venv_py_exepath: str
	coverage_source: str
	cmds_base: List[str]

	calccov_human_cmd: List[str]
	reportcov_human_cmd: List[str]
	cov2json_human_cmd: List[str]

	cov_llm_basefile: str
	covdata_llm_path: str
	covjson_llm_path: str

	covdata_human_path: str
	covjson_human_path: str
	
	calccov_script_m: str = path_splitext(calcov_cfg["calccov_script"])[0]

	for proj_name, proj_info in projs_cfg.items():
		console_logger.log(f'Calcolo della coverage per il progetto "{proj_name}" ...')
		console_logger.set_messages_sep("\n\t")
		
		full_root = proj_info["full_root"]
		covconfig_root = path_join(full_root, covconfig_dirname)
		
		proj_fenv_img = focal_envs[proj_name]
		
		logger.process_start("Avvio dell' ambiente focale ...")
		proj_fenv = FocalContainer(
			proj_fenv_img, full_root,
			projsenv_cfg["environ"]["path_prefix"],
		)
		proj_fenv.start_container()
		logger.process_end()
		
		glob_end: str
		excluded: List[str] = list()
		focal_excluded: List[str] = proj_info.get("focal_excluded", [])
		tests_excluded: List[str] = proj_info.get("tests_excluded", [])
		
		for fexcl_relpath in focal_excluded:
			glob_end = ""
			fexcl_pospath : PosixPath = PosixPath(fexcl_relpath)
			if fexcl_pospath.is_dir():
				glob_end = "/*"
			excluded.append(f"*{str(fexcl_pospath).lstrip(".")}{glob_end}")
			
		for texcl_relpath in tests_excluded:
			glob_end = ""
			texcl_pospath : PosixPath = PosixPath(texcl_relpath)
			if texcl_pospath.is_dir():
				glob_end = "/*"
			excluded.append(f"*{str(texcl_pospath).lstrip(".")}{glob_end}")
		
		if len(excluded) == 0:
			excluded = None
		
		covrc_writer.set_focal_project(
			path_split(proj_info["focal_root"])[1],
			excluded
		)
		
		logger.process_start("Scrittura del file .coveragerc ...")
		write_covrc(
			full_root, proj_fenv,
			path_prefix,
			covrc_writer, calcov_cfg["covrc_fname"],
			"gtsai__humcov_result.json"
		)
		logger.process_end()
		logger.process_start("Calcolo della statement coverage dei tests umani ...")
		proj_fenv.execute(
			f"/bin/bash python -m $COVTOOLS_DIRNAME.{calccov_script_m} "
		    f"{calcov_cfg["covrc_fname"]} gtsai__results/gtsai__humcov_result.json "
			f"--rtype json"
		)
		logger.process_end()
		
		# ===== Calcolo della coverage per ogni modello =====
		for model_name in models_list:
			model_nname = normalize_llmname(
				model_name,
				general_cfg["model_names"]["hashing_alg"],
				general_cfg["model_names"]["digest_len"]
			)

			# Scrittura dei tests generati dal LLM nell' ambiente focale
			gentests_dirname = path_join(
				general_cfg["gen_tests_dir"],
				model_nname
			)
			gentests_root = path_join(
				full_root,
				gentests_dirname
			)
			write_dir_intofenv(
				gentests_root,
				model_nname,
				f"project/{general_cfg['gen_tests_dir']}",
				path_prefix, proj_fenv,
				remove_src=False
			)
			
			# Scrittura dell' RCFile specifico e calcolo della coverage
			logger.process_start("Scrittura del file .coveragerc ...")
			write_covrc(
				full_root, proj_fenv,
				path_prefix,
				covrc_writer, calcov_cfg["covrc_fname"],
				f"gtsai__{model_nname}_cov_result.json"
			)
			logger.process_end()
			logger.process_start(f'Calcolo della statement coverage del modello "{model_name}" ...')
			proj_fenv.execute(
				f"/bin/bash python -m $COVTOOLS_DIRNAME.{calccov_script_m} --llm "
			    f"{calcov_cfg["covrc_fname"]} gtsai__results/gtsai__{model_nname}_cov_result.json "
				f"--rtype json"
			)
			logger.process_end()
		
		console_logger.set_messages_sep("\n")
		logger.process_start("Stop dell' ambiente focale ...")
		proj_fenv.stop_container()
		logger.process_end()
		

if __name__ == "__main__":
	calculate_coverage()