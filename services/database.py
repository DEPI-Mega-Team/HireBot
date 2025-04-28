from sqlalchemy.orm import Session
from models.schema import Interview

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db

    def get_interview(self, interview_id: int) -> Interview:
        """Fetch Interview Data from database using the interview ID"""
        
        return self.db.query(Interview).filter(Interview.interview_id == interview_id).first()

    def add_interview(self, interview: Interview) -> None:
        """Add interview to the database"""
        self.db.add(interview)
        
        try:
            self.db.commit()
        except Exception as e:
            print(f"Error adding interview: {e}")
            self.db.rollback()
            raise e
        
    def del_interview(self, interview_id: int) -> None:
        """Delete interview from the database"""
        
        interview = self.db.query(Interview).filter(Interview.interview_id == interview_id).first()
        
        if interview:
            self.db.delete(interview)
            self.db.commit()
        else:
            raise Exception(f"Interview with ID {interview_id} not found.")