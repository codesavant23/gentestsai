from .i_moddecls_extr_f import IModuleDeclsExtractorFactory
from .e_moddeclsextr_chars import EModuleDeclsExtractorChars

from .mutable_moddeclsextr_f import MutableModuleDeclsExtractorFactory



class ModuleDeclsExtractorFactoryResolver:
	"""
		Rappresenta una factory per ogni `IModuleDeclsExtractorFactory`
	"""
	
	
	@classmethod
	def create(
			cls,
			chars: EModuleDeclsExtractorChars,
	) -> IModuleDeclsExtractorFactory:
		"""
			Istanzia un nuovo estrattore di codice focale dei moduli che ha le specifiche
			caratteristiche astratte fornite
			
			Parameters
			----------
				chars: EModuleDeclsExtractorChars
					Un valore `EModuleDeclsExtractorChars` rappresentante l'insieme di
					caratteristiche astratte che l' oggetto `IModuleDeclsExtractor` ha
					
			Returns
			-------
				IModuleDeclsExtractorFactory
					Un oggetto `IModuleDeclsExtractorFactory` che permette di istanziare
					estrattori del codice focale aventi le caratteristiche astratte specificate
		"""
		obj_f: IModuleDeclsExtractorFactory
		match chars:
			case EModuleDeclsExtractorChars.MUTABLE:
				obj_f = MutableModuleDeclsExtractorFactory()
		
		return obj_f
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================