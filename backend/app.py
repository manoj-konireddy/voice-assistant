from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import tempfile
import ffmpeg
import speech_recognition as sr
import re
import requests
from processor import generate_response
from faq import search_faq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Voice Assistant!"}


@app.post("/voice-to-text/")
async def voice_to_text(file: UploadFile = File(...)):
    input_path = output_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_input:
            temp_input.write(await file.read())
            input_path = temp_input.name

        output_path = input_path.replace(".webm", ".wav")

        ffmpeg.input(input_path).output(
            output_path, ac=1, ar=16000, format='wav'
        ).global_args("-err_detect", "ignore_err").run(overwrite_output=True, quiet=True)

        recognizer = sr.Recognizer()
        with sr.AudioFile(output_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                return {"transcription": text}
            except sr.UnknownValueError:
                return JSONResponse(content={"error": "Could not understand audio"}, status_code=400)
            except sr.RequestError as e:
                return JSONResponse(content={"error": str(e)}, status_code=500)

    except Exception as e:
        return JSONResponse(content={"error": f"Server error: {str(e)}"}, status_code=500)

    finally:
        if input_path and os.path.exists(input_path):
            os.remove(input_path)
        if output_path and os.path.exists(output_path):
            os.remove(output_path)


@app.post("/chat-response/")
async def chat_response(request: Request):
    try:
        # Handle both form data and JSON
        if request.headers.get("content-type", "").startswith("application/json"):
            data = await request.json()
        else:
            data = await request.form()

        user_input = data.get("user_input")
        if not user_input:
            return JSONResponse(content={"error": "user_input is required"}, status_code=400)

        lower_input = user_input.lower()
        parts = []

        if "time" in lower_input:
            now = datetime.now().strftime("%I:%M %p")
            parts.append(f"The current time is {now}.")

        if "date" in lower_input:
            today = datetime.now().strftime("%B %d, %Y")
            parts.append(f"Today's date is {today}.")

        if "day" in lower_input:
            day = datetime.now().strftime("%A")
            parts.append(f"Today is {day}.")

        if "weather" in lower_input:
            match = re.search(r"in ([a-zA-Z\s]+)", lower_input)
            city = match.group(1).strip() if match else "Andhra Pradesh"
            key = os.getenv("WEATHER_API_KEY")

            if not key:
                parts.append("Weather API key is not set.")
            else:
                url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric"
                res = requests.get(url)
                if res.status_code == 200:
                    data = res.json()
                    temp = data["main"]["temp"]
                    desc = data["weather"][0]["description"]
                    parts.append(
                        f"The weather in {city} is {desc} with {temp}°C.")
                else:
                    parts.append("I couldn't get the weather right now.")

        if parts:
            return {"response": " ".join(parts)}

        # Default: use DeepSeek
        response = generate_response(user_input)
        return {"response": response}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
