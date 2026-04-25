# Method `_ap__assert_platspec`

<div class="acc-specs">
	
	<span class="acc-badge acc-abstract">abstract</span>
	
	<span class="acc-badge acc-protected">protected</span>
	
</div>

Checks the validity of the values ​​of the inference platform fields
specified by descendants of this abstract class.

If validation is successful, this operation should be equivalent to a no-op.


!!! abstract "Details"
    - **Defined into:** _APlatSpecConfigValidator
	
	- **Exposed by:** [AAccessorConfigValidator](../../absclasses/AAccessorConfigValidator.md)
	
	
	
	
## Signature
```python
	def _ap__assert_platspec(config_dict: Dict[str, Any]) -> Dict[str, Any]
```


## Guarantees

When this entity is called it is already guaranteed:

- That all mandatory fields, not specific to the inference platform, exist and are semantically correct.

- That optional fields, which do exist but are not specific to the inference platform, are semantically correct.





---
## Parameters

- `config_dict` (`Dict[str, Any]`):
	<div class="tabbed-text">
	
	An any-type, string-indexed dictionary representing the read configuration file

	</div>





## Return Type

This entity doesn't return any value

---


## Exceptions
!!! warning "Raised Exceptions"
		
	- **ValueError**, happens if:
		
		- The semantics of one or more fields are correct but a specific platform error exists, declared by the descendants of this its class.
		
	
