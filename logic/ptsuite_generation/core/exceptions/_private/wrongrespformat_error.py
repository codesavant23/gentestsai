class WrongResponseFormatError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando il formato
		della risposta di un LLM non è quello previsto in base alle istruzioni
		fornite nel prompt datogli
	"""
	pass