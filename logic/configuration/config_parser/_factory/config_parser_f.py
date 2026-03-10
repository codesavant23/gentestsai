from .. import IConfigParser
from .e_parser_ftype import EParserFiletype

from .._private.json_cfgparser import JsonConfigParser



class ConfigParserFactory:
	"""
		Rappresenta una factory per ogni `IConfigParser`
	"""
		
	
	@classmethod
	def create(
			cls,
			ftype: EParserFiletype
	) -> IConfigParser:
		"""
			Istanzia un nuovo parser di file di configurazione per il file-type specificato
			
			Parameters
			----------
				ftype: EParserFiletype
					Un valore `EParserFiletype` rappresentante il tipo di file parsabile
					dall' oggetto `IConfigParser` richiesto
					
			Returns
			-------
				IConfigParser
					Un oggetto `IConfigParser` che permette di parsare files di configurazione
					del file-type specificato
		"""
		obj: IConfigParser
		match ftype:
			case EParserFiletype.JSON:
				obj = JsonConfigParser()
			
		return obj
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================