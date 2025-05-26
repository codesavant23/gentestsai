"""
    Componente che fornisce strutture di codice/strumenti che permettono una progettazione OO pulita
    (che si avvicina a una SOLID) anche in Python.

    Si fornisce in particolare:
        - Una "classe" base rappresentante il concetto di una dichiarazione di interfaccia.
        - Un decoratore di classe (@abstract_class) come meccanismo di dichiarazione di una classe come astratta.
        - Un decoratore di metodo (@abstract) come meccanismo per assicurarsi che la dichiarazione di metodi
          astratti rispecchi quella di altri linguaggi a oggetti (es. Java) mantenendone intatti i relativi
          contratti e forzandone l' implementazione da parte dei discendenti (controllo a run-time).
"""

# Interface/Class/Method Exports
from clean_oodabs._private.abstract_class import abstract_class
from clean_oodabs._private.abstract_method import abstract
from clean_oodabs._private.interface import Interface

__all__ = [
    "abstract_class",
    "abstract",
    "Interface"
]