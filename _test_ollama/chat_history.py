from typing import Dict, List, Literal


class ChatHistory:
    def __init__(self):
        self._history: List[Dict[str, str]] = []


    def clear(self):
        self._history.clear()


    def add_message(self,
            wrote_by: Literal["user", "llm"],
            message: str
    ):
        role: str
        if wrote_by == "user":
            role = "user"
        else:
            role = "assistant"

        self._history.append(
            ChatHistory._new_history_message(role, message)
        )


    @classmethod
    def _new_history_message(cls, role: str, message: str):
        """
            TODO: Finish description

            Parameters
            ----------
            role
            message

            Returns
            -------

        """
        history_message: Dict[str, str] = dict()

        history_message["role"] = role
        history_message["content"] = message

        return history_message