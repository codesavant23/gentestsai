from enum import Enum as PythonEnumerator



class EParserFiletype(PythonEnumerator):
	"""
		Rappresenta un tipo di file di cui si richiede il parser per i files
		di configurazione
	"""
	JSON = 0,