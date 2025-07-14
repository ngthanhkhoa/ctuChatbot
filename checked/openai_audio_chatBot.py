import speech_recognition
from gtts import gTTS
from openai import OpenAI
import pygame


client = OpenAI(
 api_key="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"
)
robot_ear = speech_recognition.Recognizer()
robot_brain = ""
pygame.mixer.init()

while True:
	with speech_recognition.Microphone() as mic:
		print("Robot: Mình đang nghe ...")
		audio = robot_ear.listen(mic)		
		print("Robot: ...")
	
	try:
		you = robot_ear.recognize_google(audio, language ="vi-VN")
	except:
		you=""
	print("You: " + you)
	
	try:
		completion = client.chat.completions.create(
		  model="gpt-4.1-nano",
		  messages=[
		    {"role": "system", "content": "Bạn trả lời ngắn gọn, súc tích"},
		    {"role": "user", "content": you}
		  ],
		  temperature = 0.6,
		  max_tokens = 100
		)
		robot_brain=completion.choices[0].message.content
	except:
		robot_brain="Tôi đang bận, vui lòng liên hệ lại sau nhé!"
	
	print("Robot: " + robot_brain)
	audio_response=client.audio.speech.create(
	  model="tts-1",
	  voice="nova",
	  input=robot_brain
	)
	with open("voice.mp3", "wb") as file:
		file.write(audio_response.content)
		
	pygame.mixer.music.load("voice.mp3")
	pygame.mixer.music.play()
	while pygame.mixer.music.get_busy():
		continue
		
	
	
	
	
	

