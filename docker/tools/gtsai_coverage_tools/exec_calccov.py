from typing import Dict
# ============== OS Utilities ============== #
from os import (
	chdir as os_chdir,
	environ as os_getenv
)
from os.path import exists as os_fdexists
# ========================================== #
# ============ Path Utilities ============ #
from os.path import (
	sep as path_sep,
	altsep as path_altsep,
	join as path_join,
	split as path_split,
)
from pathlib import Path as SystemPath
_PATH_SEPS: str = f"{path_sep}{path_altsep if path_altsep is not None else ''}"
# ======================================== #
# =========== ArgParse Utilities =========== #
from argparse import (
	ArgumentParser,
	Namespace as ArgumentsList,
	ZERO_OR_MORE,
	ONE_OR_MORE,
)
ARGP_0_PLUS = ZERO_OR_MORE
ARGP_1_PLUS = ONE_OR_MORE
# ========================================== #
# ============== JSON Utilities ============== #
from json import JSONDecoder
# ============================================ #

from .execs import resolve_report_type
from .coverage_evaluation import (
	CoverageEvaluator, ECoverageReportType
)



if __name__ == "__main__":
	arg_parser: ArgumentParser = ArgumentParser(
		description="Human tests's coverage evaluation for GenTestsAI",
		usage="""
		python exec_calccov.py <rcfile_name> <covconfig_dirname> <covresult_relpath> [--rtype <report_type>] [--tests-runner <tests_runner_name>] [--pyt-args <pytargs_fname>] [--cov-args <covargs_fname>]
		-OR-
		python exec_calccov.py <rcfile_name> <covconfig_dirname> <covresult_relpath> --llm <llm_gentests_root> [--rtype <report_type>] [--tests-runner <tests_runner_name>] [--pyt-args <pytargs_fname>] [--cov-args <covargs_fname>]
		"""
	)
	
	arg_parser.add_argument(
		"rcfile_name",
	    help='Name of the ".coveragerc" file'
	)
	arg_parser.add_argument(
		"covconfig_dirname",
	    help='Name of the optional Cov-Config directory'
	)
	arg_parser.add_argument(
		"covresult_relpath",
		help="Coverage result JSON file path (relative to the container path prefix)"
	)
	
	arg_parser.add_argument(
		"--llm",
		help="Optional. Flag to run script for LLM's coverage calculation.",
		required=False,
		default=""
	)
	arg_parser.add_argument(
		"--rtype",
		help='Optional. Type of the coverage report that will be produced.',
		required=False,
		default="json"
	)
	arg_parser.add_argument(
		"--tests_runner",
		help='Optional. Name of the tests runner that will be executed by "coverage.py".',
		required=False,
		default="pytest"
	)
	arg_parser.add_argument(
		"--pytargs-fname",
		help='Optional. Name of the "pytest" arguments file.',
		required=False,
		default="pytest_args.json"
	)
	arg_parser.add_argument(
		"--covargs-fname",
		help='Optional. Name of the "coverage.py" arguments file.',
		required=False,
		default="coverage_args.json"
	)
	
	script_args: ArgumentsList = arg_parser.parse_args()
	
	report_type: ECoverageReportType = resolve_report_type(script_args.rtype)
	
	full_root: str = os_getenv["FULL_ROOT"]
	focal_root: str = os_getenv["FOCAL_ROOT"]
	path_prefix: str = path_split(full_root)[0]
	
	rcfile_path: str = path_join(full_root, script_args.rcfile_name)
	covresult_path: str = f"{path_prefix}/{script_args.covresult_relpath}"
	covconfig_root: str = f"{path_prefix}/project/{script_args.covconfig_dirname}"
	
	cov_evaluator: CoverageEvaluator = CoverageEvaluator(
		rcfile_path, report_type
	)
	if os_fdexists(covconfig_root):
		pytargs_path: str = path_join(covconfig_root, script_args.pytargs_fname)
		covargs_path: str = path_join(covconfig_root, script_args.covargs_fname)
		
		json_dec: JSONDecoder = JSONDecoder()
		if os_fdexists(pytargs_path):
			with open(pytargs_path, "r") as fp:
				args: Dict[str, str] = json_dec.decode(fp.read())
				cov_evaluator.set_tester_args(args)
			
		if os_fdexists(covargs_path):
			with open(pytargs_path, "r") as fp:
				content: Dict[str, Dict[str, str]] = json_dec.decode(fp.read())
				general_args: Dict[str, str] = content.get("general", None)
				run_args: Dict[str, str] = content.get("run", None)
				cov_evaluator.set_covpy_args(general_args, run_args)
	
	tests_root: str = os_getenv["TESTS_ROOT"]
	if script_args.llm:
		tests_root = f"{path_prefix}/{script_args.llm}"
	
	os_chdir(str(SystemPath(focal_root).parent))
	cov_evaluator.evaluate(tests_root)
	
	cov_evaluator.process_report()
	
	cov_evaluator.create_report()