from typing import Tuple


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
    info_prompt: str = templ.replace(focalcode_patt, focal_info)

    persona_patt: str = r"{@Opt_Persona@}"
    if opt_persona is not None:
        info_prompt = info_prompt.replace(persona_patt, opt_persona)
    else:
        info_prompt = info_prompt.replace(persona_patt, "")

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
    task_prompt: str = templ.replace(focalcode_patt, task_info)

    return task_prompt


def build_full_singleprompt(
        templ: str,
        focal_code: str,
        paths: Tuple[str, str],
        context_names: Tuple[str, str],
) -> str:
    """

        Parameters
        ----------
        templ: str
            Una stringa contenente il template da utilizzare per costruire il prompt

        focal_code: str
            Una stringa contenente il codice focale da aggiungere al full prompt risultante

        paths: Tuple[str, str]
            Una tupla di stringhe, contenente:

                - [0]: La path (senza file) del modulo focale
                - [1]: La path (senza file) della test suite associata al modulo focale

        context_names
            Una tupla di stringhe, contenente:

                - [0]: Il nome del progetto a cui appartiene il codice del modulo focale
                - [1]: Il nome del modulo focale

        Returns
        -------

    """
    proj_name: str = context_names[0]
    mod_name: str = context_names[1]

    focal_path: str = paths[0]
    tsuite_path: str = paths[1]

    projname_patt: str = r"{@Project_Name@}"
    full_prompt: str = templ.replace(projname_patt, proj_name)

    modname_patt: str = r"{@Module_Name@}"
    full_prompt = full_prompt.replace(modname_patt, mod_name)

    focalcode_patt: str = r"{@Focal_Code@}"
    full_prompt = full_prompt.replace(focalcode_patt, focal_code)

    focalpath_patt: str = r"{@Focal_Path@}"
    full_prompt = full_prompt.replace(focalpath_patt, focal_path)
    tsuitepath_patt: str = r"{@Suite_Path@}"
    full_prompt = full_prompt.replace(tsuitepath_patt, tsuite_path)

    return full_prompt


def build_full_fbyf_funcprompt(
        templ: str,
        focal_code: str,
        func_name: str,
        paths: Tuple[str, str],
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
                Una stringa contenente il nome della funzione di cui generare i tests

            paths: Tuple[str, str]
                Una tupla di stringhe, contenente:

                    - [0]: La path (senza file) del modulo focale
                    - [1]: La path (senza file) della test suite associata al modulo focale

            context_names: Tuple[str, str]
                Una tupla di stringhe, contenente:

                    - [0]: Il nome del progetto a cui appartiene il codice del modulo focale
                    - [1]: Il nome del modulo focale

        Returns
        -------

    """
    full_prompt: str = build_full_singleprompt(templ, focal_code, context_names, paths)

    funcname_patt: str = r"{@Function_Name@}"
    full_prompt = full_prompt.replace(funcname_patt, func_name)

    return full_prompt


def build_full_fbyf_methprompt(
        templ: str,
        focal_code: str,
        cls_name: str,
        meth_name: str,
        paths: Tuple[str, str],
        context_names: Tuple[str, str]
) -> str:
    """

        Parameters
        ----------
            templ: str
                Una stringa contenente il template da utilizzare per costruire il prompt

            focal_code: str
                Una stringa contenente il codice focale da aggiungere al full prompt risultante

            cls_name: str
                Una stringa contenente il nome della classe focale

            meth_name: str
                Una stringa contenente il nome della funzione di cui generare i tests

            paths: Tuple[str, str]
                Una tupla di stringhe, contenente:

                    - [0]: La path (senza file) del modulo focale
                    - [1]: La path (senza file) della test suite associata al modulo focale

            context_names
                Una tupla di stringhe, contenente:

                    - [0]: Il nome del progetto a cui appartiene il codice del modulo focale
                    - [1]: Il nome del modulo focale

        Returns
        -------

    """
    full_prompt: str = build_full_singleprompt(templ, focal_code, context_names, paths)

    methname_patt = r"{@Method_Name@}"
    full_prompt = full_prompt.replace(methname_patt, meth_name)

    clsname_patt = r"{@Class_Name@}"
    full_prompt = full_prompt.replace(clsname_patt, cls_name)

    return full_prompt


def build_corr_prompt(
        templ: str,
        focal_code: str,
        wrong_tsuite: str,
        paths: Tuple[str, str],
        context_names: Tuple[str, str]
) -> str:
    """

        Parameters
        ----------
            templ: str
                Una stringa contenente il template da utilizzare per costruire il prompt

            focal_code: str
                Una stringa contenente il codice focale da aggiungere al full prompt risultante

            wrong_tsuite: str
                Una stringa contenente il codice della test suite da correggere

            paths: Tuple[str, str]
                Una tupla di stringhe, contenente:

                    - [0]: La path (senza file) del modulo focale
                    - [1]: La path (senza file) della test suite associata al modulo focale

            context_names: Tuple[str, str]
                Una tupla di stringhe, contenente:

                    - [0]: Il nome del progetto a cui appartiene il codice del modulo focale
                    - [1]: Il nome del modulo focale

        Returns
        -------

    """
    full_prompt: str = build_full_singleprompt(templ, focal_code, context_names, paths)

    suitecode_patt: str = r"{@Suite_Code@}"
    full_prompt = full_prompt.replace(suitecode_patt, wrong_tsuite)

    return full_prompt


def build_corrimps_prompt(
        templ: str,
        focal_code: str,
        wrong_tsuite: str,
        paths: Tuple[str, str],
        context_names: Tuple[str, str]
) -> str:
    """

        Parameters
        ----------
            templ: str
                Una stringa contenente il template da utilizzare per costruire il prompt

            focal_code: str
                Una stringa contenente il codice focale da aggiungere al full prompt risultante

            wrong_tsuite: str
                Una stringa contenente il codice della test suite da correggere

            paths: Tuple[str, str]
                Una tupla di stringhe, contenente:

                    - [0]: La path (senza file) del modulo focale
                    - [1]: La path (senza file) della test suite associata al modulo focale

            context_names: Tuple[str, str]
                Una tupla di stringhe, contenente:

                    - [0]: Il nome del progetto a cui appartiene il codice del modulo focale
                    - [1]: Il nome del modulo focale

        Returns
        -------

    """
    full_prompt: str = build_corr_prompt(templ, focal_code, wrong_tsuite, paths, context_names)

    return full_prompt