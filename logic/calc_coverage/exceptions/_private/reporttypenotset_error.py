class ReportTypeNotSetError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando viene richiesta la scrittura
		di un file "coverage.rc" senza aver precedentemente impostato la tipologia di report
		desiderata
	"""
	pass