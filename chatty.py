"""
Author: Marina Wooden
Date: 04-12-2024
Description: The chatty cathy bot, which allows you to have a conversation with an ai
person.
"""
# speech recognition libs
import speech_recognition as sr

# env vars read
import os
from dotenv import load_dotenv

# init chatgpt
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

gpt_client = OpenAI()

# all messages
messages = [
  {"role": "system", "content": "You're having a casual conversation with a friend."}
]

def main():
  print("Hello! Welcome to speech recognizer!")

  speech = None
  while speech != "bye":
    speech = speech_input()

def speech_input():
  r = sr.Recognizer()
  with sr.Microphone() as source:
      print("Say something!")
      audio = r.listen(source)

  # recognize speech using Whisper API
  try:
    my_resp = r.recognize_whisper_api(audio, api_key=OPENAI_API_KEY)
    print(f"You said: {my_resp}")

    # log your message
    messages.append({"role": "user", "content": my_resp})

    cathy_resp = gpt_client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=messages
    )

    cathy_resp = cathy_resp.choices[0].message.content

    print(f"Cathy said: {cathy_resp}")
    messages.append({"role": "assistant", "content": cathy_resp})

    return my_resp
  except sr.RequestError as e:
    print(f"Could not request results from Whisper API; {e}")
    return "bye"

if __name__ == '__main__':
  main()