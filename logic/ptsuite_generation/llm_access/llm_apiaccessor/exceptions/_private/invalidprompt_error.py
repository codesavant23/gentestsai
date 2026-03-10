class InvalidPromptError(Exception):
    """
        Rappresenta un' eccezione (non-exiting) che si verifica nel momento in cui
        una stringa rappresentante un prompt ha un valore invalido (es. stringa vuota).
    """
    pass