from typing import List

from os.path import (
	join as path_join,
)

from .cmds_building import (
	build_calc_coverage_cmd,
	build_report_coverage_cmd,
	build_cov2json_cmd
)

from subprocess import (
	run as subp_run
)



def calculate_human_coverage(
	human_tests_root: str,
	focal_root: str,
	covdata_file: str,
	covjson_file: str,
	output_path: str,
	python_exepath: str = None,
	cov_general_args: List[str] = None,
	cov_run_args: List[str] = None,
	pytest_args: List[str] = None,
):
	"""
		Calcola la coverage dei tests umani

		Parameters
		----------
			human_tests_root: str
				Una stringa contenente la root path dei tests umani

			focal_root: str
				Una stringa contenente la root path del codice focale

			covdata_file: str
				Una stringa contenente il nome del data-file corrispondente al calcolo della coverage

			covjson_file: str
				Una stringa contenente il nome del file JSON, di report, corrispondente all' output
				del calcolo della coverage

			output_path: str
				Una stringa contenente la path che conterrà il data-file e il report relativi al
				calcolo della coverage

			python_exepath: str
				Opzionale. Una stringa contenente il path dell' interprete Python da utilizzare

			cov_general_args: List[str]
				Opzionale. Una lista di stringhe contenente gli argomenti da passare al comando `coverage`

			cov_run_args: List[str]
				Opzionale. Una lista di stringhe contenente gli argomenti da passare all' operazione `run` del comando `coverage`

			pytest_args: List[str]
				Opzionale. Una lista di stringhe contenente gli argomenti da passare al comando `pytest`
	"""
	covdata_human_path = path_join(output_path, covdata_file)
	covjson_human_path = path_join(output_path, covjson_file)

	# Setup dei comandi per il calcolo della coverage su tests umani
	calccov_human_cmd = build_calc_coverage_cmd(
		human_tests_root,
		focal_root,
		pythonexe_path=python_exepath,
		coverage_gen_args=cov_general_args,
		coverage_run_args=cov_run_args,
		pytest_args=pytest_args,
		covdata_file=covdata_human_path
	)
	reportcov_human_cmd = build_report_coverage_cmd(
		covdata_file=covdata_human_path
	)
	cov2json_human_cmd = build_cov2json_cmd(
		covdata_file=covdata_human_path,
		output_file=covjson_human_path
	)

	# Calcolo della Coverage sui tests umani
	subp_run(calccov_human_cmd)
	# Creazione del report sui tests umani
	subp_run(reportcov_human_cmd)
	# Creazione del file JSON contenente il report sui tests umani
	subp_run(cov2json_human_cmd)