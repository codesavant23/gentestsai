from abc import abstractmethod
from .. import ILlmChat



class IMixedLlmChat(ILlmChat):
	"""
		Rappresenta un `ILlmChat` che ha anche la capacità di contenere messaggi legati alla
		risposta di un tool.
		
		Le API di LLMs compatibili sono specificate dai discendenti di questa interfaccia.
	"""


	@abstractmethod
	def add_tool_response(
			self,
			tool_response: str
	):
		"""
			Aggiunge, in questa chat, un messaggio di risposta fornito da un tool chiamato dal LLM
			
			Parameters
			----------
				tool_response: str
					Una stringa, single-line o multi-line, contenente il messaggio di risposta
					fornito da un tool chiamato dal LLM
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `tool_response` ha valore `None`
						- Il parametro `tool_response` è una stringa vuota
		"""
		pass