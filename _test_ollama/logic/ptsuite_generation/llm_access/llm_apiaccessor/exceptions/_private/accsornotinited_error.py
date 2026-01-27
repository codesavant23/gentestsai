class AccessorNotInitedError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando viene
		chiamata un' operazione senza aver mai inizializzato l' API accessor
		relativo all' operazione
	"""
	pass