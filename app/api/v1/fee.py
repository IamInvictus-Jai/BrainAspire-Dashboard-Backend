from fastapi import APIRouter
from dependency_injector.wiring import inject
from app.utils.dependencyManager import Dependencies
from app.schemas.admin_client_req_res import CalculateCourseFeeRequest, CalculateCourseFeeResponse

fee_router = APIRouter(
    prefix="/v1/fee",
    tags=["Fee"],
    responses={404: {"description": "Not found"}},
)


@fee_router.get("/calculate-course-fee", response_model=CalculateCourseFeeResponse)
@inject
async def get_fee_type_configurations(studentDetails:CalculateCourseFeeRequest, fees:Dependencies.PaymentService):
    return fees.calculate_course_fee(studentDetails=studentDetails)