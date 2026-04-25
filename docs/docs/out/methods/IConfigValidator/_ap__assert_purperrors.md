# Method `_ap__assert_purperrors`

<div class="acc-specs">
	
	<span class="acc-badge acc-abstract">abstract</span>
	
	<span class="acc-badge acc-protected">protected</span>
	
</div>

Checks for errors related to the specified purpose from descendants of each IConfigValidator.

If validation is successful, this operation should be equivalent to a no-op.


!!! abstract "Details"
    - **Defined into:** _ABaseConfigValidator
	
	- **Exposed by:** [AAccessorConfigValidator](../../absclasses/AAccessorConfigValidator.md)
	
	
	
	
## Signature
```python
	def _ap__assert_purperrors(config_dict: Dict[str, Any]) -> Dict[str, Any]
```


## Guarantees

When this entity is called it is already guaranteed:

- That all required fields exist and are semantically correct.

- That optional fields, which do exist, are semantically correct.





---
## Parameters

- `config_read` (`Dict[str, Any]`):
	<div class="tabbed-text">
	
	An any-type, string-indexed dictionary representing the read configuration file

	</div>





## Return Type

This entity doesn't return any value

---


## Exceptions
!!! warning "Raised Exceptions"
		
	- **InvalidConfigValueError**, happens if:
		
		- The semantics of one or more fields are correct but a specific error exists, declared by the descendants of its abstract class.
		
	
