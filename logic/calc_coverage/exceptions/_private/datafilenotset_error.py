class DataFileNotSetError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando viene chiamata
		un' operazione senza aver prima impostato la path del data-file richiesto di
		coverage.py
	"""
	pass