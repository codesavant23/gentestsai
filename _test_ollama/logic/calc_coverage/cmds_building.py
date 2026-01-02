from typing import List



def build_calc_coverage_cmd(
		tests_root: str,
		focal_root: str,
		pythonexe_path: str = None,
		coverage_gen_args: List[str] = None,
		coverage_run_args: List[str] = None,
		pytest_args: List[str] = None,
		covdata_file: str = None,
) -> List[str]:
	"""
		Costruisce il comando per un calcolo specifico di una coverage (dei tests umani, o dei modelli).
		Il comando costruito specificherà al framework `coverage.py` di utilizzare `pytest` per l' esecuzione
		dei tests.

		Parameters
		----------
			tests_root: str
				Una stringa contenente la root path dei tests di cui calcolare la coverage rispetto al codice focale

			focal_root: str
				Una stringa contenente la root path del codice focale su cui basare il calcolo della coverage

			pythonexe_path: str
				Opzionale. Una stringa contenente la path all' interprete di Python da utilizzare per
				l'esecuzione di `coverage.py`

			coverage_gen_args: List[str]
				Opzionale. Una lista di stringhe contenente gli argomenti di `coverage.py` (ovvero generici) da
				utilizzare nel comando

			coverage_run_args: List[str]
				Opzionale. Una lista di stringhe contenente gli argomenti dell' operazione `run` di `coverage.py` da
				utilizzare nel comando

			pytest_args: List[str]
				Opzionale. Un lista di stringhe contenente gli argomenti di `pytest` eseguito da `coverage.py`

			covdata_file: str
				Opzionale. Una stringa contenente il nome del data-file in output dal calcolo della coverage
				(prima di effettuare l' operazione `coverage report`)

		Returns
		-------
			List[str]
				Una lista di stringhe, da utilizzarsi con `subprocess.run`, contenente il comando costruito

	"""
	whole_cmd: List[str]
	if pythonexe_path:
		whole_cmd = [pythonexe_path, "-m", "coverage"]
	else:
		whole_cmd = ["coverage"]

	if coverage_gen_args:
		whole_cmd.extend(coverage_gen_args)

	cov_source_flag: str = "--source=" + focal_root
	whole_cmd.extend(["run", cov_source_flag])

	if covdata_file:
		cov_datafile_flag: str = "--data-file=" + covdata_file
		whole_cmd.append(cov_datafile_flag)
	if coverage_run_args:
		whole_cmd.extend(coverage_run_args)

	whole_cmd.extend(["-m", "pytest"])

	if pytest_args:
		whole_cmd.extend(pytest_args)

	whole_cmd.append(tests_root)

	return whole_cmd


def build_report_coverage_cmd(
		covdata_file: str = None
) -> List[str]:
	"""
		Costruisce il comando per effettuare il report di un data-file di coverage.

		Parameters.
		----------
			covdata_file: str
				Opzionale. Una stringa contenente il nome del data-file creato in output dal calcolo
				della coverage

		Returns
		-------
			List[str]
				Una lista di stringhe, da utilizzarsi con `subprocess.run`, contenente il comando costruito
	"""

	whole_cmd: List[str] = ["coverage", "report"]

	if covdata_file:
		cov_datafile_flag: str = "--data-file="+covdata_file
		whole_cmd.append(cov_datafile_flag)

	return whole_cmd


def build_cov2json_cmd(
		output_file: str,
		covdata_file: str = None
) -> List[str]:
	"""

		Parameters
		----------
			output_file: str
				Una stringa contenente il nome del file JSON che conterrà i dati del calcolo della
				coverage

			covdata_file: str
				Opzionale. Una stringa contenente il nome del data-file creato in output dal calcolo
				della coverage

		Returns
		-------
			List[str]
				Una lista di stringhe, da utilizzarsi con `subprocess.run`, contenente il comando costruito
	"""
	whole_cmd: List[str] = ["coverage", "json"]

	if covdata_file:
		cov_datafile_flag: str = "--data-file="+covdata_file
		whole_cmd.append(cov_datafile_flag)

	whole_cmd.append("--output="+output_file)

	return whole_cmd