import socket
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

load_dotenv()

def check_dns():
    host = "generativelanguage.googleapis.com"
    print(f"Checking DNS for {host}...")
    try:
        addr = socket.getaddrinfo(host, 443)
        print(f"Address: {addr}")
    except Exception as e:
        print(f"socket.getaddrinfo failed: {e}")

def check_gemini():
    print("\nChecking ChatGoogleGenerativeAI...")
    api_key = os.getenv("GEMINI_API_KEY")
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0
        )
        response = llm.invoke([HumanMessage(content="Hello")])
        print(f"Response success: {response.content}")
    except Exception as e:
        print(f"Gemini call failed: {e}")

if __name__ == "__main__":
    check_dns()
    check_gemini()
