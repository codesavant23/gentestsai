from typing import Set, Any
from abc import ABC, abstractmethod

from ...llm_api import ILlmApi



class ILlmChat(ABC):
	"""
		Rappresenta una chat tra un utente e un Large Language Model che è legata a una, o più,
		specifiche API di Large Language Models.
		
		Quest' oggetto ha anche la capacità di fornire la chat rappresentata secondo il tipo,
		e formato, accettato dalle API di LLMs legate a questo ILlmChat.
		
		Le API di LLMs compatibili sono specificate dai discendenti di questa interfaccia.
		Il tipo dati, e formato, accettato dalle API è specificato dai discendenti di
		questa interfaccia. Nel caso di più API esse devono coincidere nel tipo dati,
		e formato, della chat che utilizzano
	"""
	
	
	@abstractmethod
	def compat_apis(self) -> Set[ILlmApi]:
		"""
			Restituisce l' insieme delle APIs di LLMs che sono compatibili
			con questo ILlmChat
			
			Returns
			-------
				Set[ILlmApi]
					Un insieme di oggetti `ILlmApi` rappresentante l' insieme degli identificatori
					di APIs con cui è compatibile questa chat
		"""
		pass


	@abstractmethod
	def clear(self):
		"""
			Azzera la chat riportandola allo stato iniziale come se fosse appena
			istanziata
		"""
		pass
	
	
	@abstractmethod
	def set_system_prompt(self, sys_prompt: str):
		"""
			Imposta il "System Prompt" (o "Context Prompt") in questa chat
			
			Parameters
			----------
				sys_prompt: str
					Una stringa, single-line o multi-line, contenente il "System Prompt" con cui contestualizzare
					questa chat
					
			Raises
			------
				ChatNotEmptyError
					Si verifica se la chat contiene già almeno un messaggio
		"""
		pass
	
	
	@abstractmethod
	def add_prompt(self, user_prompt: str):
		"""
			Aggiunge, in questa chat, un messaggio di richiesta fornito dall' utente
			
			Parameters
			----------
				user_prompt: str
					Una stringa, single-line o multi-line, contenente il messaggio di richiesta
					dell' utente
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `user_prompt` ha valore `None`
						- Il parametro `user_prompt` è una stringa vuota
		"""
		pass
	
	
	@abstractmethod
	def add_response(self, response: str):
		"""
			Registra, in questa chat, un messaggio di risposta fornito dal LLM
			
			Parameters
			----------
				response: str
					Una stringa, single-line o multi-line, contenente il messaggio di risposta del
					Large Language Model
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `response` ha valore `None`
						- Il parametro `response` è una stringa vuota
		"""
		pass
	
	
	@abstractmethod
	def get_last_prompt(self) -> str:
		"""
			Restituisce l' ultimo prompt parte di questa chat.
			
			Returns
			-------
				str
					Una stringa contenente l' ultimo prompt parte di questa chat
		"""
		pass
	
	
	@abstractmethod
	def get_last_response(self) -> str:
		"""
			Restituisce l' ultima risposta, del LLM, parte di questa chat.
			
			Returns
			-------
				str
					Una stringa contenente l' ultima risposta, del LLM, parte di questa chat
		"""
		pass
	
	
	@abstractmethod
	def chat_messages(self) -> Any:
		"""
			Restituisce la chat con la tecnologia richiesta per il suo utilizzo da parte delle
			API specifiche
			
			Returns
			-------
				Any
					Un potenziale oggetto indicante la chat di messaggi aggiunti, dopo l' ultimo `.clear()`,
					rappresentata con la tecnologia implmentativa che è richiesta dalle API specifiche
					a cui è legato questo `ILlmChat`.
					Il tipo corrispondente alla tecnologia richiesta è specificato dai discendenti
					di questa interfaccia.
		"""
		pass