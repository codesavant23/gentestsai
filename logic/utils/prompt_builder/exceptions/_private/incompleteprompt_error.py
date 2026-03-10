class IncompletePromptError(Exception):
    """
        Rappresenta un' eccezione (non-exiting) che si verifica se si richiede di eseguire
        un' operazione che necessita di un full prompt ma il prompt utilizzato contiene
        ancora dei placeholders
    """
    pass