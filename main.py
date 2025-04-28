from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from models.schema import InterviewRequest, InterviewResponse, Interview, ChatRequest, ChatResponse
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
async def init_interview(request: InterviewRequest, db: Session = Depends(get_db)) -> JSONResponse:
    """
    Initialize a new interview session.
    """    
    
    try:
        # Initialize database service
        db_service = DatabaseService(db)
        
        # Validate request data
        if request.interview_type not in interview_types:
            raise HTTPException(status_code=400, detail=f"Invalid interview type, must be one of the following: {interview_types}")
        
        if request.number_of_questions <= 0:
            raise HTTPException(status_code=400, detail="Number of questions must be greater than 0")
        
        if not request.skills:
            request.skills = []
        
        # Initialize Instructions
        instructions = instruction_chain.invoke({
            "candidate_name": request.candidate_name,
            "job_title": request.job_title,
            "number_of_questions": request.number_of_questions,
            "skills": request.skills,
            "interview_type": request.interview_type,
        })
        
        # Make Interview Data Object
        interview = Interview(
            interview_id= request.interview_id,
            candidate_name= request.candidate_name,
            job_title= request.job_title,
            interview_type= request.interview_type,
            number_of_questions= request.number_of_questions,
            skills= request.skills,
            instructions= instructions,
        )
        
        # Store interview data in the database
        db_service.add_interview(interview)
        
        # Construct Chain input
        chain_input = {
            "candidate_name": interview.candidate_name,
            "job_title": interview.job_title,
            "number_of_questions": interview.number_of_questions,
            "skills": interview.skills,
            "instructions": interview.instructions,
            "chat_history": [HumanMessage("Hello")],
        }
        
        # Determine the chain based on interview type
        chain = interview_chains[request.interview_type]
        
        # Generate response
        response = chain.invoke(chain_input)
        
        return InterviewResponse(interview_id=request.interview_id, response=response)
    
    except Exception as e:
        if 'status_code' in str(e):
            # If the exception is already an HTTPException, re-raise it
            raise e
        else:
            # Otherwise, raise a new HTTPException with a 500 status code
            raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/chat", response_model=ChatResponse, description="Proceed a Chat session or create a new one")
async def chat(request: ChatRequest,  db: Session = Depends(get_db)) -> JSONResponse:
    """
    Proceed a chat session or create a new one.
    """
    try:
        # Initialize database service
        db_service = DatabaseService(db)
        
        # Get interview data from the database
        interview = db_service.get_interview(request.interview_id)
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
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
            "candidate_name": interview.candidate_name,
            "job_title": interview.job_title,
            "number_of_questions": interview.number_of_questions,
            "skills": interview.skills,
            "instructions": interview.instructions,
            "chat_history": request.chat_history,
        }
        
        # Determine the chain based on interview type
        chain = interview_chains[interview.interview_type]
        
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
            interview_id=interview.interview_id,
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