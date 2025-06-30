import ollama
import base64

OLLAMA_BASE = "http://158.110.146.224:1337/"
URL = "http://158.110.146.224:1337/api/chat"
AUTH = "ollama:3UHn2uyu1sxgAy15"
MODEL = "qwen3:32b"

PROMPT = "Generate a test for this Python code."

with open("test.txt", "r") as f:
    code = f.read().strip()

auth_token = base64.b64encode(AUTH.encode()).decode()
c = ollama.Client(host=OLLAMA_BASE, headers={'Authorization': f'Basic {auth_token}'})
OPT = {
		"num_ctx": 88192,
		"temperature": 0,
		"seed": 42,
		"stream": True
}

msg = PROMPT + "\n\n" + code
r = c.chat(model=MODEL, messages=[{'role': "user", 'content': msg}], options=OPT, stream=True, think=True)
for part in r:
	print(part['message']['content'], end='', flush=True)