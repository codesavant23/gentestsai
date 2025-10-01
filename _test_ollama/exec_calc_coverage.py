"""
	TODO: Sviluppare l' effettivo calcolo della coverage in una cartella temporanea (poi si farà in containers)
"""

from typing import List, Dict, Any

from logic.utils.json_to_str import read_json_tobuff
from json import (
	loads as json_loads
)

from logic.utils.model_name_normalizer import normalize_model_name

from os import (
	name as os_name,
)
from shutil import (
	copytree as os_dcopy,
)
from os.path import (
	join as path_join,
	exists as os_fdexists,
	split as path_split,
	relpath as path_relpath,
)

from tempfile import (
	TemporaryDirectory
)

from logic.calc_coverage.focal_proj_configuration import (
	configure_project_environ
)

from logic.calc_coverage.human_cov_calculation import (
	calculate_human_coverage
)
from logic.calc_coverage.llm_cov_calculation import (
	calculate_llm_coverage
)



def calculate_venv_pyexe(
		full_root: str,
		venv_name: str,
) -> str:
	venv_py_exepath: str = path_join(
		full_root,
		venv_name
	)
	if os_name == "posix":
		venv_py_exepath = path_join(venv_py_exepath, "bin/python")
	elif os_name == "nt":
		venv_py_exepath = path_join(venv_py_exepath, r"Scripts\python.exe")
	else:
		raise OSError("Sistema operativo sconosciuto")

	return venv_py_exepath


if __name__ == "__main__":
	general_config: Dict[str, str] = json_loads(
		read_json_tobuff("config/general.json")
	)

	projs_config: Dict[str, Dict[str, Any]] = json_loads(
		read_json_tobuff("config/projs.json")
	)

	models_list: List[Dict[str, Any]] = json_loads(
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
	pytest_args_path: str
	coverage_args_path: str

	covconfig_root: str

	project_names: List[str] = list(projs_config.keys())

	pytest_args: List[str]
	coverage_args: Dict[str, List[str]]

	venv_py_exepath: str
	coverage_source: str
	cmds_base: List[str]

	has_human_cov_calc: bool
	calccov_human_cmd: List[str]
	reportcov_human_cmd: List[str]
	cov2json_human_cmd: List[str]

	cov_llm_basefile: str
	covdata_llm_path: str
	covjson_llm_path: str

	covdata_human_path: str
	covjson_human_path: str

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

			focal_root = path_join(
				eff_full_root,
				focal_dirname
			)
			tests_root = path_join(
				eff_full_root,
				tests_dirname
			)
			covconfig_root = path_join(
				eff_full_root,
				covconfig_dirname
			)

			# Configurazione dell'ambiente del progetto focale (es. Installa le dipendenze)
			configure_project_environ(
				path_join(
					covconfig_root,
					covconfig_main_file
				),
				eff_full_root
			)

			for model in models_list:
				model_name = model["name"]
				model_normname = normalize_model_name(model_name)

				eff_gentests_dirname = path_join(
					gentests_dirname,
					model_normname
				)
				gentests_root = path_join(
					eff_full_root,
					eff_gentests_dirname
				)

				# Costruzione della path del python del venv creato
				venv_py_exepath = calculate_venv_pyexe(eff_full_root, "venv-coverage")

				# Lettura degli argomenti relativi a coverage.py
				coverage_args_path = path_join(covconfig_root, coverage_args_file)
				coverage_args = dict()
				if os_fdexists(coverage_args_path):
					coverage_args = json_loads(
						read_json_tobuff(coverage_args_path)
					)

				# Lettura degli argomenti relativi a pytest
				pytest_args_path = path_join(covconfig_root, pytest_args_file)
				pytest_args = None
				if os_fdexists(pytest_args_path):
					pytest_args = json_loads(
						read_json_tobuff(pytest_args_path)
					)

				# Calcolo della Coverage sui tests Umani
				if not has_human_cov_calc:
					calculate_human_coverage(
						tests_root,
						focal_root,
						"coverage_human.dat",
						"coverage_human.json",
						full_root,
						python_exepath=venv_py_exepath,
						cov_general_args=coverage_args.get("general", None),
						cov_run_args=coverage_args.get("run", None),
						pytest_args=pytest_args
					)
					has_human_cov_calc = True

				# Calcolo della Coverage sui tests generati dallo specifico LLM
				calculate_llm_coverage(
					model_normname,
					gentests_root,
					focal_root,
					full_root,
					python_exepath=venv_py_exepath,
					cov_general_args=coverage_args.get("general", None),
					cov_run_args=coverage_args.get("run", None),
					pytest_args=pytest_args
				)