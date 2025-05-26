from typing import Callable, Tuple
from inspect import Signature, signature as getsignature, getmro
from abc import abstractmethod


def abstract(method: Callable):
    """
        Decoratore, sostituente @abstractmethod del modulo 'abc', che prende come argomento un metodo, definito a livello semantico
        come astratto in un determinato contesto (es. Classe Astratta), e ne forza la sua implementazione ai discendenti
        della classe in cui è definito, bloccando anche una eventuale non-sensata implementazione nella classe astratta
        (possibilità di base permessa in Python).

        Il contratto (testuale) del metodo viene, ovviamente, lasciato intatto come dunque la sua firma.
        A differenza del semplice utilizzo di @abstractmethod questo decoratore GARANTISCE che
        il contratto del metodo astratto sia visibile agli utilizzatori/implementatori.
        Se il metodo non ha un contratto esplicitato viene GARANTITO avere quello del metodo
        di cui sta facendo l' override se esiste.

        Si ASSUME che il parametro `method` rappresenti effettivamente un metodo d' istanza, semanticamente
        astratto, di una classe o interfaccia.
        Si ASSUME anche che o la classe del metodo dato è dichiarata essere astratta, tramite il decoratore
        @abstract_class fornito dal package 'clean_oodabs', oppure il metodo è in realtà definito
        in un' "interfaccia" definita come discendente di `Interface` (fornita dal package 'clean_oodabs').

        NOTA DI FONDAMENTALE IMPORTANZA: L' utilizzo di questo decoratore è da applicare insieme
        ad un approccio con Paradigma SOLID e NON COME UN MODIFICATORE SEMANTICO DI COMPORTAMENTO
        dei metodi ereditati dalle interfacce/classi padre.
    """

    meth_name: str = method.__name__
    meth_sig: Signature = getsignature(method)
    meth_classname: str = method.__qualname__.split(".")[0]

    meth_cls: type = type(meth_classname)
    methcls_bases: Tuple[type, ...] = getmro(meth_cls)

    meth_contract: str = """"""
    contr_notfound: bool = True
    methcls_base: type
    i: int = 0
    while contr_notfound and (i < len(methcls_bases)):
        methcls_base = methcls_bases[i]
        try:
            poss_parmeth: Callable = getattr(methcls_base, meth_name)
            if hasattr(poss_parmeth, '__doc__') and poss_parmeth.__doc__:
                contr_notfound = False
                meth_contract = poss_parmeth.__doc__
        except AttributeError:
            pass  # Il metodo non è presente nella classe base
        i += 1

    abs_method: Callable = abstractmethod(method)

    abs_method.__signature__ = meth_sig
    abs_method.__doc__ = meth_contract
    return abs_method