from typing import Tuple
from abc import ABC, abstractmethod



class ISyntacticChecker(ABC):
	"""
		Rappresenta un oggetto in grado di effettuare la verifica di correttezza sintattica
		di una test-suite parziale tramite un tool di verifica.
	
		Il tool di verifica è specificato dai discendenti di questa interfaccia
	"""


	@abstractmethod
	def check_synt(
			self,
			ptsuite_code: str
	) -> Tuple[str, str]:
		"""
			Effettua il controllo di correttezza sintattica della test-suite parziale
			fornita come argomento
			
			Parameters
			----------
				ptsuite_code: str
					Una stringa contenente il codice della test-suite parziale di cui
					effettuare la verifica di correttezza sintattica
					
			Returns
			-------
				Tuple[str, str]
					Una tupla di 2 stringhe rappresentante l' eventuale primo errore evidenziato
					dalla  verifica di correttezza sintattica effettuata. Contiene opzionalmente:
						
						- [0]: Il nome della problematica riscontrata nella verifica di correttezza effettuata
						- [1]: Il messaggio associato alla problematica riscontrata nella verifica di correttezza effettuata

					Se non si è verificato nessun errore viene restituita una tupla vuota
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `ptsuite_code` ha valore `None` o è una stringa vuota
						- Il parametro `resp_timeout` ha valore minore di 1
		"""
		pass
	
	
	@abstractmethod
	def clear_resources(self):
		"""
			Ripulisce le risorse che sono state utilizzate dal verificatore
			a livello di linting
		"""
		pass