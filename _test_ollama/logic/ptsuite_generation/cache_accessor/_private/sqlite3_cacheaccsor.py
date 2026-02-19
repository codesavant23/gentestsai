from typing import Tuple
from ._a_base_cacheaccsor import _ABaseCacheAccessor

# =========== SQLite3 Utilities ============ #
from sqlite3 import (
	connect as sql_connect,
	Connection as SqlConnection,
	Cursor as SqlConnectionCursor,
)
# ========================================== #

from ..exceptions import CacheFileTypeError



class Sqlite3CacheAccessor(_ABaseCacheAccessor):
	"""
		Rappresenta un `IPtsuiteCacheAccessor` che utilizza come cache
		un database locale SQLite3
	"""
	
	def __init__(
			self,
			cache_path: str
	):
		"""
			Costruisce un nuovo Sqlite3CacheAccessor associandolo alla path
			del database SQLite3 di caching da utilizzare
			
			Parameters
			----------
				cache_path: str
					Una stringa rappresentante la path che contiene il database di caching
					SQLite3 da utilizzare
		"""
		super().__init__(cache_path)
		
		self._conn: SqlConnection = sql_connect(cache_path)
		self._cursor: SqlConnectionCursor = self._conn.cursor()
	
	
	def close(self):
		self._cursor.close()
		self._conn.close()
	
	
	def does_ptsuite_exists(self, proj_name: str, prompt: str, model: str, try_num: int) -> bool:
		row: Tuple[str, str, str, str]= self._query_db(
			proj_name, prompt, model, try_num
		)

		return (row is not None)
	
	
	def _ap__create_projspace_spec(self, proj_name: str):
		self._cursor.execute(f"""
			CREATE TABLE IF NOT EXISTS "{proj_name}" (
				`prompt` TEXT NOT NULL,
				`model` TEXT NOT NULL,
				`try_num` INTEGER NOT NULL,
				`ptsuite` TEXT NOT NULL,
				PRIMARY KEY (`prompt`, `model`, `try_num`)
			)
		""")
		self._conn.commit()
	
	
	def _ap__register_ptsuite_spec(
			self,
			proj_name: str,
			prompt: str, model: str, try_num: int,
			ptsuite_code: str
	):
		self._cursor.execute(f"""
			INSERT INTO {proj_name} (prompt, model, try_num, ptsuite)
			VALUES (?, ?, ?, ?);
		""",
		[prompt, model, try_num, ptsuite_code])
		self._conn.commit()
	
	
	def _ap__get_ptsuite_spec(self, proj_name: str, prompt: str, model: str, try_num: int) -> str:
		partial_tsuite: str = self._query_db(
			proj_name,
			prompt, model, try_num
		)[3]
		return partial_tsuite
	
	
	def _ap__assert_cache_type(self, cache_path: str):
		header: bytes
		with open(cache_path, "rb") as fp:
			header = fp.read(16)
			
		if header != b"SQLite format 3\x00":
			raise CacheFileTypeError()


	##	============================================================
	##						PRIVATE METHODS
	##	============================================================


	def _query_db(
			self,
			project_name: str,
			prompt: str,
			model: str,
			try_num: int
	) -> Tuple[str, str, str, str]:
		self._cursor.execute(f"""
			SELECT * FROM `{project_name}`
			WHERE `prompt` = ?
			AND `model` = ?
			AND `try_num` = ?
		""", [prompt, model, try_num])

		return self._cursor.fetchone()