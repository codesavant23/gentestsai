from .i_moddecls_extr_f import IModuleDeclsExtractorFactory

from ..._private.e_parser_tool import ECodeParserTool
from .._private.a_mutable_moddeclsextr import AMutableModuleDeclsExtractor
from .._private.treesitter_moddeclsextr import TreeSitterModuleDeclsExtractor


class MutableModuleDeclsExtractorFactory(IModuleDeclsExtractorFactory):
	"""
		Rappresenta una factory per ogni `IModuleDeclsExtractor` mutabile
	"""
	
	
	def create(
			self,
			tool: ECodeParserTool,
			module_code: str
	) -> AMutableModuleDeclsExtractor:
		match tool:
			case ECodeParserTool.TREE_SITTER:
				return TreeSitterModuleDeclsExtractor(module_code)
			case _:
				raise NotImplementedError()


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================