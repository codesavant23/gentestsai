from logic.focalproj_configuration.focal_container import FocalContainer
from logic.calc_coverage import CoverageRcWriter

# ============ Path Utilities ============ #
from os.path import (
	sep as path_sep,
	altsep as path_altsep,
	join as path_join,
)
_PATH_SEPS: str = f"{path_sep}{path_altsep if path_altsep is not None else ''}"
# ======================================== #

from main_execs.calc_cov import write_file_intofenv



def write_covrc(
	full_root: str,
	focal_env: FocalContainer,
	path_prefix: str,
	covrc_writer: CoverageRcWriter,
	covrc_fname: str,
	result_fname: str
):
	temp_rcfile_path: str = path_join(full_root, covrc_fname)
	covrc_writer.set_option(
		"json", "output",
		f"{path_prefix}/gtsai__results/{result_fname}"
	)

	covrc_writer.write_rcfile(temp_rcfile_path)
	
	write_file_intofenv(
		temp_rcfile_path,
		"project",
		covrc_fname,
		path_prefix,
		focal_env
	)