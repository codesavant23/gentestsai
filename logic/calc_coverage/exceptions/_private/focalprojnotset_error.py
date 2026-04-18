class FocalProjectNotSetError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando viene richiesta la scrittura
		di un file "coverage.rc" senza aver precedentemente impostato un progetto focale
	"""
	pass