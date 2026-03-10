class ModelNotSelectedError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando viene
		eseguita un' operazione senza aver mai impostato prima un LLM da utilizzare
	"""
	pass