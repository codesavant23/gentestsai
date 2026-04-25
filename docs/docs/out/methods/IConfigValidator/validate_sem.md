# Method `validate_sem`

<div class="acc-specs">
	
	<span class="acc-badge acc-public">public</span>
	
</div>

Perform semantic validation of the associated Python dictionary representing a configuration file


!!! abstract "Details"
    - **Defined into:** [IConfigValidator](../../interfaces/IConfigValidator.md)
	
	
	
	
## Signature
```python
	def validate_sem(self)
```








---


## Return Type

This entity doesn't return any value

---


## Exceptions
!!! warning "Raised Exceptions"
		
	- **FieldDoesntExistsError**, happens if:
		
		- The represented configuration file has one or more missing mandatory fields.
		
		
	- **ConfigExtraFieldsError**, happens if:
		
		- The configuration file contains fields not intended for the purpose specified by the descendant of IConfigValidator that implements this method.
		
		
	- **InvalidConfigValueError**, happens if:
		
		- The semantics of one or more required fields are incorrect
		
		- The semantics of one or more optional fields are incorrect
		
		- The semantics of one or more fields are correct, but a specific error exists declared by descendants of IConfigValidator that implements this method
		
	
