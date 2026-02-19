from typing import List

from .. import ILlmHyperParamFactory
from .....variability.combinatorial import (
	EModelCombo, EPlatformCombo, EModelPlatformCombo
)

from .._factory.ollama_hparam_f import OllamaHyperParamFactory



class LlmHyperParamFactoryResolver:
	"""
		Rappresenta una factory di `ILlmHyperParamFactory`
	"""
	
	
	@classmethod
	def resolve(
			cls,
	        models_apis: str
	) -> ILlmHyperParamFactory:
		"""
			Istanzia una nuova `ILlmHyperParamFactory` della combinazione modelli/piattaforme richiesta
			
			Parameters
			----------
				models_apis: str
					Una stringa rappresentante i modelli e/o piattaforme di cui ottenere
					la factory di iperparametri.
					Se sia i modelli che le piattaforme sono specificate la stringa
					è semicolon-separated tra le due parti ("<models>;<apis>")
					
			Returns
			-------
				ILlmHyperParamFactory
					Un oggetto `ILlmHyperParamFactory` che permette di istanziare iperparametri
					dei modelli/piattaforme selezionati richiesti
					
			Raises
			------
				ValueError
					Si verifica se:
						
						- Il parametro `models_apis` ha valore `None`
						- Il parametro `models_apis` è una stringa vuota
						- Il parametro `models_apis`, nel caso in cui non abbia 2 parti, non rappresenta
						  una combinazione di piattaforme, o di modelli, valida
						  
				NotImplementedError
					Si verifica se la factory della combinazione modelli/piattaforme richiesta non è
					implementata attualmente, o non esiste, in GenTestsAI
		"""
		obj_f: ILlmHyperParamFactory
		
		parts: List[str] = models_apis.split(";")
		for i, part in enumerate(parts):
			parts[i] = part.replace("-","_")
			parts[i] = part.replace(":", "_")
			parts[i] = part.lower().upper()
			
		if len(parts) == 2:
			obj_f = cls._create_llmsplat_factory(parts[0], parts[1])
		else:
			try:
				platforms: EPlatformCombo = EPlatformCombo[models_apis]
				obj_f = cls._create_platonly_factory(platforms)
			except KeyError:
				try:
					models: EModelCombo = EModelCombo[models_apis]
					obj_f = cls._create_llmonly_factory(models)
				except KeyError:
					raise ValueError()
			
		return obj_f
		
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================
	
	
	@classmethod
	def _create_llmsplat_factory(
			cls,
			models: str,
			apis: str
	) -> ILlmHyperParamFactory:
		models_apis_combo: EModelPlatformCombo = EModelPlatformCombo[
			"__".join([apis, models]).upper()
		]
		
		# Non ancora implementato, poichè non necessario attualmente
		match models_apis_combo:
			case None:
				pass
		
		return None


	@classmethod
	def _create_platonly_factory(
			cls,
			platforms: EPlatformCombo
	) -> ILlmHyperParamFactory:
		match platforms:
			case EPlatformCombo.OLLAMA:
				return OllamaHyperParamFactory()
	
	
	@classmethod
	def _create_llmonly_factory(
			cls,
			platforms: EModelCombo
	) -> ILlmHyperParamFactory:
		pass