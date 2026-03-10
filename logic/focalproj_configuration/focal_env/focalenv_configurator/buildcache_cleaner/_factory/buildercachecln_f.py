from typing import List

from shutil import which as os_which
from subprocess import check_output as subp_runout

from .e_contmanager import EContainerManager

from .._private.i_buildcache_cleaner import IBuildCacheCleaner
from .._private.docker_buildcachecln import DockerBuildCacheCleaner
from .._private.podmanlt400_buildcachecln import PodmanLt400BuildCacheCleaner
from .._private.podmange400_buildcachecln import PodmanGe400BuildCacheCleaner



class BuildCacheCleanerFactory:
	"""
		Rappresenta una factory per ogni `IBuildCacheCleaner`
	"""
	
	
	@classmethod
	def obtain(cls, wanted_manager: EContainerManager=None) -> IBuildCacheCleaner:
		"""
			Istanzia un nuovo pulitore della cache di building:
			
				- O del "Container Manager" scelto
				- Oppure del "Container Manager" utilizzato dal sistema operativo
				
			Nel caso di `wanted_manager` non specificato, se Docker e almeno un "Container Manager"
			compatibile con esso (es. Podman) sono disponibili, questa factory dà priorità a Docker
			
			Parameters
			----------
				wanted_manager: EContainerManager
					Opzionale. Default = `None`. Un valore `EContainerManager` che indica il
					"Container Manager" di cui ottenere il pulitore della cache di building.
					Se non viene specificato un valore si ottiene un pulitore come specificato
					dalla descrizione sovrastante del metodo
					
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
		
		match wanted_manager:
			case EContainerManager.DOCKER:
				obj = DockerBuildCacheCleaner()
			case EContainerManager.PODMAN_GE400:
				obj = PodmanLt400BuildCacheCleaner()
			case EContainerManager.PODMAN_LT400:
				obj = PodmanLt400BuildCacheCleaner()
		if wanted_manager is not None:
			return obj
		else:
			return cls._obtain_fromos()
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	@classmethod
	def _obtain_fromos(self):
		"""
			Ottiene il pulitore della cache di building in base al "Container Manager"
			utilizzato dal sistema operativo.
			
			Se Docker e almeno un "Container Manager" compatibile con esso (es. Podman)
			sono disponibili, si dà priorità a Docker
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