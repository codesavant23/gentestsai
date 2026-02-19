class TransactionStartedError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando è in corso una transazione
		di comandi shell e si prova a eseguire un' operazione che non ne dovrebbe avere una in corso.
	"""
	pass