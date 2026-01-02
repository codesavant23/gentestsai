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



def calculate_llm_coverage(
		llm_name_norm: str,
		llm_tests_root: str,
		focal_root: str,
		output_path: str,
		python_exepath: str = None,
		cov_general_args: List[str] = None,
		cov_run_args: List[str] = None,
		pytest_args: List[str] = None
):
	"""
		Calcola la coverage dei tests generati da uno specifico LLM

		Parameters
		----------
			llm_name_norm: str
				Una stringa contenente il nome dell' LLM normalizzato

			llm_tests_root: str
				Una stringa contenente la root path dei tests generati da quello specifico LLM

			focal_root: str
				Una stringa contenente la root path del codice focale

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
	# Setup dei comandi per il calcolo della coverage sui tests dello specifico LLM
	cov_llm_basefile = "coverage_" + llm_name_norm
	covdata_llm_path = path_join(output_path, cov_llm_basefile + ".dat")
	covjson_llm_path = path_join(output_path, cov_llm_basefile + ".json")

	calccov_llm_cmd = build_calc_coverage_cmd(
		llm_tests_root,
		focal_root,
		pythonexe_path=python_exepath,
		coverage_gen_args=cov_general_args,
		coverage_run_args=cov_run_args,
		pytest_args=pytest_args,
		covdata_file=covdata_llm_path
	)
	reportcov_llm_cmd = build_report_coverage_cmd(
		covdata_file=covdata_llm_path
	)
	cov2json_llm_cmd = build_cov2json_cmd(
		output_file=covjson_llm_path,
		covdata_file=covdata_llm_path
	)

	# Calcolo della Coverage sui tests generati dallo specifico LLM
	subp_run(calccov_llm_cmd)
	# Creazione del report sui tests generati dallo specifico LLM
	subp_run(reportcov_llm_cmd)
	# Creazione del file JSON contenente il report sui tests generati dallo specifico LLM
	subp_run(cov2json_llm_cmd)