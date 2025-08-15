import streamlit as st
from langchain_groq import ChatGroq

# Load GROQ API key from Streamlit secrets
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant",
    temperature=0
)

if __name__ == "__main__":
    response = llm.invoke("What are the main ingredients in a cake?")
    print(response.content)

