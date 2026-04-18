from io import BytesIO
from logic.focalproj_configuration.focal_container import FocalContainer

# ============ Path Utilities ============ #
from os.path import (
	sep as path_sep,
	altsep as path_altsep,
)
_PATH_SEPS: str = f"{path_sep}{path_altsep if path_altsep is not None else ''}"
# ======================================== #
# ============== OS Utilities ============== #
from os import remove as os_remove
from shutil import rmtree as os_dremove
# ========================================== #
from tarfile import (
	open as tarf_open,
	TarInfo
)



def write_dir_intofenv(
		src_path: str,
		src_dirname: str,
		dest_relpath: str,
		path_prefix: str,
		focal_env: FocalContainer,
		remove_src: bool=True,
		recursive: bool=True
):
	tarfile_stream: BytesIO = BytesIO()
	
	with tarf_open(fileobj=tarfile_stream, mode="w") as tfptsuite:
		tfptsuite.add(src_path, arcname=src_dirname, recursive=recursive)
	tarfile_stream.seek(0)
	
	focal_env.put_tararchive(
		f"{path_prefix}/{dest_relpath.rstrip("/")}/",
		tarfile_stream
	)
	
	if remove_src:
		os_dremove(src_path)


def write_file_intofenv(
		src_path: str,
		destfenv_relpath: str,
		dest_fname: str,
		path_prefix: str,
		focal_env: FocalContainer,
		remove_src: bool=True,
):
	tarfile_stream: BytesIO = BytesIO()
	src_content: str
	with open(src_path, "r") as fprcfile:
		src_content = fprcfile.read()
	
	content_bytes: bytes = src_content.encode("utf-8")
	with tarf_open(fileobj=tarfile_stream, mode="w") as tfptsuite:
		tarfile_info: TarInfo = TarInfo(name=dest_fname)
		tarfile_info.size = len(content_bytes)
		tfptsuite.addfile(tarinfo=tarfile_info, fileobj=BytesIO(content_bytes))
	tarfile_stream.seek(0)
	
	focal_env.put_tararchive(
		f"{path_prefix}/{destfenv_relpath.rstrip("/")}/",
		tarfile_stream
	)
	
	if remove_src:
		os_remove(src_path)