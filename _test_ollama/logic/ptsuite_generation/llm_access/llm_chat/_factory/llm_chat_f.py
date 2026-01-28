from .. import (
	ILlmChat,
	ELlmChatApis
)
from .._private.ollama_chat import OllamaLlmChat



class LlmChatFactory:
	"""
		Rappresenta una factory per ogni `ILlmChat`
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo LlmChatFactory
		"""
		pass
		
	
	@classmethod
	def create(
			cls,
			chat_apis: ELlmChatApis
	) -> ILlmChat:
		"""
			Istanzia una chat legata alle APIs specificate
			
			Parameters
			----------
				chat_apis: ELlmChatApis
					Un valore `ELlmChatApis` rappresentante le APIs legate all' oggetto `ILlmChat`
					di cui si richiede l' istanziazione
					
			Returns
			-------
				ILlmChat
					Un oggetto `ILlmChat` che permette gestisce una chat di messaggi specifica delle
					APIs richieste
		"""
		obj: ILlmChat
		match chat_apis:
			case ELlmChatApis.OLLAMA:
				obj = OllamaLlmChat()
		
		return obj
	
		
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================