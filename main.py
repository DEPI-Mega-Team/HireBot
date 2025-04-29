from fastapi import FastAPI, HTTPException, Request, Depends, Body
from fastapi.responses import JSONResponse
from models.schema import InterviewProperties, InterviewResponse, ChatRequest, ChatResponse, Instructions
import gc


print("Loading Services...")
from app.chains import instruction_chain, interview_chains
from langchain_core.messages import AIMessage, HumanMessage

from sqlalchemy.orm import Session
from services.database import DatabaseService
from config.database import get_db, engine, Base
print("Services Loaded successfully.")

print("Declaring Variables...")
interview_types = interview_chains.keys()
print("Variables Declared successfully.")

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HireBot: Mock Interview Chatbot")

# Initialize middleware
@app.middleware("http")
async def cleanup_after_request(request: Request, call_next):
    response = await call_next(request)
    gc.collect()
    return response


# Initialize End-Points
@app.get("/healthy", description="Check if the server is healthy")
async def health_check() -> JSONResponse:
    """
    Health check endpoint to verify if the server is running.
    """
    return JSONResponse(content={"status": "healthy"})


@app.post("/init_interview", description="Initialize a new interview session")
async def init_interview(request: InterviewProperties, db: Session = Depends(get_db)) -> JSONResponse:
    """
    Initialize a new interview session.
    """    
    
    try:
        # Initialize database service
        db_service = DatabaseService(db)
        
        if not request.skills:
            request.skills = []
        
        # Initialize Instructions
        instructions = db_service.get_instructions(request.interview_type, request.job_title.lower().replace(' ', ''))        
        
        if instructions:
            instructions_content = instructions.content
        else:
            instructions_content = instruction_chain.invoke({
                "candidate_name": request.candidate_name,
                "job_title": request.job_title,
                "number_of_questions": request.number_of_questions,
                "skills": request.skills,
                "interview_type": request.interview_type,
            })
            db_service.add_instructions(Instructions(
                                            job_title=request.job_title,
                                            interview_type=request.interview_type,
                                            content=instructions_content,
                                        )
            )
        
        # Construct Chain input
        chain_input = {
            "candidate_name": request.candidate_name,
            "job_title": request.job_title,
            "number_of_questions": request.number_of_questions,
            "skills": request.skills,
            "instructions": instructions_content,
            "chat_history": [HumanMessage("Hello")],
        }
        
        # Determine the chain based on interview type
        chain = interview_chains[request.interview_type]
        
        # Generate response
        response = chain.invoke(chain_input)
        
        return InterviewResponse(response= response)
    
    except Exception as e:
        if 'status_code' in str(e):
            # If the exception is already an HTTPException, re-raise it
            raise e
        else:
            # Otherwise, raise a new HTTPException with a 500 status code
            raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/chat", response_model= ChatResponse, description="Proceed a Chat session or create a new one")
async def chat(request: ChatRequest,  db: Session = Depends(get_db)) -> JSONResponse:
    """
    Proceed a chat session or create a new one.
    """
    try:
        # Initialize database service
        db_service = DatabaseService(db)
        
        # Get Instructions
        interview_properties = request.interview_properties
        instructions_content = db_service.get_instructions(interview_properties.interview_type, interview_properties.job_title)
        
        # Load Chat History in Langchain format
        roles = {"user": HumanMessage, "assistant": AIMessage}
        
        chat_history = []
        for message in request.chat_history:
            role = roles[message.role]
            chat_history.append(role(content=message.message))
        
        # Set chat history in request
        request.chat_history = chat_history
        
        # Append user message to chat history
        request.chat_history.append(HumanMessage(content=request.prompt))
        
        # Construct Chain input
        chain_input = {
            "candidate_name": interview_properties.candidate_name,
            "job_title": interview_properties.job_title,
            "number_of_questions": interview_properties.number_of_questions,
            "skills": interview_properties.skills,
            "instructions": instructions_content,
            "chat_history": request.chat_history,
        }
        
        # Determine the chain based on interview type
        chain = interview_chains[interview_properties.interview_type]
        
        # Generate response
        response = chain.invoke(chain_input)

        # Check Ending of Interview
        if "END OF INTERVIEW" in response:
            ended = True
            # Remove the "END OF INTERVIEW" part from the response
            response = response.replace("END OF INTERVIEW", "").strip()
        else:
            ended = False
        
        return ChatResponse(
            response= response,
            ended=ended,
        )

    except Exception as e:
        if 'status_code' in str(e):
            # If the exception is already an HTTPException, re-raise it
            raise e
        else:
            # Otherwise, raise a new HTTPException with a 500 status code
            raise HTTPException(status_code=500, detail=str(e)) from e