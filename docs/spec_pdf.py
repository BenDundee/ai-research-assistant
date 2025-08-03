import requests
import json
url = "https://openrouter.ai/api/v1/chat/completions"
API_KEY_REF = "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"
headers = {
    "Authorization": f"Bearer {API_KEY_REF}",
    "Content-Type": "application/json"
}
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "What are the main points in this document?"
            },
            {
                "type": "file",
                "file": {
                    "filename": "document.pdf",
                    "file_data": "https://arxiv.org/pdf/2507.23261"
                }
            },
        ]
    }
]
# Optional: Configure PDF processing engine
plugins = [
    {
        "id": "file-parser",
        "pdf": {
            "engine": "mistral-ocr"
        }
    }
]
payload = {
    "model": "google/gemini-2.5-flash-lite",
    "messages": messages,
    "plugins": plugins
}
response = requests.post(url, headers=headers, json=payload)
out = response.json()["choices"][0]["message"]["content"]
print(out)