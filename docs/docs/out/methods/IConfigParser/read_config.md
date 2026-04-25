# Method `read_config`

<div class="acc-specs">
	
	<span class="acc-badge acc-abstract">abstract</span>
	
	<span class="acc-badge acc-public">public</span>
	
</div>

Parses the configuration file at the specified path, checking:

- If the extension is the one required by the type, if applicable
- If the contents are valid for the type specified by the descendants its interface
- If the configuration file can be represented as a Python dictionary

It then reads the configuration file, returning it as a Python dictionary of any-type values.


!!! abstract "Details"
    - **Defined into:** [IConfigParser](../../interfaces/IConfigParser.md)
	
	
	
	
## Signature
```python
	def read_config(self, cfgfile_path: str) -> Dict[str, Any]
```





---
## Parameters

- `cfgfile_path` (`str`):
	<div class="tabbed-text">
	
	A string containing the path to the configuration file to be parsed.

	</div>





## Return Type

_`Dict[str, Any]`_
<div class="tabbed-text">
	An any-type string-indexed dictionary, representing the read configuration file.

</div>

---


## Exceptions
!!! warning "Raised Exceptions"
		
	- **ValueError**, happens if:
		
		- The provided configuration file path is set to `None`
		
		- The provided configuration file path is an empty string
		
		
	- **InvalidConfigFilepathError**, happens if:
		
		- The provided configuration file path is syntactically invalid.
		
		- There is no file at the provided path.
		
		- The configuration file cannot be opened.
		
		
	- **WrongConfigFileTypeError**, happens if:
		
		- The associated configuration file is not a file of the type specified by the descendants of this interface (extension).
		
		- The contents of the file are invalid for the type specified by the descendants of this interface.
		
		
	- **WrongConfigFileFormatError**, happens if:
		
		- The configuration file is not representable as a Python dictionary
		
	
