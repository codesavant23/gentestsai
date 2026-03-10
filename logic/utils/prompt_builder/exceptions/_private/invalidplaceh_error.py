class InvalidPlaceholderError(Exception):
    """
        Rappresenta un' eccezione (non-exiting) che si verifica se si tenta di utilizzare
        un placeholder che non è possibile utilizzare in un template prompt
    """
    pass