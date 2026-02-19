from main_execs.pdirs_hasher import hash_modelname



if __name__ == '__main__':
	digest: str = hash_modelname()
	print(digest)