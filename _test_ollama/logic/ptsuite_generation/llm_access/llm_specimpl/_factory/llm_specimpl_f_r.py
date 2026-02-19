from .. import ILlmSpecImplFactory
from .....variability.combinatorial import EPlatformCombo

from .._factory.ollama_specimpl_f import OllamaSpecImplFactory



class LlmSpecImplFactoryResolver:
	"""
		Rappresenta una factory di `ILlmSpecImplFactory`
	"""
	
	
	@classmethod
	def resolve(
			cls,
	        platforms: EPlatformCombo
	) -> ILlmSpecImplFactory:
		"""
			Istanzia una nuova `ILlmSpecImplFactory` della combinazione di piattaforme richiesta
			
			Parameters
			----------
				platforms: EPlatformCombo
					Un valore `EPlatformCombo` rappresentante le piattaforme di cui ottenere la factory
					di implementazioni specifiche di LLMs.
					
			Returns
			-------
				ILlmSpecImplFactory
					Un oggetto `ILlmSpecImplFactory` che permette di istanziare implementazioni specifiche
					di LLMs della combinazione di piattaforme richiesta
					
			Raises
			------
				NotImplementedError
					Si verifica se la factory della combinazione di piattaforme richiesta non è
					implementata attualmente, o non esiste, in GenTestsAI
		"""
		obj_f: ILlmSpecImplFactory
		
		match platforms:
			case EPlatformCombo.OLLAMA:
				obj_f = OllamaSpecImplFactory()
			case _:
				raise NotImplementedError()
			
		return obj_f
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================