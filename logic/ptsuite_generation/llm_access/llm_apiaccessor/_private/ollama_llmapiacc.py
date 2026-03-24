from typing import List, Dict, Iterator, Any
from ._a_base_llmapiacc import _ABaseLlmApiAccessor

from base64 import b64encode as b64_encode
from ollama import (
	Client as OllamaClient,
	ChatResponse,
	ResponseError as OllamaApiResponseError
)
from time import monotonic as time_monotonic
from httpx import (
	Timeout as HttpxTimeout,
	TimeoutException as HttpxTimeoutError,
	ConnectTimeout as HttpxConnectTimeoutError
)

from ...llm_api import (
	ILlmApi,
	OllamaApi
)
from ...llm_chat import ILlmChat
from ...llm_hyperparam.id import (
	ILlmHyperParamId,
	LlmHyperParamIdFactoryResolver,
)
from ...llm_hyperparam import ILlmHyperParam
from ...llm_specimpl import ILlmSpecImpl


from .....utils.logger import ATemporalFormattLogger
from .....utils.logger.exceptions import FormatNotSetError

from ..exceptions import (
	ApiConnectionError,
	ApiResponseError,
	ResponseTimedOutError,
	SaturatedContextWindowError
)



class OllamaLlmApiAccessor(_ABaseLlmApiAccessor):
	"""
		Rappresenta un `ILlmApiAccessor` per la piattaforma di inferenza "Ollama".
		
		Vengono loggati i seguenti step dell' intera fase di richiesta al LLM:
			- Inizio del tentativo di connessione
			- Riuscita del tentativo di connessione
			- Inizio della sotto-fase di ricevimento della risposta
			- Ogni "chunk" della risposta ricevuta (a scelta indipendentemente dal logger)
			- Fine della sotto-fase di ricevimento della risposta
	"""
	
	def __init__(
			self,
			address: str,
			auth: str,
			conn_timeout: int,
			logger: ATemporalFormattLogger = None,
			log_resp: bool = False,
			logger_sep: str="\n",
	):
		"""
			Costruisce un nuovo OllamaLlmApiAccessor associandolo alla prima chat da utilizzare
			per effettuare le richieste
			
			Parameters
			----------
				address: str
					Una stringa contenente l' indirizzo (URL assoluto, IPv4 o IPv6) che identifica
					il server Ollama su cui è ospitata la piattaforma di inferenza
					
				auth: str
					Una stringa contenente le credenziali di accesso, come coppia `user:token`,
					da utilizzare per le interazioni
					
				conn_timeout: int
					Un intero rappresentante il timeout in millisecondi dopo il quale
					dichiarare un tentativo di connessione fallito
					
				logger: ATemporalFormattLogger
					Opzionale. Default = `None`. Un oggetto `ATemporalFormattableLogger` rappresentante
					il logger da utilizzare per registrare i passaggi effettuati da questo OllamaLlmApiAccessor
					durante ogni richiesta effettuata
					
				logger_sep: str
					Opzionale. Default = `\\n`. Una stringa contenente il separatore da utilizzare per i
					messaggi di logging che verranno registrati.
					
				log_resp: bool
					Opzionale. Default = `False`. Un booleano che indica se è necessario loggare anche
					i "chunks" della risposta che vengono ricevuti
					
			Raises
			------
				ValueError
					Si verifica se:
						
						- Almeno uno tra `address` e `auth` hanno valore `None`
						- Il parametro `log_resp` ha valore `True` ma non è stato fornito un logger
		"""
		super().__init__()
		
		self._logger: ATemporalFormattLogger = logger
		if logger is not None:
			self._logger_sep = logger_sep if logger_sep is not None else "\n"
		
		if log_resp and (logger is None):
			raise ValueError()
		if (address is None) or (auth is None):
			raise ValueError()
		
		self._log_resp: bool = log_resp
		self._o_addr: str = address
		self._o_auth: str = b64_encode(auth.encode()).decode()
		self._conn_tout: int = conn_timeout
		
		self._think_param: ILlmHyperParamId = LlmHyperParamIdFactoryResolver.resolve("ollama").create("think")
		self._numctx_param: ILlmHyperParamId = LlmHyperParamIdFactoryResolver.resolve("ollama").create("context_window")
	
	
	def _ap__prompt_spec(
			self,
			chat: ILlmChat,
			model: ILlmSpecImpl,
			hparams: List[ILlmHyperParam],
			timeout: int,
	) -> str:
		options_param: Dict[str, Any] = {
			hparam.param_id().id(): hparam.to_effvalue()
			for hparam in hparams
		}
		think_param: bool = options_param.pop(self._think_param.id())
		num_ctx_param: int = options_param[self._numctx_param.id()]
		
		conn_timeout: HttpxTimeout = HttpxTimeout(
			None, connect=int(self._conn_tout) / 1000.0
		)
		resp_timeout: float = timeout / 1000.0

		def_time_format: str = "( {day}-{month}-{year} | {hour}:{min}:{second} )"
		log_format: str = None
		if self._logger is not None:
			try:
				log_format = self._logger.unset_format()
				self._logger.set_format(log_format)
			except FormatNotSetError:
				self._logger.set_format("[LLM REQUEST (Ollama)] {message} " + def_time_format)
				
			self._logger.set_messages_sep(self._logger_sep)
			self._logger.log("Tentativo di connesione con Ollama ...")
			
		oll_client: OllamaClient
		try:
			oll_client = OllamaClient(
				host=self._o_addr,
				headers={ 'Authorization': f'Basic {self._o_auth}' },
				timeout=conn_timeout
			)
			if self._logger is not None:
				self._logger.log("Connessione con Ollama stabilita.")
		except HttpxConnectTimeoutError as httpx_tout_error:
			gensai_exc: ApiConnectionError = ApiConnectionError()
			gensai_exc.args = ("timeout",) + httpx_tout_error.args
			raise gensai_exc from httpx_tout_error
		except ConnectionError as ollama_err:
			gensai_exc: ApiConnectionError = ApiConnectionError()
			gensai_exc.args = ("other",) + ollama_err.args
			gensai_exc.errno = ollama_err.errno
			raise gensai_exc from ollama_err
		
		response_iter: Iterator[ChatResponse]
		try:
			response_iter = oll_client.chat(
				model.model_name(),
				chat.chat_messages(),
				options=options_param,
				stream=True,
				think=think_param,
			)
		except OllamaApiResponseError as ollama_err:
			gensai_exc: ApiResponseError = ApiResponseError()
			gensai_exc.args = ("known",) + ollama_err.args
			raise gensai_exc from ollama_err
		
		start_time: float
		timed_out: bool = False
		drifted: bool = False
		prompt_tokens: int = -1
		resp_tokens: int = -1
		full_response: str = ""
		try:
			self._logger.log("Inizio della risposta ...") if self._logger is not None else None
			if self._log_resp:
				log_format = self._logger.unset_format()
				self._logger.set_messages_sep("")
				
			start_time = time_monotonic()
			for chunk in response_iter:
				full_response += chunk['message']['content']
				if self._log_resp:
					self._logger.log(chunk['message']['content'])
				
				# Check del tempo complessivo occupato dalla risposta fino ad ora
				if ((time_monotonic() - start_time) > resp_timeout):
					timed_out = True
					break
				
				# Se è arrivato alla fine
				if "eval_count" in chunk:
					resp_tokens = chunk["eval_count"]
					prompt_tokens = chunk["prompt_eval_count"]
					if self._log_resp:
						self._logger.log(f'{self._logger_sep}')
							
			if timed_out or drifted:
				if self._log_resp:
					self._logger.set_format(log_format)
					self._logger.set_messages_sep(self._logger_sep)
				if timed_out:
					raise ResponseTimedOutError()
		except HttpxTimeoutError as httpx_tout_err:
			gensai_exc: ResponseTimedOutError = ResponseTimedOutError()
			gensai_exc.args = httpx_tout_err.args
			raise gensai_exc from httpx_tout_err
		except OllamaApiResponseError as ollama_err:
			gensai_exc: ApiResponseError = ApiResponseError()
			gensai_exc.args = ("known",) + ollama_err.args
			raise gensai_exc from ollama_err
		
		if self._log_resp:
			self._logger.set_format(log_format)
			self._logger.set_messages_sep(self._logger_sep)
		self._logger.log(f'Fine della risposta.') if self._logger is not None else None

		if ((prompt_tokens == -1) or (resp_tokens == -1) or
			(full_response == "")):
			gensai_exc: ApiResponseError = ApiResponseError()
			gensai_exc.args = ("unknown",) + (str(prompt_tokens), str(resp_tokens), full_response)
			raise gensai_exc

		if (prompt_tokens + resp_tokens) >= num_ctx_param:
			raise SaturatedContextWindowError()
		
		return full_response
	
	
	def _ap__accepted_api(self) -> ILlmApi:
		return OllamaApi()


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================