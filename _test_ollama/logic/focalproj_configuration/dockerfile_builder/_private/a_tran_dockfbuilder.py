from typing import List
from abc import abstractmethod
from ._a_base_dockfbuilder import _ABaseDockfBuilder

from ..exceptions import (
	TransactionStartedError,
	TransactionNotStartedError
)



class ATransactDockfBuilder(_ABaseDockfBuilder):
	"""
		Rappresenta un `IDockfBuilder` "transazionale" ovvero che da la possibilità di scrivere 
		transazioni di comandi shell (molteplici comandi shell eseguiti in un unico layer `RUN`).
		
		La tecnologia implementativa di memorizzazione delle istruzioni è specificata dagli
		implementatori di questa classe astratta
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo ATransactDockfBuilder
		"""
		super().__init__()
		
		self._tran_open: bool = False
		self._tran_cmds: List[str] = list()
		
		
	def begin_cmds_tran(self):
		"""
			Inizia una nuova transazione di comandi shell da apporre in un' unica istruzione `RUN`.
			La transazione fa in modo che venga aggiunto un unico, nuovo, layer al dockerfile.

			Raises
			------
				TransactionStartedError
					Si verifica se è già in corso un' altra transazione
		"""
		self._assert_transaction_not_started()

		self._tran_open = True
		self._tran_cmds.clear()


	def add_shellcmd_step(
			self,
			shell_cmd: str
	):
		"""
			Aggiunge un nuovo comando shell alla transazione in corso

			Parameters
			----------
				shell_cmd: str
					Il comando shell da aggiungere alla transazione in corso

			Raises
			------
				TransactionNotStartedError
					Si verifica se non è stata iniziata nessuna transazione
		"""
		self._assert_transaction_started()

		self._tran_cmds.append(shell_cmd)


	def commit_cmds_tran(self):
		"""
			Finalizza la transazione di comandi shell iniziata e scrive tutti i comandi shell
			in un' unica istruzione `RUN`.
			Tutti i comandi vengono concatenati con il separatore `"&&"`.

			Raises
			------
				TransactionNotStartedError
					Se non è stata iniziata nessuna transazione
		"""
		self._assert_transaction_started()

		if len(self._tran_cmds) > 0:
			self._ap__add_instr(f"RUN {" && ".join(self._tran_cmds)}")

		self._tran_open = False
	
	
	def build_dockerfile(self, dockf_path: str):
		"""
			Costruisce il dockerfile scrivendolo nella path specificata. Il file alla path specificata
			viene troncato e poi scritto.
			
			Ogni transazione di comandi shell viene forzatamente chiusa.
			
			Le variabili d' ambiente definite, vengono tutte scritte all' inizio dopo la scelta 
			dell' immagine base e delle variabili globali del dockerfile

			Parameters
			----------
				dockf_path: str
					Una stringa rappresentante la path del file che conterrà il dockerfile
					costruito incrementalmente dalla istanziazione di questo IDockfBuilder
					o dall' ultima chiamata a `.new_dockerfile(...)`

			Raises
			------
				BaseImageNotSetError
					Se non è stata impostata alcuna immagine base alla chiamata di questa
					operazione
		"""
		try:
			self.commit_cmds_tran()
		except TransactionNotStartedError:
			pass
		super().build_dockerfile(dockf_path)
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__new_dockerf_spec(self):
		pass
	
	
	@abstractmethod
	def _ap__add_instr(self, instr: str):
		pass
	
	
	@abstractmethod
	def _ap__addupd_envvar(self, var_name: str, value: str):
		pass
	
	
	@abstractmethod
	def _ap__rem_envvar(self, var_name: str):
		pass
	
	
	@abstractmethod
	def _ap__get_dockf_content(
			self,
			base_image: str,
			glob_args: str,
			epcmd_instrs: str = None
	) -> str:
		"""
			Restituisce il contenuto del dockerfile attuale per scriverlo in un file.
			
			E' garantito all' interno di questo metodo che un' eventuale transazione di comandi
			shell, che era in corso, è già stata chiusa
			
			Parameters
			----------
				base_image: str
					Una stringa contenente l' ultima immagine base impostata per il dockerfile
					che verrà costruito
					
				glob_args: str
					Una stringa contenente le istruzioni `ARG` che definiscono gli argomenti globali
					del dockerfile che verrà costruito
			
				epcmd_instrs: str
					Opzionale. Default = `None`. Una stringa contenente le eventuali istruzioni `ENTRYPOINT`+`CMD`
					da inserire nel contenuto del dockerfile
					
			Returns
			-------
				str
					Una stringa rappresentante il contenuto del dockerfile costruito
		"""
		pass
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _assert_transaction_started(
			self,
			err_msg: str = "Nessuna transazione di comandi shell è stata iniziata!"
	):
		if not self._tran_open:
			raise TransactionNotStartedError(err_msg)


	def _assert_transaction_not_started(
			self,
			err_msg: str = "E' già in corso una transazione di comandi shell!"
	):
		if self._tran_open:
			raise TransactionStartedError(err_msg)