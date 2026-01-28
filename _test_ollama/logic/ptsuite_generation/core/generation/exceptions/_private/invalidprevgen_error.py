class InvalidPreviousGenerationError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica se l' ultima richiesta
        di correzione effettuata è da considerarsi invalida (corrotta o non utilizzabile).
        Ciò vale anche per il riferimento ad una richiesta di correzione mai effettuata.
	"""
	pass
