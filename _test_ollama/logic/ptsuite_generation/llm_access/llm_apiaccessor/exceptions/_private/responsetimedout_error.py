class ResponseTimedOutError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando avviene
		un timeout nel ricevimento della risposta di un' interazione con un
		LLM
	"""
	pass