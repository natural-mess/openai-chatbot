from openai import OpenAI
from fastapi import FastAPI, Form, Request, WebSocket
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Open AI API key
client = OpenAI(
    api_key = ""
)

# Creates an instance of a FastAPI application
app = FastAPI()

# Create an instance of Jinja2 Templates, directory location is templates
templates = Jinja2Templates(directory="templates")

chat_responses = []

@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "chat_responses": chat_responses})

# Create chat_log to keep history
chat_log = [{"role": "system",
             "content": "You are a helpful assistant."
            }]

# Websocket endpoint
@app.websocket("/ws")
async def chat(websocket: WebSocket):

    await websocket.accept()

    while True:
        user_input = await websocket.receive_text()
        chat_log.append({'role': 'user', 'content': user_input})
        chat_responses.append(user_input)

        try:
            response = client.responses.create(
                model="gpt-3.5-turbo",
                input=chat_log,
                temperature=0.6,
                stream=True
            )

            ai_response = ""

            for event in response:
                # Only process the text deltas (incremental content)
                if event.type == "response.output_text.delta":
                    delta = event.delta  # This is the text content like "Hello"
                    ai_response += delta
                    await websocket.send_text(delta)
            
            chat_log.append({'role': 'assistant', 'content': ai_response})
            chat_responses.append(ai_response)

        except Exception as e:
            await websocket.send_text(f"Error: {str(e)}")
            break

# Chat
@app.post("/", response_class=HTMLResponse)
async def chat(request: Request, user_input: Annotated[str, Form()]):
    chat_log.append({"role": "user", "content": user_input})
    chat_responses.append(user_input)

    # Get response
    response = client.responses.create(
        model="gpt-3.5-turbo",
        input=chat_log,
        temperature=0.6
    )

    bot_reponse = response.output_text
    chat_log.append({"role": "assistant", "content": bot_reponse})

    # Return the response
    chat_responses.append(bot_reponse)
    return templates.TemplateResponse("home.html", {"request": request, "chat_responses": chat_responses})

# Image generation
@app.get("/image", response_class=HTMLResponse)
async def image_page(request: Request):
    return templates.TemplateResponse("image.html", {"request": request})

@app.post("/image", response_class=HTMLResponse)
async def create_image(request: Request, user_input: Annotated[str, Form()]):

    response = client.images.generate(
        prompt=user_input,
        n=1,
        size="256x256"
    )

    image_url = response.data[0].url
    return templates.TemplateResponse("image.html", {"request": request, "image_url": image_url})
