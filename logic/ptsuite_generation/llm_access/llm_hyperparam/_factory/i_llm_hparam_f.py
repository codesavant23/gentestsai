from .. import ILlmHyperParam



class ILlmHyperParamFactory:
	"""
		Rappresenta una factory per ogni `ILlmHyperParam`.
		
		I modelli e/o le specifiche APIs, a cui appartengono gli iperparametri istanziati,
		sono descritti/e dai discendenti di questa interfaccia.
	"""
	
	
	def create(
			self,
			param_id: str,
	) -> ILlmHyperParam:
		"""
			Istanzia un nuovo iperparametro legato alla piattaforma/modelli descritti dai discendenti
			di questa interfaccia
			
			Parameters
			----------
				param_id: str
					Una stringa contenente il naming dell' iperparametro da richiedere
					
			Returns
			-------
				ILlmHyperParam
					Un oggetto `ILlmHyperParam`, legato alla piattaforma/LLMs specificati dai discendenti
					di questa interfaccia, che rappresenta l' iperparametro richiesto
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `param_id` fornito ha valore `None`
						- Il parametro `param_id` fornito è una stringa vuota
						
				NotImplementedError
					Si verifica se l' iperparametro richiesto non è implementato, in GenTestsAI,
					per la piattaforma/modelli specificati dai discendenti di questa interfaccia
		"""
		pass
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================