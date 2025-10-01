from os import (
	name as os_name
)
from shutil import (
	which as os_cmdwhere
)

from subprocess import (
	run as subp_run,
	CalledProcessError
)



def _is_wsl_installed() -> bool:
	return os_cmdwhere("wsl") is not None


def configure_project_environ(
		covconfig_mainscript_path: str,
		full_root: str
):
	if (not (os_name == "posix")) and (not (os_name == "nt")):
		raise OSError("Sistema operativo '" + os_name + "' non supportato!")

	executer: str
	if os_name == "nt":
		if not _is_wsl_installed():
			raise Exception("E' necessario installare Windows Subsystem for Linux (WSL)")
		else:
			executer = "wsl"
	else:
		executer = "bash"

	subp_run([
		executer, covconfig_mainscript_path, full_root
	], check=True)