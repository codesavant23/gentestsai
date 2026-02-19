from enum import Enum as PythonEnumerator



class EPlatSpecCfgPurpose(PythonEnumerator):
	"""
		Rappresenta un scopo di un file di configurazione che è legato a una
		piattaforma specifica
	"""
	PLATFORM_CONFIG = 0,
	GENERAL_CONFIG = 1,
	MODELS_CONFIG = 2,