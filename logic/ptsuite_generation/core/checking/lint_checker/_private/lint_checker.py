from typing import Dict

# ============== Docker SDK Utilities =============== #
from docker.models.images import Image as DockerImage
# =================================================== #
# ============== OS Utilities ============== #
from os import makedirs as os_mkdirs
from os.path import exists as os_fdexists
from shutil import rmtree as os_dremove
# ========================================== #
# ============ Path Utilities ============ #
from os.path import (
	join as path_join,
	split as path_split,
	splitext as path_splitext,
	relpath as path_relative
)
# ======================================== #
# ============== JSON Utilities ============== #
from json import JSONDecoder
# ============================================ #
from datetime import datetime as DateTime

from ......utils.logger import ATemporalFormattLogger
from ......utils.logger.exceptions import FormatNotSetError

from ......focalproj_configuration.focal_container import FocalContainer

from ..exceptions import ProjectNeverSetError



class LintingChecker:
	"""
		Rappresenta un oggetto in grado di effettuare la verifica di correttezza,
		a livello di linting, di test-suites parziali tramite un tool di verifica
		installato all' interno dell' ambiente focale.
		
		Attributi di Classe Pubblici:
			- `LINTING_TEMP_DIR` (str) : Rappresenta il nome, di default, della directory temporanea, nel container, in cui verranno memorizzati i files usati temporaneamente durante la verifica del codice
			- `LINTING_SCRIPT` (str) : Rappresenta il nome, di default, dello script Python, contenuto nella directory dei tools per la verifica a livello di linting, che eseguirà la verifica nell' ambiente del progetto focale tramite gli strumenti scelti
	"""
	
	_RESULT_FNAME: str = "gtsai__linting_result.json"
	
	def __init__(
			self,
			fenv_script_fname: str,
			shared_dirname: str,
	        logger: ATemporalFormattLogger = None,
	):
		"""
			Costruisce un nuovo LintingChecker associandolo eventualmente al logger utilizzato per registrare
			gli steps di ogni verifica a livello di linting effettuata.
			
			Parameters
			----------
				fenv_script_fname: str
					Una stringa contenente il nome dello script Python che esegue la verifica di correttezza,
					a livello di linting, all' interno dell' ambiente focale
			
				shared_dirname: str
					Una stringa rappresentante il nome della directory-volume, all' interno del path prefix dell' ambiente focale,
					che conterrà la copia temporanea delle test-suites parziali di cui effettuare la verifica di linting.
			
				logger: ATemporalFormattLogger
					Opzionale. Default = `None`. Un oggetto `ATemporalFormattLogger` rappresentante l' eventuale logger
					da utilizzare per registrare le fasi di ogni tentativo di correzione (non per registrare le fasi
					della richiesta al LLM)
					
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `fenv_script_fname` ha valore `None`
						- Il parametro `fenv_script_fname` è una stringa vuota
						- Il parametro `shared_dirname` ha valore `None`
						- Il parametro `shared_dirname` è una stringa vuota
		"""
		if(fenv_script_fname is None) or (fenv_script_fname == ""):
			raise ValueError()
		if(shared_dirname is None) or (shared_dirname == ""):
			raise ValueError()
		
		self._focal_env: FocalContainer = None
		
		# Attributi relativi al progetto focale impostato
		self._proj_name: str = None
		self._full_root: str = None
		self._focal_env: FocalContainer = None
		
		self._shared_dir: str = shared_dirname
		
		# Nome dello script Python che esegue il linter all' interno dell' ambiente focale
		self._fenv_script_fname: str = fenv_script_fname
		
		# Path (reale) del file con la test-suite parziale per la verifica di linting
		self._ptsuite_path: str = None
		# Path (reale) del risultato della verifica di linting effettuata
		self._lint_result_path: str = None
		# Path (relativa) del file con la test-suite parziale per la verifica di linting
		self._ptsuite_relpath: str = None
		# Path (relativa) del risultato della verifica di linting effettuata da un singolo tentativo
		self._lint_result_relpath: str = None
		
		# Logger da utilizzare per loggare gli steps di ogni verifica
		self._logger: ATemporalFormattLogger = logger
		
		# Setup del formato del logger
		def_time_format: str = "( {day}-{month}-{year} | {hour}:{min}:{second} )"
		logger_frmt: str
		try:
			logger_frmt = self._logger.unset_format() if logger is not None else None
		except FormatNotSetError:
			logger_frmt = "[LintingChecker] {message} " + def_time_format
		self._logger.set_format(logger_frmt) if logger is not None else None
		
		self._inited: bool = False
		self._proj_everset: bool = False
	
	
	def set_focal_project(
			self,
			project_name: str,
			full_root: str,
			env_image: DockerImage,
			path_prefix: str
	):
		"""
			Imposta il prossimo progetto focale delle quali test-suites parziali si richiederà
			la verifica di correttezza a livello di linting.
			Viene impostato anche l' ambiente focale, associato a questo progetto, che contiene
			il tool di verifica di linting
			
			Parameters
			----------
				project_name: str
					Una stringa contenente il nome del prossimo progetto focale a cui appartengono
					le test-suites parziali di cui si richiederà la verifica di correttezza
			
				full_root: str
					Una stringa contenente la Full Project Root Path del progetto focale a cui
					appartengono le test-suites parziali
					
				env_image: DockerImage
					Un oggetto `docker.models.images.Image` rappresentante l' immagine docker,
					pre-configurata, da utilizzare come ambiente per il progetto focale
					che si sta impostando
					
				path_prefix: str
					Una stringa contenente il path prefix utilizzato come Full Project Root Path
					all' interno dell' immagine docker fornita
				
			Raises
			------
				ValueError
					Si verifica se:
					
						- I parametri stringa hanno valore `None` o sono stringhe vuote
						- Il parametro `env_image` ha valore `None`
		"""
		if ((project_name is None) or (project_name == "") or
		    (full_root is None) or (full_root == "") or
			(path_prefix is None) or (path_prefix == "")
		):
			raise ValueError()
		
		# Verifica dell' esistenza della directory dei files shared nella F.P.R.P
		if not os_fdexists(path_join(full_root, self._shared_dir)):
			raise ValueError()
		
		# Stop dell' eventuale ambiente focale precedente
		if self._focal_env is not None:
			self._logger.log("Stop dell' ambiente focale ...") if self._logger is not None else None
			self._focal_env.stop_container()
			self._logger.log(f"Ambiente focale del progetto {self._proj_name} fermato") if self._logger is not None else None
			
			del self._focal_env
		
		self._proj_name = project_name
		self._full_root = full_root
		
		# Impostazione della path che conterrà il risultato delle verifiche di linting
		# Impostazione della path del file temporaneo che conterrà le test-suites parziali
		actual_time: DateTime = DateTime.now()
		self._ptsuite_path = path_join(
			self._full_root, self._shared_dir,
			f"temp_{str(actual_time.timestamp())}.py"
		)
		self._lint_result_path = f"{self._full_root}/gtsai__results/{self._RESULT_FNAME}"
		
		# Calcolo delle paths relative (con cui si costruiranno quelle assolute dell' ambiente focale)
		self._ptsuite_relpath = path_relative(self._ptsuite_path, start=self._full_root)
		self._lint_result_relpath = path_relative(self._lint_result_path, start=self._full_root)
		
		# Creazione della directory-volume shared
		self._create_shareddir()
		
		self._focal_env = FocalContainer(
			env_image,
			self._full_root,
			path_prefix,
			self._shared_dir
		)
		
		# Avvio dell' ambiente focale (container)
		self._logger.log("Avvio dell' ambiente focale ...") if self._logger is not None else None
		self._focal_env.start_container()
		self._logger.log(f"Ambiente focale del progetto {self._proj_name} avviato") if self._logger is not None else None
		
		if not self._proj_everset:
			self._proj_everset = True


	def check_lintically(
			self,
			ptsuite_code: str
	) -> Dict[str, str]:
		"""
			Effettua il controllo di correttezza sintattica della test-suite parziale
			fornita come argomento
			
			Parameters
			----------
				ptsuite_code: str
					Una stringa contenente il codice della test-suite parziale di cui effettuare
					la verifica di correttezza sintattica
					
			Returns
			-------
				Dict[str, str]
					Un dizionario di stringhe, indicizzato da stringhe rappresentante il primo errore evidenziato
					dalla verifica di linting effettuata. Contiene opzionalmente:
						
						- "except_name": Il nome della problematica riscontrata nella verifica di linting effettuata
						- "except_mess": Il messaggio associato alla problematica riscontrata nella verifica di linting effettuata
						- "except_pos": Il numero di linea e colonna (separati da ";") in cui si trova la problematica riscontrata

					Se non si è verificato nessun errore viene restituito un dizionario vuoto
					
			Raises
			------
				ValueError
					Si verifica se il parametro `ptsuite_code` ha valore `None` o è una stringa vuota
					
				ProjectNeverSetError
					Si verifica se non è mai stato impostato un progetto focale prima di eseguire
					questa operazione
					
				OSError
					Se si verificano problemi con l' apertura, o scrittura, nel file temporaneo utilizzato
					per la verifica
		"""
		if (ptsuite_code is None) or (ptsuite_code == ""):
			raise ValueError()
		if not self._proj_everset:
			raise ProjectNeverSetError()
		if not self._inited:
			self._create_shareddir()
			
		self._logger.log(
			f"Inizio della verifica di linting ..."
		) if self._logger is not None else None
		
		self._logger.log("Scrittura della test-suite parziale nella directory-volume shared ...") if self._logger is not None else None
		with open(self._ptsuite_path, "w") as fptsuite:
			fptsuite.write(ptsuite_code)
			fptsuite.flush()
		self._logger.log("Scrittura eseguita") if self._logger is not None else None
		
		# Richiesta della verifica della correttezza (a livello di linting)
		self._logger.log("Esecuzione della verifica di linting ...") if self._logger is not None else None
		self._focal_env.execute(
			f"/bin/bash -c 'python -m $LINTTOOLS_DIRNAME.{path_splitext(self._fenv_script_fname)[0]} "
			f"{self._ptsuite_relpath} {self._lint_result_relpath}'"
		)
		self._logger.log("Verifica di linting eseguita") if self._logger is not None else None
		
		# Lettura del risultato della verifica di correttezza
		self._logger.log("Lettura del risultato della verifica ...") if self._logger is not None else None
		json_dec: JSONDecoder = JSONDecoder()
		result: Dict[str, str] = None
		with open(self._lint_result_path, "r") as fjson:
			result = json_dec.decode(fjson.read())
		self._logger.log("Risultato della verifica letto") if self._logger is not None else None
		
		self._logger.log("Fine della verifica di linting") if self._logger is not None else None
		return result
	
	
	def clear_resources(self):
		"""
			Ripulisce le risorse che sono state utilizzate dal verificatore
			a livello di linting
		"""
		if self._focal_env is not None:
			self._logger.log("Stop dell' ambiente focale ...") if self._logger is not None else None
			self._focal_env.stop_container()
			self._logger.log(f"Ambiente focale del progetto {self._proj_name} fermato") if self._logger is not None else None
		
		os_dremove(
			path_split(self._ptsuite_path)[0], ignore_errors=False
		)
		self._inited = False
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _create_shareddir(self):
		"""
			Crea la directory temporanea per i files necessari all' esecuzione
			della verifica a livello di linting
		"""
		shared_path: str = path_join(self._full_root, self._shared_dir)
		os_dremove(shared_path, ignore_errors=False)
		os_mkdirs(shared_path)
		
		self._inited = True