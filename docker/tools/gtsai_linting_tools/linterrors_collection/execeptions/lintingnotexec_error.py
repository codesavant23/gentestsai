class LintingNotExecutedError(Exception):
    """
        Rappresenta un' eccezione (non-exiting) che si manifesta se la verifica
        di linting non è stata eseguita ma viene richiesto qualcosa correlato
        al suo risultato
    """
    pass