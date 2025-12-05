import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load model & tokenizer
model_name = "EleutherAI/gpt-neo-125M"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Streamlit UI
st.title("Small Free GPT-Neo Test")
prompt = st.text_input("Enter your prompt:")

if prompt:
    # Tokenize input
    inputs = tokenizer(prompt, return_tensors="pt")

    # Generate output with settings to reduce repetition
    outputs = model.generate(
        **inputs,
        max_new_tokens=50,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.5,           # less randomness
        repetition_penalty=1.2,    # avoid repeating
        pad_token_id=tokenizer.eos_token_id
    )

    # Decode and truncate to first sentence
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    text = text.split(".")[0] + "."

    st.write(text)
