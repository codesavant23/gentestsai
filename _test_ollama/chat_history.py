from typing import Dict, List, Literal


class ChatHistory:
    def __init__(self):
        self._history: List[Dict[str, str]] = []

    def history(self) -> List[Dict[str, str]]:
        return self._history

    def clear(self):
        self._history.clear()


    def add_message(
        self,
        writer_role: Literal["user", "llm", "context", "tool"],
        message: str
    ):
        role: str
        if writer_role == "user":
            role = "user"
        elif writer_role == "llm":
            role = "assistant"
        elif writer_role == "context":
            role = "system"
        else:
            role = "tool"

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