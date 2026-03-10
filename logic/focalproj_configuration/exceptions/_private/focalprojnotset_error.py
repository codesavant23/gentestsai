class FocalProjectNotSetError(Exception):
    """
        Rappresenta un' eccezione (non-exiting) che si verifica se si richiede di eseguire
        un' operazione, in un configuratore di ambienti per progetti focali, senza aver impostato
        precedentemente i dati relativi ad un progetto focale
    """
    pass

