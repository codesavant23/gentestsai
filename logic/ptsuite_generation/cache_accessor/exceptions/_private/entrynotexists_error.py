class EntryNotExistsError(Exception):
	"""
	    Rappresenta un' eccezione (non-exiting) che si verifica se si tenta di accedere ad un
	    tentativo di produzione, di una test-suite parziale, non esistente nello spazio
	    di memorizzazione indicato per la cache in esame
	"""
	pass