from typing import Any, List, Dict, Tuple
from functools import reduce
from requests import Response, Session as RequestSession
from chat_history import ChatHistory


def ollama_interact(
        ollama_apiurl: str,
        model: str,
        sesh: RequestSession,
        chat_history: ChatHistory,
        keep_alive: str="30m",
        model_spec: Dict[str, Any]=None,
        think: bool=True,
        stream: bool=False,
        debug_msgs: Tuple[str, str]=None
) -> str:
    noopts_call: bool = True
    if model_spec is not None:
        noopts_call = False

    wants_debug: bool = False
    if debug_msgs is not None:
        wants_debug = True

    post_body: Dict[str, Any] = {
        "model": model,
        "messages": chat_history.history(),
        "stream": stream,
        "think": think,
        "keep-alive": keep_alive
    }
    if noopts_call:
        post_body["options"] = model_spec

    if wants_debug:
        print(debug_msgs[0], end="")
    response: Response = sesh.post(
        url=ollama_apiurl,
        json=post_body
    )
    if wants_debug:
        print(debug_msgs[1])

    resp_str: str = str(response.json()["message"]["content"])
    return resp_str