from typing import List
from .i_buildcache_cleaner import IBuildCacheCleaner

from subprocess import run as subp_run



class PodmanLt400BuildCacheCleaner(IBuildCacheCleaner):
	"""
		Rappresenta un `IBuildCacheCleaner` per il "Container Manager" Podman
		la cui versione è "<4.0"
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo PodmanLt40BuildCache
		"""
		pass
		
	
	def clean_buildcache(self):
		whole_cmd: List[str] = list()
		
		whole_cmd.append("podman images -a")
		whole_cmd.append("--format")
		whole_cmd.append('"{{.ID}} {{.Tag}}"')
		whole_cmd.append("|")
		whole_cmd.append("awk '$2 == \"<none>\" {print $1}'")
		whole_cmd.append("|")
		whole_cmd.append("xargs -r podman rmi -f")
		
		subp_run(whole_cmd)
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================