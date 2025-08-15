import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load the .env file into environment variables
load_dotenv()

# Optional check
print("Loaded Key:", os.getenv("GROQ_API_KEY"))

llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0
)

if __name__ == "__main__":
    response = llm.invoke("What are main ingredients in cake?")
    print(response.content)
