import speech_recognition
from gtts import gTTS
from openai import OpenAI
import pygame
import time

# Khởi tạo OpenAI client
client = OpenAI(
 api_key="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"
)

# Khởi tạo bộ nhận dạng và pygame
robot_ear = speech_recognition.Recognizer()
pygame.mixer.init()

print("🤖 Robot đã sẵn sàng. Nhấn Ctrl+C để thoát.\n")

try:
    while True:
        with speech_recognition.Microphone() as mic:
            print("Robot: Mình đang nghe... (timeout=5s, giới hạn 10s)")
            try:
                robot_ear.adjust_for_ambient_noise(mic)
                audio = robot_ear.listen(mic, timeout=10, phrase_time_limit=30)
                print("Robot: Đã ghi âm xong. Đang xử lý...")

                try:
                    you = robot_ear.recognize_google(audio, language="vi-VN")
                except speech_recognition.UnknownValueError:
                    you = ""
                    print("Robot: Xin lỗi, mình không hiểu bạn nói gì.")
                except speech_recognition.RequestError:
                    you = ""
                    print("Robot: Không kết nối được với dịch vụ nhận dạng giọng nói.")

                print("Bạn: " + you)

                if you != "":
                    # Gọi GPT để phản hồi
                    completion = client.chat.completions.create(
                        model="gpt-4.1-nano",
                        messages=[
                            {"role": "system", "content": "Bạn trả lời ngắn gọn, súc tích"},
                            {"role": "user", "content": you}
                        ],
                        temperature=0.6,
                        max_tokens=100
                    )
                    robot_brain = completion.choices[0].message.content
                else:
                    robot_brain = "Tôi không nghe rõ bạn nói gì."

            except speech_recognition.WaitTimeoutError:
                robot_brain = "Bạn đã không nói gì trong 5 giây. Mình dừng nghe."
                print("Robot: " + robot_brain)

            except Exception as e:
                robot_brain = f"Có lỗi xảy ra: {str(e)}"
                print("Robot: " + robot_brain)

            # Phản hồi bằng giọng nói
            try:
                audio_response = client.audio.speech.create(
                    model="tts-1",
                    voice="nova",
                    input=robot_brain
                )
                with open("voice.mp3", "wb") as file:
                    file.write(audio_response.content)

                pygame.mixer.music.load("voice.mp3")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            except Exception as e:
                print("Robot: Không thể phát âm thanh. Lỗi:", str(e))

except KeyboardInterrupt:
    print("\n👋 Robot: Tạm biệt bạn. Hẹn gặp lại!")

