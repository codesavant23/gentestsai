from .. import ILlmSpecImpl

from .....variability import ESpecLlmImpl



class ILlmSpecImplFactory:
	"""
		Rappresenta una factory per ogni `ILlmSpecImpl`.
		
		Le specifiche API, alle quali è legata sono legate le implementazioni specifiche istanziate,
		sono descritte dai discendenti di questa interfaccia
	"""
	
	
	def create(
			self,
			model: ESpecLlmImpl,
	) -> ILlmSpecImpl:
		"""
			Istanzia una nuova implementazione specifica legata alle piattaforme descritte
			dai discendenti di questa interfaccia
			
			Parameters
			----------
				model: ESpecLlmImpl
					Un valore `ESpecLlmImpl` rappresentante l' implementazione specifica del
					Large Language Model di cui ottenere l' oggetto `ILlmSpecImpl`
					
			Returns
			-------
				ILlmSpecImpl
					Un oggetto `ILlmSpecImpl`, legato alle piattaforme specificate dai discendenti
					di questa interfaccia, che rappresenta l' implementazione specifica di LLM richiesta
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `model` fornito ha valore `None`
						- Il parametro `model` fornito è una stringa vuota
						
				NotImplementedError
					Si verifica se l' implementazione di LLM richiesta non è implementata, in GenTestsAI,
					per la combinazione di piattaforme specificate dai discendenti di questa interfaccia
		"""
		pass
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================