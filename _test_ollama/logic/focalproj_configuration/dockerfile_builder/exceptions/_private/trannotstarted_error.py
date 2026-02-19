class TransactionNotStartedError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando nessuna transazione
		di comandi shell è stata iniziata e si prova a eseguire un' operazione
		che ne richiederebbe una in corso.
	"""
	pass