class CoverageNotEvaluatedError(Exception):
	"""
		Rappresenta un' eccezione (non-exiting) che si verifica quando viene chiamata un' operazione
		senza aver effettuato precedentemente una valutazione della coverage
	"""
	pass