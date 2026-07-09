from enum import Enum as PythonEnumerator



class EPlatSpecCfgPurpose(PythonEnumerator):
	"""
		Represents the purpose of a configuration file that is associated
		with a specific platform
	"""
	PLATFORM_CONFIG = 0,
	GENERAL_CONFIG = 1,
	MODELS_CONFIG = 2,