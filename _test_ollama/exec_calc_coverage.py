from typing import List, Dict, Tuple, Any
from coverage import Coverage, CoverageData, exceptions as covex

from configuration import read_json_tobuff
from json import (
	loads as json_loads
)

from os import (
	walk as os_walk,
	makedirs as os_mkdirs,
)
from shutil import (
	rmtree as os_dremove
)
from os.path import (
	sep as path_sep,
	altsep as path_altsep,
	exists as os_fdexists,
	join as path_join,
	split as path_split,
	splitext as path_split_ext
)

if __name__ == "__main__":
	cover_measurer: Coverage = Coverage(
		config_file=False,
		cover_pylib=False,
		branch=True
	)

	dirs_config: Dict[str, str] = json_loads(
		read_json_tobuff("config/general.json")
	)
	#cover_dirname: str = dirs_config["coverage_dir"]

	projs_config: Dict[str, Dict[str, Any]] = json_loads(
		read_json_tobuff("config/projs.json")
	)

	models_list: List[str] = json_loads(
		read_json_tobuff("config/models.json")
	)

	gentests_dirname: str = dirs_config["gen_tests_dir"]
	eff_gentests_dirname: str

	focal_root: str
	gentests_root: str

	project_names: List[str] = list(projs_config.keys())
	for model in models_list:
		model_dirname = model.replace(":", "_")

		eff_gentests_dirname = path_join(
			gentests_dirname,
			model_dirname
		)

		for project_name in project_names:
			focal_root = projs_config[project_name]["focal_root"]
			tests_root = projs_config[project_name]["focal_root"]

			gentests_root = path_join(
				path_split(focal_root)[0],
				eff_gentests_dirname
			)

			cover_measurer