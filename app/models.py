import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()

class GeminiModel:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required.")

        # Initialize the embedding and model
        self.embedding = GoogleGenerativeAIEmbeddings(
            model= 'models/text-embedding-004', 
            google_api_key= self.api_key,
            )
        
        # Initialize the model
        self.model = ChatGoogleGenerativeAI(
            model= 'gemini-2.0-flash',
            api_key= self.api_key,
            temperature= 0.2,
        )