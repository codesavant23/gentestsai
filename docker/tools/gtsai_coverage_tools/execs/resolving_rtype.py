from typing import Dict
from ..coverage_evaluation import ECoverageReportType



def resolve_report_type(report_type: str) -> ECoverageReportType:
	"""
		Risolve il tipo di report di coverage da produrre in seguito al
		calcolo della coverage tramite "coverage.py"
		
		Parameters
		----------
			report_type: str
				Una stringa contenente il tipo di report da produrre
				
		Returns
		-------
			ECoverageReportType
				Un valore `ECoverageReportType` rappresentante il tipo di report
				da produrre in seguito al calcolo della coverage
				
		Raises
		------
			NotImplementedError
				Si verifica se il parametro `report_type` rappresenta un tipo
				di report non supportato
	"""
	
	report_type_e: ECoverageReportType
	
	resolver: Dict[str, ECoverageReportType] = {
		"json": ECoverageReportType.JSON,
		"html": ECoverageReportType.HTML,
		"xml": ECoverageReportType.XML,
		"lcov": ECoverageReportType.LCOV,
		"annotate": ECoverageReportType.ANNOTATE
	}
	
	try:
		report_type_e = resolver[report_type]
	except KeyError:
		raise NotImplementedError(f"Unknown coverage report type: {report_type}")
	
	return report_type_e