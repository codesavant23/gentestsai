class IncompatibleApiError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando
		un' oggetto fornito, legato ad una o più APIs, non è compatibile con l' API
		legata all' oggetto che lancia questa eccezione
	"""
	pass