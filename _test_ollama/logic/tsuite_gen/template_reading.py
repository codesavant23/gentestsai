def read_templ_frompath(templ_path: str) -> str:
    """
        Legge un template per prompt da un file a caratteri

        Returns
        -------
        str
            Una stringa contenente il template del prompt da parsare
            per essere arricchito e creare quindi un prompt completo.
    """
    templ: str
    with open(templ_path, "r") as ftempl:
        templ = ftempl.read()
    return templ