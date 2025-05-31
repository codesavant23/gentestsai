from re import sub as reg_replace


def build_full_infoprompt(templ: str, focal_info: str, opt_persona: str = None) -> str:
    """
        Costruisce un Informational Prompt parsando il template
        e arrichendolo con il codice focale in esame.

        Returns
        -------
        str
            Una stringa contenente l' Informational Prompt Completo da fornire
            alla prima chat-like interaction con l' LLM
    """
    focalcode_patt: str = r"{@Focal_Code@}"
    info_prompt: str = reg_replace(focalcode_patt, focal_info, templ)

    if opt_persona is not None:
        persona_patt: str = r"{@Opt_Persona@}"
        info_prompt = reg_replace(persona_patt, opt_persona, info_prompt)

    return info_prompt


def build_full_taskprompt(templ: str, task_info: str) -> str:
    """
        Costruisce un Task Prompt parsando il template e arrichendolo
        con il codice di cui generare il test in esame.

        Returns
        -------
        str
            Una stringa contenente il Task Prompt Completo da fornire
            alla chat-like interaction con l' LLM per richiedere la
            generazione di uno specifico test.
    """
    focalcode_patt: str = r"{@Subtask_Code@}"
    task_prompt: str = reg_replace(focalcode_patt, task_info, templ)

    return task_prompt