from typing import List

# ============== OS Utilities ============== #
from os import environ as os_envvar
# ========================================== #
from shutil import which as os_which
from subprocess import check_output as subp_runout

from .._private.i_buildcache_cleaner import IBuildCacheCleaner
from .._private.docker_buildcachecln import DockerBuildCacheCleaner
from .._private.podmanlt400_buildcachecln import PodmanLt400BuildCacheCleaner
from .._private.podmange400_buildcachecln import PodmanGe400BuildCacheCleaner



class BuildCacheCleanerFactory:
	"""
		Rappresenta una factory per ogni `IBuildCacheCleaner`
	"""
	
	
	@classmethod
	def obtain(cls) -> IBuildCacheCleaner:
		"""
			Istanzia un nuovo pulitore della cache di building del "Container Manager" utilizzato
			dal sistema operativo.
			Se Docker e almeno un "Container Manager" compatibile con esso (es. Podman) sono disponibili,
			questa factory dà priorità a Docker.
					
			Returns
			-------
				IBuildCacheCleaner
					Un oggetto `IBuildCacheCleaner` che permette la pulizia della building
					cache del "Container Manager" che è stato scelto per essere utilizzato
					
			Raises
			------
				NotImplementedError
					Si verifica se il sistema operativo utilizza un "Container Manager"
					il cui ottenimento non è ancora implementato
		"""
		obj: IBuildCacheCleaner
		
		cont_manager: str
		if os_which("docker") is not None:
			cont_manager = "docker"
		elif os_which("podman") is not None:
			cont_manager = "podman"
		else:
			raise NotImplementedError()
		
		match cont_manager:
			case "docker":
				obj = DockerBuildCacheCleaner()
			case "podman":
				version: List[str] = (subp_runout(['podman', 'version', '--format', '"{{.Client.Version}}"'], text=True).strip()
				                      .split("."))
				if int(version[0]) >= 4:
					obj = PodmanGe400BuildCacheCleaner()
				else:
					obj = PodmanLt400BuildCacheCleaner()
				
		return obj
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================