from typing import List, Dict, Any

from os.path import (
	join as path_join,
	split as path_split,
)

from logic.utils.model_name_normalizer import normalize_model_name

from logic.utils.json_to_str import read_json_tobuff
from json import (
	loads as json_loads,
)

from pandas import (
	DataFrame as PdDataFrame
)
from pprint import pprint



def read_total_coverage(
		covjson_path: str
) -> float:
	coverage_report: Dict[str, Any] = json_loads(
		read_json_tobuff(covjson_path)
	)
	return coverage_report["totals"]["percent_covered"]


if __name__ == "__main__":
	results_path: str = "evaluation.csv"

	projs_config: Dict[str, Dict[str, Any]] = json_loads(
		read_json_tobuff("config/projs.json")
	)

	models_list: List[Dict[str, Any]] = json_loads(
		read_json_tobuff("config/models.json")
	)

	model_colnames: List[str] = list()
	model_normname: str

	new_row_idx: int = 0

	for model in models_list:
		model_name = model["name"]
		model_normname = normalize_model_name(model_name)
		model_colnames.append(model_normname)
	col_names: List[str] = ["project", "human"] + model_colnames
	results_df: PdDataFrame = PdDataFrame(columns=col_names)

	project_names: List[str] = list(projs_config.keys())

	covjson_human_file: str = "coverage_human.json"
	covjson_llm_basefile: str = "coverage_"

	covjson_file: str
	covjson_path: str

	coverage_report: Dict[str, Any]
	coverage_value: float
	current_row: Dict[str, Any]

	for project_name in project_names:
		full_root = path_split(projs_config[project_name]["focal_root"])[0]
		current_row = dict()
		current_row["project"] = project_name

		covjson_file = covjson_human_file

		covjson_path = path_join(full_root, covjson_file)
		coverage_value = read_total_coverage(covjson_path)

		current_row["human"] = coverage_value

		for model_name in model_colnames:
			covjson_file = covjson_llm_basefile + model_name + ".json"

			covjson_path = path_join(full_root, covjson_file)
			coverage_value = read_total_coverage(covjson_path)

			current_row[model_name] = coverage_value

		results_df.loc[new_row_idx] = current_row
		new_row_idx += 1
		del current_row

	results_df.to_csv(results_path, mode="w")
	pprint(results_df)