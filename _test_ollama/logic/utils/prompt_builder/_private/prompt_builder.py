from typing import Dict

from regex import (
	Pattern,
	compile as create_pattern,
	escape as reg_escape,
)

from ..exceptions import (
	TemplateNotSetError,
	InvalidPlaceholderError,
	IncompletePromptError
)



class PromptBuilder:
	"""
		Rappresenta un oggetto in grado di costruire un full prompt dato un template di cui
		sostituirne i placeholders.

		I placeholders accettati da questo costruttore di full prompts sono identificati con il wrapping
		del nome del placeholder da due delimitatori: uno iniziale al nome e uno finale.

		Per default quest' oggetto usa i seguenti delimitatori:
			- Iniziale: `{@`
			- Finale: `@}`

		es.	Placeholder nel template con i delimitatori di default:
		Place_Holder1	----identificato-con---->	{@Place_Holder1@}
	"""

	def __init__(
			self,
			template_prompt: str = None,
			init_del: str="{@",
			end_del: str="@}"
	):
		"""
			Costruisce un nuovo PromptBuilder legandolo ad un particolare template prompt

			Parameters
			----------
				template_prompt: str
					Opzionale. Default = `None`. Una stringa contenente il template prompt su cui basarsi.
					Se il template prompt non viene fornito ora è necessario fornirlo in seguito,
					tramite il metodo `.`

				init_del: str
					Opzionale. Default = `{@`. Una stringa contenente il delimitatore iniziale per riconoscere
					i placeholders nel template

				end_del: str
					Opzionale. Default = `{@`. Una stringa contenente il delimitatore finale per riconoscere
					i placeholders nel template
		"""
		self._idel: str = init_del
		self._edel: str = end_del
		self._templ: str = template_prompt

		self._placehs: Dict[str, str] = None
		if self._templ is not None:
			self._placehs = self._init_placehs_dict(template_prompt, init_del, end_del)


	def set_template_prompt(self, template_prompt: str):
		"""
			Imposta un nuovo template prompt di cui creare il full prompt,
			disassociando quello eventualmente impostato in precedenza
			
			Raises
			------
				ValueError
					Si verifica se:
					
						- Il parametro `template_prompt` ha valore `None`
						- Il parametro `template_prompt` è una stringa vuota
		"""
		if (template_prompt is None) or (template_prompt == ""):
			raise ValueError()
		
		self._templ = template_prompt
		
		if self._placehs is not None:
			del self._placehs
		self._placehs = self._init_placehs_dict(
			template_prompt, self._idel, self._edel
		)


	def does_placeh_exists(
			self,
			placeh_name: str
	) -> bool:
		"""
			Verifica se esiste il placeholder con nome fornito, nel template associato, e può essere utilizzato

			Parameters
			----------
				placeh_name: str
					Una stringa contenente il nome del placeholder di cui verificare l'esistenza

			Returns
			-------
				bool
					Un booleano che indica se il placeholder, con nome `placeh_name`, esiste
					
			Raises
			------
				TemplateNotSetError
					Si verifica se non è stato ancora impostato alcun template prompt
				
		"""
		if self._templ is None:
			raise TemplateNotSetError()
		
		if placeh_name in self._placehs:
			return True
		else:
			return False
	
	
	def unset_placeholders(self):
		"""
			Elimina il valore impostato per ogni placeholder
			
			Raises
			------
				TemplateNotSetError
					Si verifica se non è stato ancora impostato alcun template prompt
		"""
		if self._templ is None:
			raise TemplateNotSetError()
		
		for key in self._placehs.keys():
			self._placehs[key] = None
		

	def set_placeholder(
			self,
			name: str,
			value: str
	):
		"""
			Sostituisce il placeholder indicato, nel template prompt associato a questo PromptBuilder, con il valore scelto

			Parameters
			----------
				name: str
					Una stringa che identifica il nome del placeholder da sostituire

				value: str
					Una stringa che identifica il valore con cui sostituire il placeholder indicato

			Raises
			------
				TemplateNotSetError
					Si verifica se non è stato ancora impostato alcun template prompt
					
				InvalidPlaceholderError
					Se il placeholder con nome `name` non esiste nel template prompt a cui è associato questo prompt builder
		"""
		if self._templ is None:
			raise TemplateNotSetError()
		if not self.does_placeh_exists(name):
			raise InvalidPlaceholderError()

		self._placehs[name] = value


	def build_prompt(self) -> str:
		"""
			Costruisce il full prompt risultante dalle sostituzioni scelte nel template.
			E' richiesto che tutti i placeholders siano stati sostituiti prima di chiamare quest' operazione

			Returns
			-------
				str
					Una stringa contenente il full prompt derivante dalle sostituzioni del template prompt

			Raises
			------
				TemplateNotSetError
					Si verifica se non è stato ancora impostato alcun template prompt
			
				IncompletePrompt
					Se si esegue quest' operazione senza aver sostituito prima tutti i placeholders
					nel template prompt
		"""
		if self._templ is None:
			raise TemplateNotSetError()
		
		for placeh, value in self._placehs.items():
			if value is None:
				raise IncompletePromptError()

		full_prompt: str = self._templ
		for placeh, value in self._placehs.items():
			full_prompt = full_prompt.replace(
				reg_escape(
					f"{self._idel}{placeh}{self._edel}"
				),
				value
			)

		return full_prompt
	
	
	##	============================================================
	##						PRIVATE METHODS
	##	============================================================
	
	
	@classmethod
	def _init_placehs_dict(
			cls,
			template_prompt: str,
			init_del: str,
			end_del: str
	) -> Dict[str, str]:
		placehs_dict: Dict[str, str] = dict()
		
		plach_patt: Pattern = create_pattern(
			fr"{reg_escape(init_del)}(?P<placeh_name>[A-Za-z0-9_]+){reg_escape(end_del)}"
		)
		for placeh_match in plach_patt.finditer(template_prompt):
			placehs_dict[placeh_match.group("placeh_name")] = None
			
		return placehs_dict