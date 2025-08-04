from typing import Tuple

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
    full_prompt: str = build_full_singleprompt(templ, focal_code, paths, context_names)

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
    full_prompt: str = build_full_singleprompt(templ, focal_code, paths, context_names)

    methname_patt = r"{@Method_Name@}"
    full_prompt = full_prompt.replace(methname_patt, meth_name)

    clsname_patt = r"{@Class_Name@}"
    full_prompt = full_prompt.replace(clsname_patt, cls_name)

    return full_prompt


def build_full_corrprompt(
        templ: str,
        wrong_tsuite: str,
        error: Tuple[str, str],
        paths: Tuple[str, str],
        context_names: Tuple[str, str]
) -> str:
    """

        Parameters
        ----------
            templ: str
                Una stringa contenente il template da utilizzare per costruire il prompt

            wrong_tsuite: str
                Una stringa contenente il codice della test suite da correggere

            error: str
                Una tupla di stringhe, contenente:

                    - [0]: Il nome dell' eccezione che si è verificata
                    - [1]: Il messaggio associato all' eccezione verificatasi

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
    full_prompt: str = build_full_singleprompt(templ, "", paths, context_names)

    suitecode_patt: str = r"{@Suite_Code@}"
    full_prompt = full_prompt.replace(suitecode_patt, wrong_tsuite)

    exceptname_patt: str = r"{@Exception_Name@}"
    full_prompt = full_prompt.replace(exceptname_patt, error[0])

    exceptmess_patt: str = r"{@Exception_Message@}"
    full_prompt = full_prompt.replace(exceptmess_patt, error[1])

    return full_prompt