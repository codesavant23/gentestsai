from enum import Enum as PythonEnumerator



class ECoverageReportType(PythonEnumerator):
	"""
		Rappresenta una tipologia di report supportata da coverage.py
	"""
	HTML = 0,
	XML = 1,
	JSON = 2,
	ANNOTATE = 3,
	LCOV = 4