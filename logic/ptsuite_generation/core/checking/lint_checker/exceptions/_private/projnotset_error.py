class ProjectNotSetError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando non stato
		impostato un progetto focale nel verificatore di linting in esame prima
		di eseguire una determinata operazione
	"""
	pass