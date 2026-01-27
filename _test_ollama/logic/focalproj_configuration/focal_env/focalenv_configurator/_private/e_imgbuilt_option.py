from enum import Enum as PythonEnumerator



class EImageBuiltOption(PythonEnumerator):
	"""
		Rappresenta una scelta di steps da eseguire dopo la costruzione
		dell' immagine dell' ambiente focale.
	"""
	DOCKF_REMOVE = 0,
	NO_DOCKIGNORE = 1,
	DOCKIGNORE = 2