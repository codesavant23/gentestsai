class DefaultPythonVersionNotSetError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando si esegue
		un' operazione senza aver impostato prima la versione di default (fallback)
		di Python desiderata
	"""
	pass