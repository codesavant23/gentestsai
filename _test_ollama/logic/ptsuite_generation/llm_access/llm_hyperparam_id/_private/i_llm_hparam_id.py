from abc import ABC, abstractmethod



class ILlmHyperParamId(ABC):
	"""
		Rappresenta un oggetto che identifica un parametro specifico (parametro di decoding/campionamento,
		o iperparametro) di uno, o più, LLMs.
		Essendo la disponibilità degli iperparametri di un LLM dipendente dal modello in esame, dalla variante
		del modello che si utilizza, e dalla specifica API che fornisce l' interazione con esso;
		questa interfaccia permette di modellare i 3 fattori in modo indipendente.

		Nel caso in cui il parametro specifico venga associato a più di un LLM (o varianti) è obbligatorio
		che la semantica (significato, formato, nome e range di valori) per entrambi i LLMs sia identica.
		Questo si combina con un discorso analogo fatto per più specifiche APIs.
		
		Per ogni identificatore è presente un solo iperparametro implementato (ovvero con capacità di
		valorizzazione).

		L' iperparametro e la sua semantica rappresentati sono descritti dai discendenti
		di questa interfaccia.
		I modelli e/o le specifiche APIs, a cui appartengono l' iperparametro, sono descritti/e
		dai discendenti di questa interfaccia.
	"""


	@abstractmethod
	def name(self) -> str:
		"""
			Restituisce il nome descrivente l' iperparametro LLM-specifico rappresentato

			Returns
			-------
				str
					Una stringa, single-line, contenente il nome che descrive la semantica
					dell' iperparametro rappresentato
		"""
		pass
	
	
	@abstractmethod
	def id(self) -> str:
		"""
			Resituisce l' identificatore stringa per l' iperparametro rappresentato
			
			Returns
			-------
				str
					Una stringa, single-line, contenente l' identificatore per l' iperparametro
					rappresentato relativamente ai modelli e/o alle specifiche API a cui
					appartiene
		"""
		pass