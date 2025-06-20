from app.db.client import MongoDBClient
from app.schemas.auth_schema import Auth
from app.schemas.student_schema import Students
from app.schemas.teacher_scherma import Teachers
from app.schemas.common import Subjects, MonthlyPerformanceTracker, UserRoles
from app.schemas.fee_schema import Installments
from bson import ObjectId
from typing import Dict, List

class AdminRepository:
    def __init__(self, db: MongoDBClient) -> ObjectId|None:
        self.db = db
    
    def create_new_user_auth(self, user:Auth, collection_name:str = "auth"):
        return self.db.insert(collection_name, user.model_dump(exclude={"id"}))
    
    def create_new_roles(self, user:UserRoles, collection_name:str="user-roles"):
        return self.db.insert(collection_name, user.model_dump(by_alias=True))

    def save_student_profile(self, student:Students, collection_name:str="students"):
        return self.db.insert(collection_name, student.model_dump(by_alias=True))
        
    def get_preferred_subjects(self, grade_subjects:Dict[int, List[str]], collection_name:str="subjects") -> List[Subjects] | None:
        return list(self.db.find(collection_name, {
                "$or":[
                    {"grade":grade_item, "name":{"$in":preferred_subjects}} for grade_item, preferred_subjects in grade_subjects.items()
                ]
            })
            )
    
    def add_mapped_student_subject(self, student_objID:ObjectId, subject_objIDs:List[ObjectId], collection_name:str="student-subjects") -> List[ObjectId] | None:
        student_subject_mappings = [
            {
                "studentID":student_objID,
                "subjectID":subject_objID
            } for subject_objID in subject_objIDs
        ]
        return self.db.insert_many(collection_name, student_subject_mappings)
    
    def add_mapped_student_monthly_performance_tracker(self, performance_trackers:List[MonthlyPerformanceTracker], collection_name:str="student-monthly-performance-trackers") -> List[ObjectId] | None:
        performance_trackers = [
            tracker.model_dump(by_alias=True) for tracker in performance_trackers
        ]
        return self.db.insert_many(collection_name, performance_trackers)
    
    def get_fee_type_configurations(self, collection_name:str="fee-type-configurations") -> Dict[str, str] | None:
        return self.db.find_one(collection_name, {"_id":"fee_type"})
    
    def get_coaching_modes(self, mode_type:str, collection_name:str="coaching-mode-config") -> Dict[str, str] | None:
        return self.db.find_one(collection_name, {"name":mode_type})
    
    def add_installments(self, installments:List[Installments], collection_name:str="installments") -> List[ObjectId] | None:
        installments = [installment.model_dump(by_alias=True) for installment in installments]
        return self.db.insert_many(collection_name, installments)
    
    def save_teacher_profile(self, teacher:Teachers, collection_name:str="teachers"):
        return self.db.insert(collection_name, teacher.model_dump(by_alias=True))
    
    def map_teacher_subject(self, teacher_objID:ObjectId, subject_objIDs:List[ObjectId], collection_name:str="teacher-subjects") -> List[ObjectId] | None:
        teacher_subject_mappings = [
            {
                "teacherID":teacher_objID,
                "subjectID":subject_objID
            } for subject_objID in subject_objIDs
        ]
        return self.db.insert_many(collection_name, teacher_subject_mappings)