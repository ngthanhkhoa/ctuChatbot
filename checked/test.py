
from openai import OpenAI

client = OpenAI(
  api_key="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"
)
print("Bạn hãy đặt câu hỏi")
you = input()

try:
	completion = client.chat.completions.create(
	  model="gpt-4.1-nano",
	  messages=[
	    {"role": "system", "content": "Bạn trả lời ngắn gọn"},
	    {"role": "user", "content": you}
	  ],
	  temperature = 0.7,
	  max_tokens = 100
	)
	robot_brain=completion.choices[0].message.content
except:
	robot_brain="Tôi đang bận, vui lòng liên hệ lại sau nhé!"
print(robot_brain)

