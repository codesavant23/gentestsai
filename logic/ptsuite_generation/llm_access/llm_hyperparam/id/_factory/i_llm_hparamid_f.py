from .. import ILlmHyperParamId



class ILlmHyperParamIdFactory:
	"""
		Rappresenta una factory per ogni `ILlmHyperParamId`.
		
		I modelli e/o le specifiche APIs, a cui appartengono gli iperparametri istanziati,
		sono descritti/e dai discendenti di questa interfaccia.
	"""
	
	
	def create(
			self,
			param_id: str,
	) -> ILlmHyperParamId:
		"""
			Istanzia un nuovo identificatore di un iperparametro, legato alla piattaforma/modelli
			descritti dai discendenti di questa interfaccia
			
			Parameters
			----------
				param_id: str
					Una stringa contenente il naming dell' iperparametro da richiedere
					
			Returns
			-------
				ILlmHyperParamId
					Un oggetto `ILlmHyperParamId`, legato alla piattaforma/LLMs specificati dai discendenti
					di questa interfaccia, che rappresenta l' iperparametro richiesto
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `param_id` fornito ha valore `None`
						- Il parametro `param_id` fornito è una stringa vuota
						
				NotImplementedError
					Si verifica se l' identificatore di iperparametro richiesto non è implementato, in GenTestsAI,
					per la piattaforma/modelli specificati dai discendenti di questa interfaccia
		"""
		pass
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================