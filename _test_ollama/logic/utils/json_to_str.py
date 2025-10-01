def read_json_tobuff(abs_path: str) -> str:
	buffer: str
	with open(abs_path, "r") as fp:
		buffer = fp.read()
	return buffer