from typing import Dict

from regex import (
	Pattern,
	compile as create_pattern,
	escape as reg_escape,
)

from ..exceptions import (
	InvalidPlaceholderError,
	IncompletePromptError
)



class PromptBuilder:
	"""
		Rappresenta un oggetto in grado di costruire un Full Prompt dato un template di cui
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
			template_prompt: str,
			init_del: str="{@",
			end_del: str="@}"
	):
		"""
			Costruisce un nuovo PromptBuilder legandolo ad un particolare template prompt

			Parameters
			----------
				template_prompt: str
					Una stringa contenente il template prompt su cui basarsi

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

		self._placehs: Dict[str, str] = dict()
		plach_patt: Pattern = create_pattern(
			fr"{reg_escape(init_del)}(?P<placeh_name>[A-Za-z0-9_]+){reg_escape(end_del)}"
		)
		for placeh_match in plach_patt.finditer(template_prompt):
			self._placehs[placeh_match.group("placeh_name")] = None


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
		"""
		if placeh_name in self._placehs:
			return True
		else:
			return False


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
				InvalidPlaceholderError
					Se il placeholder con nome `name` non esiste nel template prompt a cui è associato questo prompt builder
		"""
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
				IncompletePrompt
					Se si esegue quest' operazione senza aver sostituito prima tutti i placeholders
					nel template prompt
		"""
		for placeh, value in self._placehs:
			if value is None:
				raise IncompletePromptError()

		full_prompt: str = self._templ
		for placeh, value in self._placehs:
			full_prompt = full_prompt.replace(
				reg_escape(
					f"{self._idel}{placeh}{self._edel}"
				),
				value
			)

		return full_prompt