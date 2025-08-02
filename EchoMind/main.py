import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests



recognizer = sr.Recognizer()

newsapi = "cd1651781f5b405dbb1c63d2d4f22490"
apiKey = "AIzaSyBXNnpL8o1SPCda4040gUMGmgzYpVuPBsY"  

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def proceedCommand(c):
    c_lower = c.lower()
    if "open google" in c_lower:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
    elif "open facebook" in c_lower:
        speak("Opening Facebook")
        webbrowser.open("https://www.facebook.com")    
    elif "open youtube" in c_lower:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
    elif "what is your name" in c_lower:
        speak("I am Jarvis, your personal assistant.")

    elif c_lower.startswith("play "):
        song_name = c_lower.replace("play ", "").strip()
        if song_name in musicLibrary.music:
            speak(f"Playing {song_name}")
            webbrowser.open(musicLibrary.music[song_name])
        else:
            speak(f"I couldn't find the song {song_name} in your music library.")


    
    elif "news" in c_lower:
        try:
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}"
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
                articles = data.get("articles", [])
                if articles:
                    for article in articles[:5]:
                        title = article.get("title", "No title")
                        description = article.get("description", "No description")
                        if len(description) > 200:
                            description = description[:200] + "..."
                        speak(f"Title: {title}. Description: {description}")
                else:
                    speak("No news articles found.")
            else:
                speak("Failed to fetch news.")
        except Exception as e:
            speak(f"An error occurred while fetching news: {e}")

    elif "activate" in c_lower:
        chatbot_mode()

    
        
conversation_history = []

def chatbot_mode():
    speak("Chatbot mode activated. You can ask anything. Say 'exit' to stop.")
    while True:
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening for your question...")
                audio = r.listen(source, timeout=8, phrase_time_limit=15)
            user_query = r.recognize_google(audio)
            print(f"You said: {user_query}")
            if user_query.lower() in ["exit", "stop"]:
                speak("Exiting chatbot mode.")
                break
            # Add user message to history
            conversation_history.append({"role": "user", "text": user_query})

            # Prepare Gemini API payload with history
            payload = {
                "contents": [
                    {
                        "role": msg["role"],
                        "parts": [{"text": msg["text"]}]
                    } for msg in conversation_history
                ]
            }
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={apiKey}"
            headers = {"Content-Type": "application/json"}
            r_api = requests.post(url, headers=headers, json=payload)
            if r_api.status_code == 200:
                data = r_api.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        ai_text = parts[0].get("text", "")
                        # Add AI response to history
                        conversation_history.append({"role": "assistant", "text": ai_text})
                        speak(ai_text)
                    else:
                        speak("No response received.")
                else:
                    speak("No candidates found.")
            else:
                print("Gemini API error details:", r_api.text)  # <-- Add this line
                speak("Failed to get response from AI.")
        except Exception as e:
            speak(f"Error: {e}")




if __name__ == "__main__":
    speak("Say something and I will recognize it.")

    while True:
        r = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                print("Listening... Please speak now.")
                audio = r.listen(source, timeout=5, phrase_time_limit=8)
            command = r.recognize_google(audio)
            print(f"You said: {command}")
            if "hello" in command.lower():
                speak("Yes.")
                with sr.Microphone() as source:
                    print("EchoMind is active, please say your command.")
                    audio = r.listen(source, timeout=5, phrase_time_limit=8)
                    sub_command = r.recognize_google(audio)
                    print(f"You said: {sub_command}")
                    proceedCommand(sub_command)
            else:
                proceedCommand(command)
        except sr.WaitTimeoutError:
            print("Listening timed out, please try again.")
        except Exception as e:
            print(f" error; {e}")


