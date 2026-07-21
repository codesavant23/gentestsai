# Class `PromptBuilder`
Represents an object capable of constructing a full prompt given a template in which to replace the placeholders.

The placeholders accepted by this full prompt builder are identified by enclosing the placeholder name
between two delimiters: one at the beginning of the name and one at the end.

By default, this object uses the following delimiters:
	- Start: `{@`
	- End: `@}`

e.g.	Placeholder in the template with the default delimiters:
`Place_Holder1` is identified by `{@Place_Holder1@}`


!!! abstract "Details"
	- **Fully-qualified Name**: `prompt_builder.PromptBuilder`
	
	


## Public methods

- [**set_template_prompt**](../methods/PromptBuilder/set_template_prompt.md) `(self, template_prompt: str)`

- [**does_placeh_exists**](../methods/PromptBuilder/does_placeh_exists.md) `( self, placeh_name: str ) -> bool`

- [**unset_placeholders**](../methods/PromptBuilder/unset_placeholders.md) `(self)`

- [**set_placeholder**](../methods/PromptBuilder/set_placeholder.md) `( self, name: str, value: str )`

- [**build_prompt**](../methods/PromptBuilder/build_prompt.md) `(self) -> str`


