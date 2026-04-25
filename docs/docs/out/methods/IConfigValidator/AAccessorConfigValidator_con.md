# Method `__init__`

<div class="acc-specs">
	
	<span class="acc-badge acc-public">public</span>
	
</div>

Builds a new AAccessorConfigValidator by providing it with the Python configuration dictionary that will be associated with this validator.


!!! abstract "Details"
    - **Defined into:** [AAccessorConfigValidator](../../absclasses/AAccessorConfigValidator.md)
	
	
	
	
## Signature
```python
	def __init__None
```





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
		
		- The provided dictionary has the value `None`
		
		- The provided dictionary is empty
		
	
