from typing import Tuple



class LintingRelatedProblem:
	"""
		Rappresenta un problema (errore) identificato durante l'esecuzione
		della fase di "linting" del codice di una test-suite parziale
	"""


	def __init__(
			self,
			short_name: str,
			message: str,
			line_num: int,
			col_num: int,
	):
		"""
			Crea un nuovo LintingRelatedProblem

			Parameters
			----------
				short_name: str
					Il nome "corto", o per meglio dire "simbolico", dell' errore verificatosi

				message: str
					Il messaggio associato all' errore verificatosi

				line_num: int
					Il numero della linea in cui si è verificato l'errore

				col_num: int
					Il numero della colonna in cui si è verificato l' errore
		"""
		self._short_name: str = short_name
		self._message: str = message
		self._line_num: int = line_num
		self._col_num: int = col_num


	def get_short_name(self) -> str:
		"""
			Restituisce il nome breve dell' errore, di linting, rappresentato

			Returns
			-------
				str
					Una stringa contenente il nome breve dell' errore
		"""
		return self._short_name


	def get_message(self) -> str:
		"""
			Restituisce il messaggio associato all' errore, di linting, rappresentato

			Returns
			-------
				str
					Una stringa contenente il messaggio associato all' errore
		"""
		return self._message


	def get_code_position(self) -> Tuple[int, int]:
		"""
			Restituisce la posizione, nel codice associato, in cui si è verificato
			l' errore di linting rappresentato

			Returns
			-------
			Tuple[int, int]
				Una tupla di interi contenente:

					- [0]: Il numero di riga in cui si è verificato l' errore
					- [1]: Il numero di colonna in cui si è verificato l' errore
		"""
		return (self._line_num, self._col_num)