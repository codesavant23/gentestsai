class ContainerAlreadyRunningError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando viene eseguita
		un' operazione che necessita che un container docker, legato ad un progetto focale,
		non sia in esecuzione
	"""
	pass