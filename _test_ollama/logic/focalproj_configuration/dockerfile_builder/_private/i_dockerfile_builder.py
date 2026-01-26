from typing import List, Dict
from abc import ABC, abstractmethod



class IDockfBuilder(ABC):
	"""
		Rappresenta un oggetto capace di costruire dockerfiles incrementalmente.
		All' istanziazione di ogni IDockfBuilder esso è già inizializzato per poter iniziare la
		costruzione incrementale del primo dockerfile.
		
		La tecnologia implementativa di memorizzazione delle istruzioni è specificata dagli
		implementatori di questa interfaccia
	"""

	
	@abstractmethod
	def new_dockerfile(self):
		"""
			Inizializza il builder per la creazione di un nuovo dockerfile azzerando ogni istruzione
			del dockerfile costruito in precedenza
		"""
		pass
		

	@abstractmethod
	def set_base_image(self, base_image: str):
		"""
			Imposta una nuova immagine base su cui si baserà il prossimo dockerfile che verrà costruito.
			La chiamata a questo metodo equivale all' aggiunta/modifica dell' istruzione `FROM base_image`
			nel dockerfile risultante

			Parameters
			----------
				base_image: str
					Una stringa contenente il nome dell' immagine base per le immagini derivanti
					dal dockerfile che verrà costruito successivamente.
					
			Raises
			------
				ValueError
					Si verifica se:
						
						- Il parametro `base_image` ha valore `None`
						- Il parametro `base_image` è una stringa vuota
		"""
		pass


	@abstractmethod
	def set_envvar(self, var_name: str, value: str):
		"""
			Aggiunge/modifica la definizione di una variabile d'ambiente shell (visibile anche nel dockerfile).
			La chiamata a questo metodo equivale all' aggiunta/modifica dell' istruzione `ENV var_name=value`
			nel dockerfile risultante, corrispondente al `var_name` specificato.
			Se si specifica una nuova variabile d' ambiente viene aggiunto un nuovo layer al dockerfile.
			
			Se `value` ha valore `None` allora si rimuove la variabile d' ambiente corrispondente
			(e il layer corrispondente)

			Parameters
			----------
				var_name: str
					Una stringa contenente la variabile d' ambiente di cui aggiungere/modificare la definizione

				value: str
					Una stringa contenente il valore da impostare per la variabile d' ambiente
					
			Raises
			------
				ValueError
					Si verifica se:
						
						- Il parametro `var_name` ha valore `None` o è una stringa vuota
						- Il parametro `value` è una stringa vuota
		"""
		pass


	@abstractmethod
	def add_shellcmd(self, shell_cmd: str):
		"""
			Aggiunge l'esecuzione di un comando shell al dockerfile che verrà costruito.
			La chiamata a questo metodo equivale all' aggiunta di un istruzione `RUN shell_cmd`
			nel dockerfile risultante.
			Viene aggiunto un nuovo layer al dockerfile.

			Parameters
			----------
				shell_cmd: str
					Una stringa contenente il comando che deve essere eseguito
					
			Raises
			------
				ValueError
					Si verifica se:
						
						- Il parametro `shell_cmd` ha valore `None`
						- Il parametro `shell_cmd` è una stringa vuota
		"""
		pass


	@abstractmethod
	def set_global_args(self, global_args: Dict[str, str]):
		"""
			Imposta dei nuovi argomenti globali per il prossimo dockerfile che verrà costruito.
			La chiamata a questo metodo equivale all' aggiunta/modifica dell' istruzione `ARG <key>=<value>`
			nel dockerfile risultante, relativa alla chiave di `global_args` di nome "`<key>`".
			
			Ogni chiave impostata a `None` equivale alla rimozione dell' argomento globale corrispondente

			Parameters
			----------
				global_args: Dict[str, str]
					Un dizionario di stringhe, indicizzato da stringhe, contenente gli argomenti globali
					da impostare nel prossimo dockerfile prodotto
					
			Raises
			------
				ValueError
					Si verifica se:
						
						- Il parametro `global_args` ha valore `None`
						- Il parametro `global_args` è un dizionario vuoto
		"""
		pass
	
	
	@abstractmethod
	def add_copy(self, sources: List[str], dest: str):
		"""
			Aggiunge una richiesta di copia del contenuto delle directories al dockerfile costruito successivamente.
			La chiamata a questo metodo equivale all' aggiunta di un istruzione `COPY` nel dockerfile risultante.
			Viene aggiunto un nuovo layer al dockerfile
			
			Parameters
			----------
				sources: List[str]
					Una lista di stringhe rappresentante le paths di cui copiare il contenuto all' interno
					della destinazione
					
				dest: str
					Una stringa rappresentante la path in cui copiare il contenuto delle sorgenti
					
			Raises
			------
				ValueError
					Si verifica se:
						
						- Il parametro `sources` ha valore `None` o è una lista vuota
						- Se una delle paths di `sources` è `None` o è una stringa vuota
						- Il parametro `dest`  ha valore `None` o è una stringa vuota
		"""
		pass
	
	
	@abstractmethod
	def add_workdir(self, dest: str):
		"""
			Aggiunge una richiesta di spostamento della working directory nella directory specificata.
			La chiamata a questo metodo equivale all' aggiunta di un istruzione `WORKDIR` nel dockerfile risultante.
			Viene aggiunto un nuovo layer al dockerfile
			
			Parameters
			----------
				dest: str
					Una stringa rappresentante la path di destinazione in cui spostarsi (durante la costruzione
					dell' immagine risultante dal dockerfile successivo)
					
			Raises
			------
				ValueError
					Si verifica se:
						
						- Il parametro `dest` ha valore `None`
						- Il parametro `dest` è una stringa vuota
		"""
		pass
	
	
	@abstractmethod
	def set_entrypoint(
			self,
	        entry_cmd: str,
			def_args: List[str]=None
	):
		"""
			Imposta l' entrypoint (processo principale) dei containers generati sulla base del dockerfile
			costruito successivamente, e eventualmente anche i suoi argomenti di default.
			La chiamata a questo metodo equivale all' aggiunta/modifica dell' istruzione `ENTRYPOINT`, e `CMD`,
			nel dockerfile risultante.
			L' istruzione `ENTRYPOINT` è scritta in Exec-Form.
			
			Parameters
			----------
				entry_cmd: str
					Una stringa contenente il comando da eseguire come processo principale del container che si basa
					sull' immagine costruita dal dockerfile costruito successivamente
					
				def_args: List[str]
					Opzionale. Default = `None`. Una lista di stringhe che contiene gli argomenti di default da passare
					al comando da eseguire come processo principale (vengono scritti nell' istruzione `CMD`).
					Possono essere sovrascritti dal comando `docker run`
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- E' stata fornita una stringa vuota per `entry_cmd`
						- E' stata fornita una lista vuota per `def_args`
		"""
		pass
	
	
	@abstractmethod
	def build_dockerfile(
			self,
	        dockf_path: str,
	):
		"""
			Costruisce il dockerfile scrivendolo nella path specificata. Il file alla path specificata
			viene troncato e poi scritto.
			
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
		pass