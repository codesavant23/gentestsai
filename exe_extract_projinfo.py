from typing import Tuple, Dict
from json import dumps as json_dump
from projinfo_extraction import extract_projsinfo


def projinfo_extractor_pgm():
    projs_path: str = input("Inserire la path della directory contenente una cartella per ogni progetto da cui estrarre le informazioni :>  ")
    infofile_path: str = input("Inserire la path del file JSON che conterrà le informazioni estratte :>  ")

    info: Dict[str, Tuple[int, int, float, float, float, float]] = extract_projsinfo(projs_path)

    with open(infofile_path, "w") as fjson:
        content: str = json_dump(info)
        fjson.write(content)

    print("Informazioni estratte e scritte in '"+infofile_path+"' !")


if __name__ == "__main__":
    projinfo_extractor_pgm()