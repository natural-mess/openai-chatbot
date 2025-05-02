# openai-chatbot
OpenAI chatbot web application to use with OpenAI API key. This web application uses FastAPI, Websocket and Jinja2.

## Prerequisite

Check requirements.txt file

## OpenAI API key

Paste your OpenAI API key in below location of main.py:
```python
client = OpenAI(
    api_key = ""
)
```

## Run application
Run below command to start application locally:
```bash
uvicorn main:app --reload
```

Or deploy if you want.
