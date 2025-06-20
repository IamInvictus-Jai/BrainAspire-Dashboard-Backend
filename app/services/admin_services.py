# Imports
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from app.repositories.admin_repository import AdminRepository
from app.utils.timeFormat import get_utc_timestamp
from app.core.security import Security
from logging import Logger
from typing import Union, List, Dict
from bson import ObjectId

from app.schemas.auth_schema import Auth
from app.schemas.admin_client_req_res import AddNewStudentRequest, Student as StudentProfile, Installments as ClientSentInstallments
from app.schemas.admin_client_req_res import AddNewTeacherRequest, TeacherProfile
from app.schemas.student_schema import Students
from app.schemas.teacher_scherma import Teachers
from app.schemas.common import Subjects, MonthlyPerformanceTracker, UserRoles, Roles
from app.schemas.fee_schema import FeeTypeConfigurations, Installments
from app.exceptions.adminExceptions import *

class StudentUtilities:
    def __init__(self, repo:AdminRepository, security:Security) -> None:
        self.repo = repo
        self.security = security

        self.fee_types = {
            "one-time": "FEE01",
            "two-time": "FEE02",
            "four-time": "FEE04"
        }

    def get_fee_id(self, payment_type:str) -> str:
        return self.fee_types[payment_type]

    def get_coaching_mode_id(self, mode:str) -> ObjectId:
        coching_mode_config = self.repo.get_coaching_modes(mode_type=mode)
        return coching_mode_config["_id"]

    def save_student(self, studentProfile:StudentProfile, student_objID:ObjectId, coaching_mode:str, fee_typeID:str) -> ObjectId:
        studentDB = Students(
            **studentProfile.model_dump(exclude={"coaching_mode", "fee_type"}),
            id=student_objID,
            coaching_modeID=coaching_mode,
            fee_typeID=fee_typeID
        )
        student_id = self.repo.save_student_profile(student=studentDB)
        if student_id is None:
            raise FailedToCreateNewStudent("Failed to create new student")
        return student_id

    def map_student_subject(self, student_objID:ObjectId, subject_objIDs:List[ObjectId]):
        inserted_ids = self.repo.add_mapped_student_subject(student_objID=student_objID, subject_objIDs=subject_objIDs)
        if not inserted_ids:
            raise FailedToMapStudentSubjects("Failed to map student subjects")
        return inserted_ids

    def map_student_monthly_performance_tracker(self, student_objID:ObjectId, grade:int, subject_objIDs:List[ObjectId], year_batch:int):
        trackers = [
            MonthlyPerformanceTracker(studentID=student_objID, grade=grade, subjectID=subject_objID, year_batch=year_batch)
            for subject_objID in subject_objIDs
        ]
        inserted_ids = self.repo.add_mapped_student_monthly_performance_tracker(performance_trackers=trackers)
        if not inserted_ids:
            raise FailedToAddPerformanceTracker("Failed to map student performance tracker")
        return inserted_ids

    def add_installments(self, student_objID:ObjectId, student_installments:List[ClientSentInstallments], fee_typeID:str):
        fee_configurations = self.repo.get_fee_type_configurations()
        if not fee_configurations:
            raise FailedToAddInstallments("Failed to fetch fee configurations")

        num_of_installments = fee_configurations["types"][fee_typeID]["installments"]
        installments = []
        for installment in student_installments:
            if installment.installment_number > num_of_installments:
                raise FailedToAddInstallments("Invalid installment number index")
            if installment.total_installment_amount_to_pay < 0:
                raise FailedToAddInstallments("Installment amount cannot be negative")
            if installment.payment_window.start_date > installment.payment_window.end_date:
                raise FailedToAddInstallments("Start date cannot be greater than end date")

            installments.append(
                Installments(
                    studentID=student_objID,
                    installment_number=installment.installment_number,
                    total_installment_amount_to_pay=installment.total_installment_amount_to_pay,
                    payment_window=installment.payment_window,
                    payment_status=installment.payment_status
                )
            )

        installments_objIDs = self.repo.add_installments(installments=installments)
        if not installments_objIDs:
            raise FailedToAddInstallments("Failed to add installments, Database Error")
        return installments_objIDs
  
    def get_subjects_by_grade(self, grade:int, preferred_subjects:List[str]) -> List  [ObjectId]:    
        subjects = self.repo.get_preferred_subjects(grade_subjects={grade: preferred_subjects})

        if not subjects:
            raise FailedToGetPreferredSubjects("Failed to get preferred subjects for teacher")
        return [subject["_id"] for subject in subjects]


class TeacherUtilities:
    def __init__(self, repo:AdminRepository, security:Security) -> None:
        self.repo = repo
        self.security = security

    def add_teacher_role(self, teacher_objID:ObjectId):
        # Add New Teacher Role
        user_role = UserRoles(
            id=teacher_objID,
            role=Roles.TEACHER
        )
        _ = self.repo.create_new_roles(user=user_role)

        if _ is None:
            raise FailedToAddTeacherRole("Failed to add teacher role")
    
    def create_teacher_profile(self, teacher:TeacherProfile, teacher_objID:ObjectId):
        teacherDB = Teachers(
            **teacher.model_dump(),
            id=teacher_objID
        )
        teacher_id = self.repo.save_teacher_profile(teacher=teacherDB)
        if teacher_id is None:
            raise FailedToCreateNewTeacherProfile("Failed to create new teacher profile")
        return teacher_id

    def map_teacher_subject(self, teacher_objID:ObjectId, subject_objIDs:List[ObjectId]):
        inserted_ids = self.repo.map_teacher_subject(teacher_objID=teacher_objID, subject_objIDs=subject_objIDs)
        if not inserted_ids:
            raise FailedToMapTeacherSubjects("Failed to map teacher subjects")
        return inserted_ids

    def get_subjects_by_grade(self, grade_subjects:Dict[int, List[str]]):
        subjects = self.repo.get_preferred_subjects(grade_subjects=grade_subjects)

        if not subjects:
            raise FailedToGetPreferredSubjects("Failed to get preferred subjects for teacher")
        return [subject["_id"] for subject in subjects]

# class AdminService:
#     def __init__(self, AuthRepository:AdminRepository, security:Security, logger:Logger) -> None:
#         self.logger = logger
#         self.repo = AuthRepository
#         self.security = security

#         self.fee_types = {
#             "one-time":"FEE01",
#             "two-time":"FEE02",
#             "four-time":"FEE04"
#         }

#     def add_student(self, student:AddNewStudentRequest) -> Union[JSONResponse, HTTPException]:
        
#         try:
#             # Add student Credentials to Auth Table and get the user ObjectID
#             student_objID = self.add_new_user_auth(user_id=student.userID, user_password=student.userPassword, is_active=True)

#             # Fetch Respective Fee Type ID
#             fee_typeID:str = self.get_fee_id(payment_type=student.studentProfile.fee_type)

#             # Fetch Respective Coaching Mode ID
#             coaching_modeID:ObjectId = self.get_coaching_mode_id(mode=student.studentProfile.coaching_mode)

#             # Store student profile in the Students Table with the user ObjectID
#             _ = self.save_student(studentProfile=student.studentProfile, student_objID=student_objID, coaching_mode=coaching_modeID, fee_typeID=fee_typeID)

#             # Fetch Respective Subjects ID
#             student_preferred_subjects:List[ObjectId] = self.get_subjects_by_grade(grade=student.studentProfile.grade, preferred_subjects=student.selectedSubjects)

#             # Map Student with their respective subjects
#             _ = self.map_student_subject(student_objID=student_objID, subject_objIDs=student_preferred_subjects)

#             # Add student doc to monthly performance tracker with empty attendance and remarks fields
#             _ = self.map_student_monthly_performance_tracker(
#                 student_objID=student_objID,
#                 grade=student.studentProfile.grade,
#                 subject_objIDs=student_preferred_subjects,
#                 year_batch=student.studentProfile.date_joined.year
#             )

#             # Create Installments records in Fee Tracker with ammt paid=0 and payment_status=false
#             _ = self.add_installments(
#                 student_objID=student_objID,
#                 student_installments=student.installments,
#                 fee_typeID=fee_typeID
#             )

#             return JSONResponse(
#                 status_code=status.HTTP_201_CREATED,
#                 content={
#                     "message":f"Successfully created new student.\nUserID: {student.userID} is active now.",
#                     "student_user_id":student.userID,
#                     "student_password":student.userPassword
#                 }
#             )

        
#         except FailedToCreateNewUserAuth as e:
#             self.logger.error(e)
#             raise HTTPException(
#                 status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#                 detail=str(e)
#             )

#         except FailedToCreateNewStudent as e:
#             self.logger.error(e)
#             raise HTTPException(
#                 status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#                 detail=str(e)
#             )
        
#         except InvalidGrade as e:
#             self.logger.error(e)
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=str(e)
#             )

#         except FailedToMapStudentSubjects as e:
#             self.logger.error(e)
#             raise HTTPException(
#                 status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#                 detail=str(e)
#             )
        
#         except FailedToAddPerformanceTracker as e:
#             self.logger.error(e)
#             raise HTTPException(
#                 status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#                 detail=str(e)
#             )
    
#         except FailedToAddInstallments as e:
#             self.logger.error(e)
#             raise HTTPException(
#                 status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#                 detail=str(e)
#             )

#     def add_new_user_auth(self, user_id:str, user_password:str, is_active:bool=True):
#         hashed_password = self.security.hash_password(user_password)
#         timestamp = get_utc_timestamp()

#         user:Auth = Auth(
#             userID=user_id,
#             hashed_pswd=hashed_password,
#             is_active=is_active,
#             last_login=timestamp
#         )
#         user_objectID = self.repo.create_new_user_auth(user=user)

#         if user_objectID is None:
#             raise FailedToCreateNewUserAuth("Failed to create new user auth")
#         return user_objectID
    
#     def get_fee_id(self, payment_type:str):
#         return self.fee_types[payment_type]
    
#     def get_coaching_mode_id(self, mode:str):
#         coching_mode_config = self.repo.get_coaching_modes(mode_type=mode)
#         modeID:ObjectId = coching_mode_config["_id"]
#         return modeID
    
#     def save_student(self, studentProfile:StudentProfile, student_objID:ObjectId, coaching_mode:str, fee_typeID:str):
#         studentDB = Students(
#                 **studentProfile.model_dump(exclude={"coaching_mode", "fee_type"}),
#                 id=student_objID,
#                 coaching_modeID=coaching_mode,
#                 fee_typeID=fee_typeID
#             )
#         student_objID = self.repo.save_student(student=studentDB)

#         if student_objID is None:
#             raise FailedToCreateNewStudent("Failed to create new student")
#         return student_objID
    
#     def get_subjects_by_grade(self, grade:int, preferred_subjects:List[str]) -> List[ObjectId]:
#         available_subjects:List[Subjects] = self.repo.get_subjects_by_grade(grade=grade)

#         if available_subjects is None:
#             raise InvalidGrade("Invalid Class Grade!, Failed to fetch subjects by grade")
        
#         subjects:List[str] = [subject["_id"] for subject in available_subjects if subject["name"] in preferred_subjects]
#         return subjects
    
#     def map_student_subject(self, student_objID:ObjectId, subject_objIDs:List[ObjectId]):
#         inserted_ids = self.repo.add_mapped_student_subject(student_objID=student_objID, subject_objIDs=subject_objIDs)
        
#         if inserted_ids is None:
#             raise FailedToMapStudentSubjects("Failed to map student subjects")
#         return inserted_ids
    
#     def map_student_monthly_performance_tracker(self, student_objID:ObjectId, grade:int, subject_objIDs:List[ObjectId], year_batch:int):

#         student_monthly_performance_trackers = [
#             MonthlyPerformanceTracker(
#                 studentID=student_objID,
#                 grade=grade,
#                 subjectID=subject_objID,
#                 year_batch=year_batch
#             ) for subject_objID in subject_objIDs
#         ]

#         inserted_ids = self.repo.add_mapped_student_monthly_performance_tracker(performance_trackers=student_monthly_performance_trackers)

#         if inserted_ids is None:
#             raise FailedToAddPerformanceTracker("Failed to map student subjects")
#         return inserted_ids
    
#     def add_installments(self, student_objID:ObjectId, student_installments:List[ClientSentInstallments], fee_typeID:str):
#         fee_configurations:FeeTypeConfigurations = self.repo.get_fee_type_configurations()

#         if fee_configurations is None:
#             raise FailedToAddInstallments("Failed to fetch fee configurations")
        
#         number_of_installments:int = fee_configurations["types"][fee_typeID]["installments"]

#         installments = []
#         for installment in student_installments:
#             if installment.installment_number > number_of_installments:
#                 raise FailedToAddInstallments("Failed to add installments, invalid installment number index")
            
#             if installment.total_installment_amount_to_pay < 0:
#                 raise FailedToAddInstallments("Failed to add installments, installment amount cannot be negative")
            
#             if installment.payment_window.start_date > installment.payment_window.end_date:
#                 raise FailedToAddInstallments("Failed to add installments, start date cannot be greater than end date")
            
#             installments.append(
#                 Installments(
#                     studentID=student_objID,
#                     installment_number=installment.installment_number,
#                     total_installment_amount_to_pay=installment.total_installment_amount_to_pay,
#                     payment_window=installment.payment_window,
#                     payment_status=installment.payment_status
#                 )
#             )
        
#         installments_objIDs = self.repo.add_installments(installments=installments)

#         if installments_objIDs is None:
#             raise FailedToAddInstallments("Failed to add installments, Database Error")
#         return installments_objIDs





class AdminService:
    def __init__(self, AuthRepository:AdminRepository, security:Security, logger:Logger) -> None:
        self.logger = logger
        self.repo = AuthRepository
        self.security = security
        self.student_utils = StudentUtilities(self.repo, self.security)
        self.teacher_utils = TeacherUtilities(self.repo, self.security)

    def add_student(self, student:AddNewStudentRequest) -> Union[JSONResponse, HTTPException]:
        try:
            student_objID = self.add_new_user_auth(
                user_id=student.userID,
                user_password=student.userPassword,
                is_active=True
            )

            fee_typeID = self.student_utils.get_fee_id(student.studentProfile.fee_type)
            coaching_modeID = self.student_utils.get_coaching_mode_id(student.studentProfile.coaching_mode)

            self.student_utils.save_student(
                studentProfile=student.studentProfile,
                student_objID=student_objID,
                coaching_mode=coaching_modeID,
                fee_typeID=fee_typeID
            )

            subjects_ids = self.student_utils.get_subjects_by_grade(
                grade=student.studentProfile.grade,
                preferred_subjects=student.selectedSubjects
            )

            self.student_utils.map_student_subject(student_objID=student_objID, subject_objIDs=subjects_ids)

            self.student_utils.map_student_monthly_performance_tracker(
                student_objID=student_objID,
                grade=student.studentProfile.grade,
                subject_objIDs=subjects_ids,
                year_batch=student.studentProfile.date_joined.year
            )

            self.student_utils.add_installments(
                student_objID=student_objID,
                student_installments=student.installments,
                fee_typeID=fee_typeID
            )

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "message": f"Successfully created new student. UserID: {student.userID} is active now.",
                    "student_user_id": student.userID,
                    "student_password": student.userPassword,
                }
            )

        except FailedToCreateNewUserAuth as e:
            self.logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )

        except FailedToCreateNewStudent as e:
            self.logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )
        
        except InvalidGrade as e:
            self.logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        except FailedToMapStudentSubjects as e:
            self.logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )
        
        except FailedToAddPerformanceTracker as e:
            self.logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )
    
        except FailedToAddInstallments as e:
            self.logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )

    def add_teacher(self, teacher:AddNewTeacherRequest) -> Union[JSONResponse, HTTPException]:

        try:
            # Create New Teacher Auth
            teacher_objID = self.add_new_user_auth(
                user_id=teacher.userID,
                user_password=teacher.userPassword,
                is_active=True
            )

            self.teacher_utils.add_teacher_role(teacher_objID=teacher_objID)
            self.teacher_utils.create_teacher_profile(
                teacher=teacher.teacherProfile,
                teacher_objID=teacher_objID
            )
            subject_ids = self.teacher_utils.get_subjects_by_grade(teacher.teachingSubjects)
            self.teacher_utils.map_teacher_subject(teacher_objID=teacher_objID, subject_objIDs=subject_ids)

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "message": f"Successfully created new teacher. UserID: {teacher.userID} is active now.",
                    "teacher_user_id": teacher.userID,
                    "teacher_password": teacher.userPassword,
                }
            )

        except FailedToCreateNewUserAuth as e:
            self.logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )

        except FailedToCreateNewTeacherProfile as e:
            self.logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )

        except FailedToMapTeacherSubjects as e:
            self.logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )
    
    def add_new_user_auth(self, user_id:str, user_password:str, is_active:bool=True) -> ObjectId:
        hashed_password = self.security.hash_password(user_password)
        timestamp = get_utc_timestamp()

        user = Auth(
            userID=user_id,
            hashed_pswd=hashed_password,
            is_active=is_active,
            last_login=timestamp
        )
        user_objectID = self.repo.create_new_user_auth(user=user)
        if user_objectID is None:
            raise FailedToCreateNewUserAuth("Failed to create new user auth")
        return user_objectID
    