class IncompatibleHyperparamError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando viene
		tentato di impostare un iperparametro incompatibile con la specifica implementazione
		del LLM scelto
	"""
	pass