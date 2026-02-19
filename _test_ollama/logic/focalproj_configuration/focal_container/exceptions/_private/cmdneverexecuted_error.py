class CommandNeverExecutedError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando viene eseguita
		un' operazione che richiede l' avvenuta esecuzione di un comando shell
	"""
	pass