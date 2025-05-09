from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from models.schema import InterviewProperties, InterviewResponse, ChatRequest, ChatResponse, Instructions, InterviewRequest
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
        
        # Get Instructions
        interview = db_service.get_interview_props(request.interview_id)
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found.")
        
        # Convert interview properties to InterviewProperties object
        interview= InterviewProperties(
                candidate_name= interview['CandidateName'],
                job_title= interview['JobTitle'],
                number_of_questions= interview['NumberOfQuestions'],
                interview_type= interview['InterviewType'],
                skills= interview['Skills'].split(',') if interview['Skills'] else [],
            )
        
        # Initialize Instructions
        instructions = db_service.get_instructions(interview.interview_type,
                                                    interview.job_title.lower().replace(' ', ''))        
        
        if instructions:
            instructions_content = instructions.content
        else:
            instructions_content = instruction_chain.invoke({
                "candidate_name": interview.candidate_name,
                "job_title": interview.job_title,
                "number_of_questions": interview.number_of_questions,
                "skills": interview.skills,
                "interview_type": interview.interview_type,
            })
            db_service.add_instructions(Instructions(
                                            job_title=interview.job_title.lower().replace(' ', ''),
                                            interview_type=interview.interview_type,
                                            content=instructions_content,
                                        )
            )
        
        # Construct Chain input
        chain_input = {
            "candidate_name": interview.candidate_name,
            "job_title": interview.job_title,
            "number_of_questions": interview.number_of_questions,
            "skills": interview.skills,
            "instructions": instructions_content,
            "chat_history": [HumanMessage("Hello")],
        }
        
        # Determine the chain based on interview type
        chain = interview_chains[interview.interview_type]
        
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
        interview = db_service.get_interview_props(request.interview_id)
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found.")
        
        # Convert interview properties to InterviewProperties object
        interview= InterviewProperties(
                candidate_name= interview['CandidateName'],
                job_title= interview['JobTitle'],
                number_of_questions= interview['NumberOfQuestions'],
                interview_type= interview['InterviewType'],
                skills= interview['Skills'].split(','),
            )
        
        # Get Instructions
        instructions_content = db_service.get_instructions(interview.interview_type, interview.job_title)
        if not instructions_content:
            raise HTTPException(status_code=404, detail="Problem while fetching interview, Maybe it was not initialized.")
        
        
        # Load Chat History in Langchain format
        roles = {"user": HumanMessage, "assistant": AIMessage}
        
        # Fetch chat history from the database
        history = db_service.get_chat_history(request.interview_id)
        if not history:
            raise HTTPException(status_code=404, detail="No Chat History found.")
        
        # Convert chat history to Langchain format
        chat_history = []
        for message in history:
            role = roles[message['Role']]
            chat_history.append(role(content=message['Message']))
        
        # Append user message to chat history
        chat_history.append(HumanMessage(content=request.prompt))
        
        # Construct Chain input
        chain_input = {
            "candidate_name": interview.candidate_name,
            "job_title": interview.job_title,
            "number_of_questions": interview.number_of_questions,
            "skills": interview.skills,
            "instructions": instructions_content,
            "chat_history": chat_history,
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