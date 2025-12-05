# import requests

# HF_API_TOKEN = ""
# HF_MODEL = "google/flan-t5-base"  # or any other free model
# HF_API_URL = f"https://router.huggingface.co/models/{HF_MODEL}"  # NEW endpoint

# prompt = "Recommend 5 IT careers for someone with skills: QA, Testing, Coding."

# headers = {
#     "Authorization": f"Bearer {HF_API_TOKEN}",
#     "Content-Type": "application/json"
# }

# payload = {"inputs": prompt}

# response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)

# print("Status code:", response.status_code)
# print("Response:", response.text)


# from transformers import pipeline

# # Initialize pipeline
# pipe = pipeline("text-generation", model="deepseek-ai/DeepSeek-V3.2")

# # Example test
# messages = [
#     {"role": "user", "content": "I have skills in testing, QA, and coding. Recommend careers."}
# ]

# output = pipe(messages)
# print(output)






# from transformers import pipeline

# # Load instruction-tuned Flan-T5 large model
# pipe = pipeline(
#     "text-generation",
#     model="google/flan-t5-large",
#     device=0  # 0 for GPU, remove or set to -1 for CPU
# )

# prompt = """
# Suggest 10 careers for a person with these skills: Quality Assurance
# For each career, write the name and a motivational 1-line description.
# Format: Career Name: Description
# """

# output = pipe(prompt, max_new_tokens=300, do_sample=True, temperature=0.7)
# text = output[0]['generated_text']
# print(text)





# from transformers import pipeline

# # Use the correct pipeline
# pipe = pipeline("text2text-generation", model="google/flan-t5-small")

# prompt = """
# Write a motivational 1-sentence description for the career "QA Engineer"
# for someone with skills: Quality Assurance, Testing, Attention to Detail,
# interests: Reading, Problem Solving, and studied subjects: ICT, Accounting.
# """


# output = pipe(
#     prompt,
#     max_new_tokens=50,
#     do_sample=True,
#     temperature=0.7,
#     top_p=0.9,
#     repetition_penalty=2.0   # <-- prevents repetitive output
# )

# print("AI Output:\n")
# print(output[0]['generated_text'])





# from transformers import pipeline
# print("Transformers pipeline is working!")




from google import genai

client = genai.Client(api_key="yyy")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Give 3 motivational career suggestions for someone skilled in Quality Assurance, Testing, and Planning."
)
print(response.text)

