class ProjectNeverSetError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando non è mai stato
		impostato un progetto focale nel verificatore di linting in esame
	"""
	pass