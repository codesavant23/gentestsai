# Class `FocalContainer`
Represents an object capable of managing a Docker-compatible container associated
with a specific focal project.
Each Docker-compatible container is built based on a pre-configured image
designed to host the focal project to which it is linked.

Specifically, the container is used for the following purposes:

	- Verifying the correctness, at the linting level, of the generated partial test suites
	- Calculating the coverage of both sets of test suites (human and LLM)


!!! abstract "Details"
	- **Fully-qualified Name**: `focalproj_configuration.focal_container.FocalContainer`
	
	


## Public methods

- [**start_container**](../methods/FocalContainer/start_container.md) `(self)`

- [**put_tararchive**](../methods/FocalContainer/put_tararchive.md) `(self, dest_path: str, tar_stream: BytesIO)`

- [**execute**](../methods/FocalContainer/execute.md) `( self, command: str, privileged: bool = False )`

- [**stop_container**](../methods/FocalContainer/stop_container.md) `(self)`

- [**get_last_stdout**](../methods/FocalContainer/get_last_stdout.md) `(self) -> str`

- [**get_last_stderr**](../methods/FocalContainer/get_last_stderr.md) `(self) -> str`

- [**get_last_exitcode**](../methods/FocalContainer/get_last_exitcode.md) `(self) -> int`


