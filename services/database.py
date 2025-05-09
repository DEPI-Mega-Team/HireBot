from sqlalchemy.orm import Session
from models.schema import Instructions, InterviewProperties, ChatMessage
from dotenv import load_dotenv
from config.database import get_mssql_connection
import os


class DatabaseService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_instructions(self, interview_type: str, job_title: str) -> str:
        """Fetch Instructions from database using the instructions ID"""
        
        return self.db.query(Instructions).filter(Instructions.interview_type == interview_type and Instructions.job_title == job_title).first()
    
    def add_instructions(self, instructions: Instructions) -> None:
        """Add instructions to the database"""
        
        self.db.add(instructions)
        
        try:
            self.db.commit()
        except Exception as e:
            print(f"Error adding instructions: {e}")
            self.db.rollback()
            raise e
    
    def del_instructions(self, instruction_id: int) -> None:
        """Delete instructions from the database"""
        
        instructions = self.db.query(Instructions).filter(Instructions.instruction_id == instruction_id).first()
        
        if instructions:
            self.db.delete(instructions)
            self.db.commit()
        else:
            raise Exception(f"Instructions with ID {instruction_id} not found.")
    
    def get_interview_props(self, interview_id: int) -> str:
        """Fetch Interview from database using the interview ID"""
        
        with get_mssql_connection() as conn, conn.cursor(as_dict= True) as cursor:
            columns = ['CandidateName', 'JobTitle', 'InterviewType', 'NumberOfQuestions', 'Skills']
            columns = ', '.join(columns)
        
            cursor.execute(f"SELECT {columns} FROM interviews WHERE interview_id = {interview_id};")
            interview = cursor.fetchone()
        
        return interview
    
    def get_chat_history(self, interview_id: int) -> str:
        """Fetch Chat History from database using the interview ID"""
        
        with get_mssql_connection() as conn, conn.cursor(as_dict= True) as cursor:
            cursor.execute(f"SELECT Role, Message FROM ChatMessages WHERE InterviewId = {interview_id} ORDER BY Id ASC;")
            chat_history = cursor.fetchall()
        
        return chat_history