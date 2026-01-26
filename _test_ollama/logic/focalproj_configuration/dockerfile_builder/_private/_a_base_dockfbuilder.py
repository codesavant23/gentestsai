from typing import List, Tuple, Dict
from abc import abstractmethod
from .. import IDockfBuilder

# ============== JSON Utilities ============== #
from json import JSONEncoder
# ============================================ #

from ...exceptions import BaseImageNotSetError



class _ABaseDockfBuilder(IDockfBuilder):
	"""
		Rappresenta un `IDockfBuilder` di base, ovvero che contiene la logica di controllo
		comune ad ogni `IDockfBuilder`
		
		La tecnologia implementativa di memorizzazione delle istruzioni è specificata dagli
		implementatori di questa classe astratta
	"""
	
	def __init__(self):
		"""
			Costruisce un nuovo _ABaseDockfBuilder
		"""
		self._bimage: str = None
		self._glob_args: Dict[str, str] = dict()
		self._entryp: List[str] = list()
		
		
	def new_dockerfile(self):
		self._bimage = None
		
		del self._glob_args
		self._glob_args = dict()
		
		self._entryp.clear()
		
		self._ap__new_dockerf_spec()
		
	
	def set_base_image(self, base_image: str):
		if (base_image is None) or (base_image == ""):
			raise ValueError()
		
		self._bimage = base_image
	
	
	def add_copy(self, sources: List[str], dest: str):
		if (sources is None) or (len(sources) == 0):
			raise ValueError()
		if (dest is None) or (dest == ""):
			raise ValueError()
		
		sources_snized: List[str] = list(map(
			lambda source: source.rstrip("/"),
			sources
		))
		dest_snized: str = f"{dest.rstrip("/")}/"
		sources_str: str = " ".join(sources_snized)
		
		self._ap__add_instr(
			f"COPY {sources_str} {dest_snized}"
		)
	
	
	def build_dockerfile(
			self,
			dockf_path: str
	):
		if (dockf_path is None) or (dockf_path == ""):
			raise ValueError()
		if self._bimage is None:
			raise BaseImageNotSetError()
		
		entryp_cmd, entryp_args = self._get_entryp_parts()
		
		global_args: str = ""
		if len(self._glob_args.keys()) > 0:
			for glob_arg, value in self._glob_args.items():
				global_args += f"ARG {glob_arg}={value}" + "\n"
		
		dockf_content: str = self._ap__get_dockf_content(
			f'FROM {self._bimage}',
			global_args,
			f'ENTRYPOINT {entryp_cmd}'+'\n'+f'CMD {entryp_args}'
		)
		with open(dockf_path, "w") as fdockf:
			fdockf.writelines(dockf_content)
			fdockf.flush()
			
		"""
			if dockignore:
				dockf_path_nof, dockf_fname = path_split(dockf_path)
				docki_path: str = path_join(
					dockf_path_nof, ".dockignore"
				)
				with open(docki_path, "w") as fdocki:
					fdocki.write(f"./{dockf_fname}")
					fdocki.flush()
		"""
	
	
	def set_global_args(self, global_args: Dict[str, str]):
		if global_args is None:
			raise ValueError()
		if len(global_args.keys()) == 0:
			raise ValueError()
		
		for key, value in global_args.items():
			self._glob_args[key] = value
	
	
	def set_envvar(self, var_name: str, value: str):
		if (var_name is None) or (var_name == ""):
			raise ValueError()
		if (value == ""):
			raise ValueError()
		
		if value is None:
			self._ap__rem_envvar(var_name)
		else:
			self._ap__addupd_envvar(var_name, value)
	
	
	def add_shellcmd(self, shell_cmd: str):
		if (shell_cmd is None) or (shell_cmd == ""):
			raise ValueError()
		
		self._ap__add_instr(f"RUN {shell_cmd}")
	
	
	def add_workdir(self, dest: str):
		if (dest is None) or (dest == ""):
			raise ValueError()
		
		self._ap__add_instr(
			f"WORKDIR {dest.rstrip("/")}/"
		)
	
	
	def set_entrypoint(
			self,
			entry_cmd: str,
			def_args: List[str] = None
	):
		if (entry_cmd is None) or (entry_cmd == ""):
			raise ValueError()
		
		if len(self._entryp) != 0:
			del self._entryp
			self._entryp = None
		
		if def_args is not None:
			self._entryp = def_args.copy()
		else:
			self._entryp = list()
			
		self._entryp.insert(0, entry_cmd)
	
	
	##	============================================================
	##						ABSTRACT METHODS
	##	============================================================
	
	
	@abstractmethod
	def _ap__new_dockerf_spec(self):
		"""
			Inizializza il builder per la creazione di un nuovo dockerfile azzerando ogni istruzione
			del dockerfile costruito in precedenza.
			
			E' garantito all' interno di questo metodo:
				
				- Che l' immagine di base è già stata azzerata
				- Che gli argomenti globali sono già stati azzerati
				- Che l' istruzione entrypoint è già stata rimossa
		"""
		pass
	
	
	@abstractmethod
	def _ap__add_instr(self, instr: str):
		"""
			Aggiunge l' istruzione fornita, al dockerfile che si sta costruendo incrementalmente
			
			Parameters
			----------
				instr: str
					Una stringa contenente l' istruzione da aggiungere al dockerfile
					che si sta costruendo
		"""
		pass
	
	
	@abstractmethod
	def _ap__addupd_envvar(self, var_name: str, value: str):
		"""
			Aggiunge/modifica la definizione di una variabile d'ambiente shell (visibile anche nel dockerfile).
			La chiamata a questo metodo equivale all' aggiunta/modifica di un istruzione `ENV var_name=value`
			nel dockerfile risultante, corrispondente al `var_name` specificato.
			Se si specifica una nuova variabile d' ambiente viene aggiunto un nuovo layer al dockerfile.
			
			E' garantito all' interno di questo metodo:
				- Che `var_name` non ha valore `None` ne è una stringa vuota
				- Che `value` non ha valore `None` ne è una stringa vuota
			
			Parameters
			----------
				var_name: str
					Una stringa contenente la variabile d' ambiente di cui aggiungere/modificare la definizione

				value: str
					Una stringa contenente il valore da impostare per la variabile d' ambiente
		"""
		pass
	
	
	@abstractmethod
	def _ap__rem_envvar(self, var_name: str):
		"""
			Rimuove la definizione di una variabile d' ambiente shell (visibile anche nel dockerfile).
			La chiamata a questo metodo equivale alla rimozione di un istruzione `ENV var_name=value`
			nel dockerfile risultante, corrispondente al `var_name` specificato.
			Viene rimosso il layer della variabile `var_name` nel dockerfile.
			
			E' garantito all' interno di questo metodo che `var_name` non ha valore `None` ne è una stringa vuota
			
			Parameters
			----------
				var_name: str
					Una stringa contenente il nome della variabile d' ambiente che è necessario rimuovere
		"""
		pass
	
	
	@abstractmethod
	def _ap__get_dockf_content(
			self,
			base_image: str,
			glob_args: str,
	        epcmd_instrs: str=None
	) -> str:
		"""
			Restituisce il contenuto del dockerfile attuale per scriverlo in un file
			
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


	def _get_entryp_parts(self) -> Tuple[str, str]:
		"""
			Restituisce le componenti dell' istruzione `ENTRYPOINT`+`CMD`, attuale,
			da scrivere nel dockerfile
			
			Returns
			-------
				str
					Una stringa contenente l' istruzione `ENTRYPOINT` da scrivere nel dockerfile.
					Viene restituito `None` se non è impostato un entrypoint per il dockerfile
		"""
		json_enc: JSONEncoder = JSONEncoder()
		
		entryp_cmd: str = json_enc.encode(f'["{self._entryp[0]}"]')
		entryp_args: str = json_enc.encode(self._entryp[1:])
		
		return (entryp_cmd, entryp_args)