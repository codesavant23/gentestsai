"""
	TODO: Sviluppare l' effettivo calcolo della coverage in una cartella temporanea (poi si farà in containers)
"""

from typing import List, Dict, Tuple, Any

from configuration import read_json_tobuff
from json import (
	loads as json_loads
)

from os import (
	name as os_name
)
from shutil import (
	rmtree as os_dremove,
	copytree as os_dcopy,
)
from os.path import (
	sep as path_sep,
	altsep as path_altsep,
	exists as os_fdexists,
	join as path_join,
	split as path_split,
	splitext as path_split_ext,
	relpath as path_relpath,
)

from tempfile import (
	TemporaryDirectory
)

from cov_cmds_building import (
	build_calc_coverage_cmd,
	build_report_coverage_cmd,
	build_cov2json_cmd
)

from subprocess import (
	run as subp_run
)



if __name__ == "__main__":
	general_config: Dict[str, str] = json_loads(
		read_json_tobuff("config/general.json")
	)

	projs_config: Dict[str, Dict[str, Any]] = json_loads(
		read_json_tobuff("config/projs.json")
	)

	models_list: List[str] = json_loads(
		read_json_tobuff("config/models.json")
	)

	calccov_config: Dict[str, str] = json_loads(
		read_json_tobuff("config/calc_coverage.json")
	)

	full_root: str
	eff_full_root: str

	focal_dirname: str
	focal_root: str

	tests_dirname: str
	tests_root: str

	gentests_dirname: str = general_config["gen_tests_dir"]
	eff_gentests_dirname: str
	gentests_root: str

	covconfig_dirname: str = calccov_config["covconfig_dir"]
	covconfig_main_file: str = calccov_config["covconfig_main_file"]
	pytest_args_file: str = calccov_config["pytest_args_file"]
	coverage_args_file: str = calccov_config["coverage_args_file"]
	covconfig_root: str

	project_names: List[str] = list(projs_config.keys())

	venv_py: str
	pytest_args: List[str]
	coverage_args: Dict[str, List[str]]

	coverage_source: str
	cmds_base: List[str]

	has_human_cov_calc: bool
	calccov_human_cmd: List[str]
	reportcov_human_cmd: List[str]
	cov2json_human_cmd: List[str]

	cov_llm_basefile: str

	for project_name in project_names:
		has_human_cov_calc = False
		full_root = path_split(projs_config[project_name]["focal_root"])[0]
		focal_dirname = path_split(projs_config[project_name]["focal_root"])[1]
		tests_dirname = path_relpath(
			projs_config[project_name]["tests_root"],
			start=full_root
		)

		# Configurazione ed Esecuzione della Coverage in una Temporary Directory
		# TODO: (In futuro) Sostituire con l'incapsulazione in un docker
		with TemporaryDirectory(dir=full_root, delete=True) as eff_full_root:
			os_dcopy(
				full_root,
				eff_full_root,
				dirs_exist_ok=True
			)

			# TODO: Esecuzione degli script Powershell (Esegui main.ps1)

			for model in models_list:
				model_dirname = model.replace(":", "_")

				eff_gentests_dirname = path_join(
					gentests_dirname,
					model_dirname
				)

				focal_root = path_join(
					eff_full_root,
					focal_dirname
				)
				tests_root = path_join(
					eff_full_root,
					tests_dirname
				)
				gentests_root = path_join(
					eff_full_root,
					eff_gentests_dirname
				)
				covconfig_root = path_join(
					eff_full_root,
					covconfig_dirname
				)

				# Costruzione della path del python del venv creato
				venv_py: str = path_join(
					eff_full_root,
					"venv-coverage"
				)
				if os_name == "posix":
					venv_py = path_join(venv_py, "bin/python")
				elif os_name == "nt":
					venv_py = path_join(venv_py, r"Scripts\python.exe")
				else:
					raise OSError("Sistema operativo sconosciuto")

				# Lettura degli argomenti relativi a coverage.py
				coverage_args = json_loads(
					read_json_tobuff(path_join(covconfig_root, coverage_args_file))
				)

				# Lettura degli argomenti relativi a pytest
				pytest_args = json_loads(
					read_json_tobuff(path_join(covconfig_root, pytest_args_file))
				)
				pytest_args.append(tests_root)

				# Calcolo della Coverage sui tests Umani
				if not has_human_cov_calc:
					# Setup dei comandi per il calcolo della coverage su tests umani
					calccov_human_cmd = build_calc_coverage_cmd(
						tests_root,
						focal_root,
						pythonexe_path=venv_py,
						coverage_gen_args=coverage_args["general"],
						coverage_run_args=coverage_args["run"],
						pytest_args=pytest_args,
						covdata_file=path_join(
							eff_full_root,
							"coverage_human.dat"
						)
					)
					reportcov_human_cmd = build_report_coverage_cmd(
						covdata_file=path_join(eff_full_root,"coverage_human.dat")
					)
					cov2json_human_cmd = build_cov2json_cmd(
						output_file=path_join(eff_full_root,"coverage_human.json"),
						covdata_file=path_join(eff_full_root,"coverage_human.dat")
					)
					# Calcolo della Coverage sui tests umani
					subp_run(calccov_human_cmd)
					# Creazione del report sui tests umani
					subp_run(reportcov_human_cmd)
					# Creazione del file JSON contenente il report sui tests umani
					subp_run(cov2json_human_cmd)
					has_human_cov_calc = True

				# Setup dei comandi per il calcolo della coverage sui tests dello specifico LLM
				cov_llm_basefile = "coverage_" + model_dirname
				calccov_llm_cmd = build_calc_coverage_cmd(
					gentests_root,
					focal_root,
					pythonexe_path=venv_py,
					coverage_gen_args=coverage_args["general"],
					coverage_run_args=coverage_args["run"],
					pytest_args=pytest_args,
					covdata_file=path_join(eff_full_root, cov_llm_basefile+".dat")
				)
				reportcov_llm_cmd = build_report_coverage_cmd(
					covdata_file=path_join(eff_full_root, cov_llm_basefile+".dat")
				)
				cov2json_llm_cmd = build_cov2json_cmd(
					output_file=path_join(eff_full_root, cov_llm_basefile+".json"),
					covdata_file=path_join(eff_full_root, cov_llm_basefile+".dat")
				)

				# Calcolo della Coverage sui tests generati dallo specifico LLM
				subp_run(calccov_llm_cmd)
				# Creazione del report sui tests generati dallo specifico LLM
				subp_run(reportcov_llm_cmd)
				# Creazione del file JSON contenente il report sui tests generati dallo specifico LLM
				subp_run(cov2json_llm_cmd)

				# TODO: Aggregazione dei risultati e Valutazione

			# Numero righe coperte / # Numero di righe totali