## Overview
HireBot is an advanced AI-powered chatbot designed to assist with interview preparation and execution. It leverages state-of-the-art language models to generate interview instructions, conduct behavioral and technical interviews, and provide feedback to users. The chatbot is tailored to ensure professional standards and industry best practices are followed.

## Features
- **Interview Instructions**: Generates clear and actionable instructions for interviewers.
- **Behavioral Interviews**: Conducts interviews focusing on past experiences and situations.
- **Technical Interviews**: Conducts interviews focusing on technical knowledge and skills.
- **Feedback and Summarization**: Provides performance summaries and feedback at the end of the interview.

## How to Use
The chatbot operates through two primary chains:

1. **Instructions Chain**
   - Generates customized interview instructions
   - Takes input parameters:
     - Interview type (Technical/Behavioral)
     - Job title

2. **Interview (Technical/Behavioral) Chain**
   - Processes the generated instructions
   - Conducts structured interviews (Technical/Behavioral)
   - Adapts questioning based on candidate responses
   - Maintains professional interview standards

More specific applied examples in branches:
- `streamlit`: Interactive web application with a polished user interface.
- `api`: Endpoints ImplementationZz using Fast API  + Database

## Project Structure
- `app/__init__.py`: Initializes the application.
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