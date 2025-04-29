from sqlalchemy.orm import Session
from models.schema import Instructions

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