# ============== OS Utilities ============== #
from os import (
	walk as os_walk,
	replace as os_rename,
	makedirs as os_mkdirs,
	remove as os_remove,
	environ as os_getenv
)
from os.path import (
	exists as os_fdexists,
	isfile as os_isfile,
	isdir as os_isdir
)
from shutil import rmtree as os_dremove
from tempfile import gettempdir as os_tempdir
# ========================================== #
# ============ Path Utilities ============ #
from os.path import (
	sep as path_sep,
	altsep as path_altsep,
	join as path_join,
	split as path_split,
	splitext as path_split_ext,
	dirname as path_getdir,
	commonpath as path_intersect,
	normpath as path_normalize,
	abspath as path_absolute,
	relpath as path_relative
)
_PATH_SEPS: str = f"{path_sep}{path_altsep if path_altsep is not None else ''}"
# ======================================== #

from jinja2 import (
	Environment as JinjaEnvironment,
	Template as JinjaTemplate,
	FileSystemLoader
)
from yaml import safe_load as yaml_load



def create_docs(
		template: JinjaTemplate,
		data_root: str,
		output_root: str,
):
	datafile_path: str
	mdfile_path: str
	fname_pure: str
	output_currpath: str
	
	yaml_data: Any
	md_content: str
	for curr_path, dirs, file_names in os_walk(data_root):
		curr_path = path_normalize(curr_path)
		
		output_currpath = path_join(
			output_root,
			path_relative(curr_path, start=data_root)
		)
		if not os_fdexists(output_currpath):
			os_mkdirs(output_currpath)
		
		for file_name in file_names:
			datafile_path = path_normalize(path_join(curr_path, file_name))
			fname_pure = path_split_ext(file_name)[0]
			
			with open(datafile_path, "r") as fp:
				yaml_data = yaml_load(fp)
				
		
			md_content = template.render(**yaml_data)
		
			mdfile_path = path_join(
				output_currpath,
				f"{fname_pure}.md"
			)
			with open(mdfile_path, "w") as fp:
				fp.write(md_content)
				fp.flush()



if __name__ == "__main__":
	env: JinjaEnvironment = JinjaEnvironment(loader=FileSystemLoader("./templates"))
	element_templ: JinjaTemplate = env.get_template("element_template.md.j2")
	entity_templ: JinjaTemplate = env.get_template("entity_template.md.j2")

	intf_dirname: str = "interfaces"
	absclss_dirname: str = "absclasses"
	clss_dirname: str = "classes"
	funcs_dirname: str = "functions"
	meths_dirname: str = "methods"
	
	output_root: str = "./docs/out"
	data_root: str = "./docs/docs_data"
	data_intf_root: str = path_join(data_root, intf_dirname)
	data_abs_root: str = path_join(data_root, absclss_dirname)
	data_clss_root: str = path_join(data_root, clss_dirname)
	data_meths_root: str = path_join(data_root, meths_dirname)
	data_funcs_root: str = path_join(data_root, funcs_dirname)
	
	if os_fdexists(data_intf_root):
		create_docs(
			element_templ,
			data_intf_root,
			path_join(output_root, intf_dirname)
		)
	
	if os_fdexists(data_abs_root):
		create_docs(
			element_templ,
			data_abs_root,
			path_join(output_root, absclss_dirname)
		)
		
	if os_fdexists(data_clss_root):
		create_docs(
			element_templ,
			data_clss_root,
			path_join(output_root, clss_dirname)
		)
		
	if os_fdexists(data_meths_root):
		create_docs(
			entity_templ,
			data_meths_root,
			path_join(output_root, meths_dirname)
		)
	
	if os_fdexists(data_funcs_root):
		create_docs(
			entity_templ,
			data_funcs_root,
			path_join(output_root, funcs_dirname)
		)