class NotWritableStreamError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando viene 
		eseguita un' operazione a cui è stato fornito uno stream di output
		non scrivibile (mentre ne richiede uno scrivibile)
	"""
	pass
