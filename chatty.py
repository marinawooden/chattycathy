"""
Author: Marina Wooden
Date: 04-12-2024
Description: The chatty cathy bot, which allows you to have a conversation with an ai
person.
"""
# speech recognition libs
import speech_recognition as sr
import io
import soundfile as sf
import sounddevice as sd

# env vars read
import os
from dotenv import load_dotenv

# init chatgpt + whisper + related stufz
from openai import OpenAI
from pathlib import Path

# regex
import re

# open image
from PIL import Image

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

openai_client = OpenAI()

# terminal colors
class bcolors:
    CATHY = '\u001b[44m'
    USER = '\u001b[43m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Cathy():
    def __init__(self, role):
      self.messages = [
        {
          "role": "system",
          "content": f"""
            You're Chatty Cathy - an AI friend bot.
            The user will tell you who they want you to pretend to be,
            and you'll mimic the speech patterns of that person.
            Remember to keep it fun and casual!  Your friend wants
            you to pretend to be {role}
          """
        }
      ]
      self.role = role

      img = Image.open('assets/barack.jpg')
      img.show()

      print("Hello! You're talking to Chatty Cathy!")

    def think(self):
      # get response from bot
      cathy_resp = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=self.messages
      )

      cathy_resp = cathy_resp.choices[0].message.content
      print(f"{bcolors.CATHY}Cathy said:{bcolors.ENDC} {cathy_resp}")
      return cathy_resp
    
    def say(self, words):
      self.messages.append({"role": "assistant", "content": words})
      
      # response to speech
      spoken_response = openai_client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=words
      )

      # render speech without saving a file    
      buffer = io.BytesIO()
      for chunk in spoken_response.iter_bytes(chunk_size=4096):
        buffer.write(chunk)

      buffer.seek(0)

      with sf.SoundFile(buffer, 'r') as sound_file:
        data = sound_file.read(dtype='int16')
        sd.play(data, sound_file.samplerate)
        sd.wait()

    def listen(self):
      r = sr.Recognizer()
      with sr.Microphone() as source:
          audio = r.listen(source)

      # recognize speech using Whisper API
      try:
        my_resp = r.recognize_whisper_api(audio, api_key=OPENAI_API_KEY)
        print(f"{bcolors.USER}You said:{bcolors.ENDC} {my_resp}")

        # log client message to conversation roster
        self.messages.append({"role": "user", "content": my_resp})

        # have cathy come up with a response and then play it out
        cathy_resp = self.think()
        self.say(cathy_resp)

        # add response to conversation
        self.messages.append({"role": "assistant", "content": cathy_resp})

        return my_resp
      except sr.RequestError as e:
        print(f"Could not request results from Whisper API; {e}")
        return "Bye-bye."

def main():
  sys_role = input("Who do you want to talk to? ")

  bot = Cathy(sys_role)
  cathy_resp = bot.think()
  bot.say(cathy_resp)

  speech = ""
  while not re.match(r'Bye-?bye[!.]?', speech, re.IGNORECASE):
    speech = bot.listen()


if __name__ == '__main__':
  main()