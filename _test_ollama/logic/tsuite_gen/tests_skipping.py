from json import (
	loads as json_loads,
	dump as json_dump
)


def skipped_testsfile_init(
		skipped_tests_path: str
):
	with open(skipped_tests_path, "w") as fjson:
		fjson.write("{}")
		fjson.flush()


def skip_function_tests(
		skipped_tests_path: str,
		func_name: str
):
	with open(skipped_tests_path, "r+") as fskipd:
		skipd_tests = json_loads(fskipd.read())
		if not skipd_tests.get("functions", None):
			skipd_tests["functions"] = [func_name]
		else:
			skipd_tests["functions"].append(func_name)
		fskipd.seek(0)
		json_dump(skipd_tests, fskipd, indent="\t")
		fskipd.flush()


def skip_method_tests(
		skipped_tests_path: str,
		cls_name: str,
		meth_name: str
):
	with open(skipped_tests_path, "r+") as fskipd:
		skipd_tests = json_loads(fskipd.read())
		if not skipd_tests.get("classes", None):
			skipd_tests["classes"] = dict()
		else:
			if not skipd_tests["classes"].get(cls_name, None):
				skipd_tests["classes"][cls_name] = [meth_name]
			else:
				skipd_tests["classes"][cls_name].append(meth_name)
		fskipd.seek(0)
		json_dump(skipd_tests, fskipd, indent="\t")
		fskipd.flush()