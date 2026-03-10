from .i_buildcache_cleaner import IBuildCacheCleaner

from subprocess import run as subp_run



class PodmanGe400BuildCacheCleaner(IBuildCacheCleaner):
	"""
		Rappresenta `IBuildCacheCleaner` per il "Container Manager" Podman
		la cui versione è ">=4.0"
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo PodmanGe40BuildCacheCleaner
		"""
		pass
	
	
	def clean_buildcache(self):
		subp_run(["podman", "builder", "prune"])


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================