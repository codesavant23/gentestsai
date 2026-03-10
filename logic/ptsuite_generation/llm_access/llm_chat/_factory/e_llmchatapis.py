from enum import Enum as PythonEnumerator



class ELlmChatApis(PythonEnumerator):
	"""
		Rappresenta una strategia di selezione degli oggetti `ILlmChat`, basata sulle API
		a cui l’ instanza concreta si richieda che sia legata.
	"""
	OLLAMA = 0,