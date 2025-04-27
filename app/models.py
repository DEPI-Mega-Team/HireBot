import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()

class GeminiModel:
    def __init__(self):
        self.embedding = GoogleGenerativeAIEmbeddings(
            model='models/text-embedding-004', 
            google_api_key=os.getenv('GOOGLE_API_KEY'),
            )
        
        self.model = ChatGoogleGenerativeAI(
            model='gemini-2.0-flash',
            api_key=os.getenv('GOOGLE_API_KEY'),
            temperature= 0.2,
        )