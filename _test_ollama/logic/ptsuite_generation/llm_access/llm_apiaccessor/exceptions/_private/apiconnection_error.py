class ApiConnectionError(ConnectionError):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando avviene
		un errore durante un tentativo di connessione con un API di LLMs.
		
		L' attirbuto `args` è valorizzato con il valore di `args` dell' eccezione
	    specifica che si è verificata con l' API (se è possibile ottenerla).
	    L' attirbuto `errno` è valorizzato con il valore di `errno` della
	    `ConnectionError` che si è verificata con l' API (se è possibile ottenerla)
	"""
	pass