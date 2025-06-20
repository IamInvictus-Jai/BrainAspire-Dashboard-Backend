from fastapi import APIRouter
from dependency_injector.wiring import inject
from app.utils.dependencyManager import Dependencies

from app.schemas.admin_client_req_res import AddNewStudentRequest, AddNewTeacherRequest

admin_router = APIRouter(
    prefix="/v1/admin",
    tags=["Admin"],
    responses={404: {"description": "Not found"}},
)


@admin_router.get("/health")
async def health_check():
    return {"status": "OK"}

@admin_router.post("/student/add")
@inject
async def add_new_student(student_details:AddNewStudentRequest, admin_service:Dependencies.AdminService):
    return admin_service.add_student(student=student_details)


@admin_router.post("/teacher/add")
@inject
async def add_new_teacher(teacher_details:AddNewTeacherRequest, admin_service:Dependencies.AdminService):
    return admin_service.add_teacher(teacher=teacher_details)