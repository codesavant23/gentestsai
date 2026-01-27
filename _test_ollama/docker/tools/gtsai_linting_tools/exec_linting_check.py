from typing import List

# ============== OS Utilities ============== #
from os import environ as os_getenv
# ========================================== #
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

from . import PartialTsuite1TimeLintingChecker



if __name__ == "__main__":
	arg_parser: ArgumentParser = ArgumentParser(
		description="Partial test-suite Linting Checker for GenTestsAI",
		usage="python exec_linting_check.py <ptsuite_relpath> <result_relpath> [--pyl_args ...]"
	)
	
	arg_parser.add_argument(
		"ptsuite_relpath",
	    help="Partial test-suite file path (relative to the Full Project Root Path)"
	)
	arg_parser.add_argument(
		"result_relpath",
		help="Linting result JSON file path (relative to the Full Project Root Path)"
	)
	arg_parser.add_argument(
		"--pyl_args",
		help='Optional. PyLint extra arguments (without any space between each flag and its value). Must not contain "--source" and "--output-format" flags',
		nargs=ARGP_1_PLUS, required=False,
		default=[]
	)
	script_args: ArgumentsList = arg_parser.parse_args()
	
	pyl_args: List[str] = script_args.pyl_args
	ptsuite_relpath: str = script_args.ptsuite_relpath
	result_relpath: str = script_args.result_relpath
	
	full_root: str = os_getenv["FULL_ROOT"]
	ptsuite_path: str = f"{full_root}/{ptsuite_relpath}"
	result_path: str = f"{full_root}/{result_relpath}"
	
	ptsuite_checker: PartialTsuite1TimeLintingChecker = PartialTsuite1TimeLintingChecker(
		full_root,
		ptsuite_path,
		result_path
	)
	
	ptsuite_checker.check_lintically()
	
	ptsuite_checker.serialize_result()