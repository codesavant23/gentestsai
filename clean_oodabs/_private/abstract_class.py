from typing import FrozenSet
from abc import ABC
from inspect import signature as getsignature, Signature


def abstract_class(cls):
    """
        Decoratore, sostituente la classe ABC del modulo 'abc' built-in di Python, che prende come argomento
        una classe, definita a livello semantico come astratta, e la rende astratta così da non essere
        istanziabile e che forza i discendenti a implementare i metodi definiti come astratti (tramite
        il decoratore @abstract, da utilizzarsi insieme a questo, fornito nel package 'clean_oodabs')

        A differenza del semplice utilizzo di ABC, del modulo 'abc' built-in di Python, oltre
        a GARANTIRE gli ultimi due comportamenti citati, questo decoratore GARANTISCE che
        sia il contratto della classe astratta, sia il contratto del costruttore astratto,
        siano visibili a utilizzatori e/o discendenti.
        Se la classe, o il costruttore, non ha un contratto esplicitato viene GARANTITO avere quello della
        sua superclasse, o del costruttore della sua superclasse, se esiste.

        Si ASSUME che la classe data, dichiarata astratta tramite questo decoratore, sia semanticamente astratta
        e quindi si ASSUME che abbia anche un metodo decorato con il decoratore @abstract.

        NOTA DI FONDAMENTALE IMPORTANZA: L' utilizzo di questo decoratore è da applicare insieme
        ad un approccio con Paradigma SOLID per ottenere disaccoppiamento e astrazione con dipendenze
        minime e NON COME UN MODIFICATORE SEMANTICO DI COMPORTAMENTO.
    """
    cls_contract: str = """"""
    if hasattr(cls, "__doc__"):
        cls_contract = cls.__doc__
    absconstr_contract: str = """"""
    if hasattr(cls.__init__, "__doc__"):
        absconstr_contract = cls.__init__.__doc__
    absconstr_sig: Signature = getsignature(cls.__init__)

    # Viene utilizzata una "Classe" Wrapper per fornire sia un "meccanismo base di astrazione"
    # sia per permettere il funzionamento con l' ecosistema built-in di Python (modulo 'abc')
    # che si basa più sui dunder attributes.

    class SingleInheritanceAbstractClass(cls, ABC):
        # Copia dei Nomi dei Metodi Astratti
        __abstractmethods__: FrozenSet[str] = getattr(cls, '__abstractmethods__', set())

    SingleInheritanceAbstractClass.__name__ = cls.__name__
    SingleInheritanceAbstractClass.__doc__ = cls_contract
    SingleInheritanceAbstractClass.__module__ = cls.__module__

    SingleInheritanceAbstractClass.__init__.__signature__ = absconstr_sig
    SingleInheritanceAbstractClass.__init__.__doc__ = absconstr_contract

    return SingleInheritanceAbstractClass
