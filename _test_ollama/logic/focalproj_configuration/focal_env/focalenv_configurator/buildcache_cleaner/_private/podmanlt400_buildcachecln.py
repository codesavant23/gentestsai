from .i_buildcache_cleaner import IBuildCacheCleaner

from subprocess import (
	DEVNULL,
	run as subp_run
)
OS_DEVNULL = DEVNULL



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
		subp_run(
			"podman images -a --format \"{{.ID}} {{.Tag}}\" | "
			"awk '$2 == \"<none>\" {print $1}' | "
			"xargs -r podman rmi -f",
			shell=True,
			check=True,
			stdout=DEVNULL,
			stderr=DEVNULL
		)
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================