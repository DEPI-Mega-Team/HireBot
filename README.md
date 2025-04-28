## Overview
HireBot is an advanced AI-powered chatbot designed to assist with interview preparation and execution. It leverages state-of-the-art language models to generate interview instructions, conduct behavioral and technical interviews, and provide feedback to users. The chatbot is tailored to ensure professional standards and industry best practices are followed.

## Features
- **Interview Instructions**: Generates clear and actionable instructions for interviewers.
- **Behavioral Interviews**: Conducts interviews focusing on past experiences and situations.
- **Technical Interviews**: Conducts interviews focusing on technical knowledge and skills.
- **Feedback and Summarization**: Provides performance summaries and feedback at the end of the interview.

## How to Use
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up environment variables:
   - Create a `.env` file in the root directory.
   - Add your Google API key:
     ```
     GOOGLE_API_KEY=your_google_api_key
     ```
3. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation

### Health Check
**Endpoint**: `/healthy`  
**Method**: `GET`  
**Description**: Verifies if the server is running and healthy.  
**Response**:
```json
{
  "status": "healthy"
}
```

---

### Initialize Interview
**Endpoint**: `/init_interview`  
**Method**: `POST`  
**Description**: Initializes a new interview session by generating interview instructions and storing the session in the database.  

**Request Model**:
```json
{
  "interview_id": int,
  "candidate_name": str,
  "job_title": str,
  "interview_type": str,
  "number_of_questions": int,
  "skills": list[str]
}
```

**Request Attributes**:
- `interview_id` (int): Unique identifier for the interview.
- `candidate_name` (str): Name of the candidate (required).
- `job_title` (str): Job title for the interview (required).
- `interview_type` (str): Type of interview. Allowed values:
  - `"technical"`
  - `"behavioral"`
- `number_of_questions` (int): Number of questions in the interview. Default is 5, must be greater than 0.
- `skills` (list[str]): List of skills to focus on during the interview (optional).

**Response Model**:
```json
{
  "interview_id": int,
  "response": str
}
```

**Response Attributes**:
- `interview_id` (int): Unique identifier for the interview.
- `response` (str): Generated instructions and initial response.

**Error Responses**:
- `400`: Invalid interview type or number of questions.
- `500`: Internal server error.

---

### Chat
**Endpoint**: `/chat`  
**Method**: `POST`  
**Description**: Proceeds with a chat session or creates a new one by interacting with the chatbot.  

**Request Model**:
```json
{
  "interview_id": int,
  "chat_history": list[ChatMessage]
  "prompt": str
}
```

**Request Attributes**:
- `interview_id` (int): Unique identifier for the interview (required).
- `chat_history` (list[ChatMessage]): List of previous chat messages (optional). Each message contains:
  - `role` (str): Role of the message sender. Allowed values:
    - `"user"`
    - `"assistant"`
  - `message` (str): Content of the message.
- `prompt` (str): New user prompt to continue the chat (required).

**Response Model**:
```json
{
  "interview_id": int,
  "response": str,
  "ended": bool
}
```

**Response Attributes**:
- `interview_id` (int): Unique identifier for the interview.
- `response` (str): Chatbot's response to the prompt.
- `ended` (bool): Indicates if the interview has ended.

**Error Responses**:
- `404`: Interview not found.
- `500`: Internal server error.

---

## Request and Response Models

### InterviewRequest
- **Attributes**:
  - `interview_id` (int): Unique identifier for the interview.
  - `candidate_name` (str): Name of the candidate (required).
  - `job_title` (str): Job title for the interview (required).
  - `interview_type` (str): Type of interview, allowed values: `"technical"`, `"behavioral"` (required).
  - `number_of_questions` (int): Number of questions, default is 5, must be greater than 0.
  - `skills` (list[str]): List of skills to focus on, optional.

### InterviewResponse
- **Attributes**:
  - `interview_id` (int): Unique identifier for the interview.
  - `response` (str): Generated instructions and initial response.

### ChatMessage
- **Attributes**:
  - `role` (str): Role of the message sender, allowed values: `"user"`, `"assistant"`.
  - `message` (str): Content of the message.

### ChatRequest
- **Attributes**:
  - `interview_id` (int): Unique identifier for the interview (required).
  - `chat_history` (list[ChatMessage]): List of previous chat messages, optional.
  - `prompt` (str): New user prompt to continue the chat (required).

### ChatResponse
- **Attributes**:
  - `interview_id` (int): Unique identifier for the interview.
  - `response` (str): Chatbot's response to the prompt.
  - `ended` (bool): Indicates if the interview has ended.

---

## Restricted Values for Attributes
- `interview_type`: `"technical"`, `"behavioral"`.
- `role` (in `ChatMessage`): `"user"`, `"assistant"`.

---

## Project Structure
- `app/utils.py`: Contains utility functions like `clear_markdown`.
- `app/templates.py`: Defines templates for interview instructions and processes.
- `app/models.py`: Configures the GeminiModel using Google Generative AI.
- `app/messages.py`: Stores system and human messages for different interview types.
- `app/chains.py`: Defines the chains for processing interview instructions and conducting interviews.

## Technologies Used
- **Python**: Core programming language.
- **LangChain**: Framework for building language model applications.
- **Google Generative AI**: Used for chat model.
- **dotenv**: For managing environment variables.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.