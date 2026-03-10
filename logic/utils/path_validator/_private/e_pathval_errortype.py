from enum import Enum as PythonEnumerator



class EPathValidationErrorType(PythonEnumerator):
	"""
		Rappresenta una tipologia di errore che può accadere durante la validazione
		di una path di sistema
	"""
	SYNTACTIC = 0,
	NOTEXISTS = 1,
	PERMISSION = 2,
	INACCESSIBLE = 3,