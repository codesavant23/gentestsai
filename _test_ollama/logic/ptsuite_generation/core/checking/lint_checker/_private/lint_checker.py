from typing import Dict

# ============== Docker SDK Utilities =============== #
from docker.models.images import Image as DockerImage
# =================================================== #
# ============== OS Utilities ============== #
from os import makedirs as os_mkdirs
from shutil import rmtree as os_dremove
# ========================================== #
# ============ Path Utilities ============ #
from os.path import (
	join as path_join,
	split as path_split,
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



class LintingChecker:
	"""
		Rappresenta un oggetto in grado di effettuare la verifica di correttezza,
		a livello di linting, di test-suites parziali tramite un tool di verifica
		installato all' interno dell' ambiente focale.
		
		Attributi di Classe Pubblici:
			- `LINTING_TEMP_DIR` (str) : Rappresenta il nome, di default, della directory temporanea, nel container, in cui verranno memorizzati i files usati temporaneamente durante la verifica del codice
			- `LINTING_TOOLS_DIRNAME` (str) : Rappresenta il nome, di default, della directory in cui sono contenuti i tools necessari per la verifica, a livello di linting, che verrà effettuata all' interno dell' ambiente del progetto focale
			- `LINTING_SCRIPT` (str) : Rappresenta il nome, di default, dello script Python, contenuto nella directory dei tools per la verifica a livello di linting, che eseguirà la verifica nell' ambiente del progetto focale tramite gli strumenti scelti
	"""
	
	LINTING_TEMP_DIR: str = "gtsai__linting_temp"
	LINTING_TOOLS_DIR: str = "gtsai_linting_tools"
	LINTING_SCRIPT: str = "exec_linting_check.py"
	_RESULT_FNAME: str = "gtsai__linting_result.json"
	
	
	def __init__(
			self,
			chk_tools_dirname: str = None,
			fenv_script_fname: str = None,
			temp_dir: str = None,
	        logger: ATemporalFormattLogger = None,
	):
		"""
			Costruisce un nuovo LintingChecker associandolo eventualmente al logger utilizzato per registrare
			gli steps di ogni verifica a livello di linting effettuata.
			
			Parameters
			----------
				chk_tools_dirname: str
					Opzionale. Default = `None`. Una stringa rappresentante il nome della directory contenente i tools da utilizzare per
					la verifica di linting all' interno dell' ambiente del progetto focale
					
				fenv_script_fname: str
					Opzionale. Default = `None`. Una stringa contenente il nome dello script Python che esegue la verifica di correttezza,
					a livello di linting, all' interno dell' ambiente per il progetto focale
			
				temp_dir: str
					Opzionale. Default = `None`. Una stringa contenente il nome della directory da utilizzare come luogo di memorizzazione
					dei files temporanei necessari alla verifica di correttezza, a livello di linting, delle test-suites parziali
			
				logger: ATemporalFormattLogger
					Opzionale. Default = `None`. Un oggetto `ATemporalFormattLogger` rappresentante l' eventuale logger
					da utilizzare per registrare le fasi di ogni tentativo di correzione (non per registrare le fasi
					della richiesta al LLM)
		"""
		self._focal_env: FocalContainer = None
		
		# Attributi relativi al progetto focale impostato
		self._proj_name: str = None
		self._full_root: str = None
		self._focal_env: FocalContainer = None
		
		# Nome della directory temporanea creata in ogni ambiente focale
		# per la memorizzazione di files legati alla verifica di linting
		self._TEMP_DIRNAME: str = self.LINTING_TEMP_DIR
		if temp_dir is not None:
			self._TEMP_DIRNAME = temp_dir
		
		# Nome della directory che contiene i tools per la verifica di linting
		self._LINTTOOLS_DIRNAME: str = self.LINTING_TOOLS_DIR
		if chk_tools_dirname is not None:
			self._LINTTOOLS_DIRNAME = chk_tools_dirname

		# Nome dello script Python che esegue il linter all' interno dell' ambiente focale
		self._fenv_script_fname: str = self.LINTING_SCRIPT
		if fenv_script_fname is not None:
			self._fenv_script_fname = fenv_script_fname
			
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
		
		self._proj_name = project_name
		self._full_root = full_root
		
		del self._focal_env
		self._focal_env = FocalContainer(
			env_image,
			self._full_root,
			path_prefix
		)
		
		# Impostazione del nome del file temporaneo che conterrà le test-suites parziali
		actual_time: DateTime = DateTime.now()
		self._ptsuite_path = path_join(
			self._full_root, self._TEMP_DIRNAME,
			f"temp_{str(actual_time.timestamp())}.py"
		)
		
		# Impostazione della path che conterrà il risultato delle verifiche di linting
		self._lint_result_path = f"{self._full_root}/{self._TEMP_DIRNAME}/{self._RESULT_FNAME}"
		
		# Calcolo delle paths relative (con cui si costruiranno quelle assolute dell' ambiente focale)
		self._ptsuite_relpath = path_relative(self._ptsuite_path, start=self._full_root)
		self._lint_result_relpath = path_relative(self._lint_result_path, start=self._full_root)
		
		# Creazione della directory temporanea
		self._inited: bool = False
		self._create_tempdir()


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
					Si verifica se:
					
						- Il parametro `ptsuite_code` ha valore `None` o è una stringa vuota
						- Il parametro `resp_timeout` ha valore minore di 1
						
				OSError
					Se si verificano problemi con l' apertura, o scrittura, nel file temporaneo utilizzato
					per la verifica
		"""
		if not self._inited:
			self._create_tempdir()
		
		with open(self._ptsuite_path, "w") as fptsuite:
			fptsuite.write(ptsuite_code)
			fptsuite.flush()
		
		self._logger.log(
			f"Inizio della verifica di linting ..."
		) if self._logger is not None else None
		
		# Avvio dell' ambiente focale (container)
		self._logger.log("Avvio dell' ambiente focale ...") if self._logger is not None else None
		self._focal_env.start_container()
		self._logger.log(f"Ambiente focale del progetto {self._proj_name} avviato") if self._logger is not None else None
		
		# Richiesta della verifica della correttezza (a livello di linting)
		self._logger.log("Esecuzione della verifica di linting ...") if self._logger is not None else None
		self._focal_env.execute(
			f"python ./{self._LINTTOOLS_DIRNAME}/{self._fenv_script_fname} {self._ptsuite_relpath} {self._lint_result_relpath}"
		)
		self._logger.log("Verifica di linting eseguita") if self._logger is not None else None
		
		# Stop dell' ambiente focale (container)
		self._logger.log("Stop dell' ambiente focale ...") if self._logger is not None else None
		self._focal_env.stop_container()
		self._logger.log(f"Ambiente focale del progetto {self._proj_name} fermato") if self._logger is not None else None
		
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
		os_dremove(
			path_split(self._ptsuite_path)[0], ignore_errors=False
		)
		self._inited = False
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _create_tempdir(self):
		"""
			Crea la directory temporanea per i files necessari all' esecuzione
			della verifica a livello di linting
		"""
		tempfile_basepath: str = path_split(self._ptsuite_path)[0]
		os_dremove(tempfile_basepath, ignore_errors=False)
		os_mkdirs(tempfile_basepath)
		
		self._inited: bool = True