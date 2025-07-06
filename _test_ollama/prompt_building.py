from typing import Tuple
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

    persona_patt: str = r"{@Opt_Persona@}"
    if opt_persona is not None:
        info_prompt = reg_replace(persona_patt, opt_persona, info_prompt)
    else:
        info_prompt = reg_replace(persona_patt, "", info_prompt)

    return info_prompt.strip(" \n\t")


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


def build_full_singleprompt(templ: str, focal_code: str, context_names: Tuple[str, str]) -> str:
    """

        Parameters
        ----------
        templ: str
            Una stringa contenente il template da utilizzare per costruire il prompt
        focal_code: str
            Una stringa contenente il codice focale da aggiungere al full prompt risultante
        context_names
            Una tupla di stringhe, contenente:

                - [0]: Il nome del progetto a cui appartiene il codice del modulo focale
                - [1]: Il nome del modulo focale

        Returns
        -------

    """
    proj_name: str = context_names[0]
    mod_name: str = context_names[1]

    projname_patt: str = r"{@Project_Name@}"
    modname_patt: str = r"{@Module_Name@}"
    focalcode_patt: str = r"{@Focal_Code@}"

    full_prompt: str = reg_replace(projname_patt, proj_name, templ)
    full_prompt = reg_replace(modname_patt, mod_name, full_prompt)
    full_prompt = reg_replace(focalcode_patt, focal_code, full_prompt)

    return full_prompt


def build_full_fbyf_funcprompt(
    templ: str,
    focal_code: str,
    func_name: str,
    context_names: Tuple[str, str]
) -> str:
    """
        Iiii

        Parameters
        ----------
            templ: str
                Una stringa contenente il template da utilizzare per costruire il prompt
            focal_code: str
                Una stringa contenente il codice focale da aggiungere al full prompt risultante
            func_name: str
                Una stringa contenente il nome della funzione di cui generare il test
            context_names: Tuple[str, str]
                Una tupla di stringhe, contenente:

                    - [0]: Il nome del progetto a cui appartiene il codice del modulo focale
                    - [1]: Il nome del modulo focale

        Returns
        -------

    """
    full_singleprompt: str = build_full_singleprompt(templ, focal_code, context_names)

    funcname_patt: str = r"{@Function_Name@}"
    full_prompt: str = reg_replace(funcname_patt, func_name, full_singleprompt)

    return full_prompt


def build_full_fbyf_methprompt(
    templ: str,
    focal_code: str,
    cls_name: str,
    meth_name: str,
    context_names: Tuple[str, str]
) -> str:
    """

        Parameters
        ----------
        templ
        focal_code
        cls_name
        meth_name
        context_names

        Returns
        -------

    """
    full_prompt: str = build_full_singleprompt(templ, focal_code, context_names)

    methname_patt = r"{@Method_Name@}"
    full_prompt = reg_replace(methname_patt, meth_name, full_prompt)

    clsname_patt = r"{@Class_Name@}"
    full_prompt = reg_replace(clsname_patt, cls_name, full_prompt)

    return full_prompt


def build_corrimps_prompt(templ: str, focal_code: str, wrong_tsuite: str) -> str:
    focalcode_patt: str = r"{@Focal_Code@}"
    suitecode_patt: str = r"{@Suite_Code@}"

    full_prompt: str = reg_replace(focalcode_patt, focal_code, templ)
    full_prompt = reg_replace(suitecode_patt, wrong_tsuite, full_prompt)

    return full_prompt