from fastapi import HTTPException, status
from logging import Logger
from app.repositories.payment_repository import PaymentRepository
from app.schemas.admin_client_req_res import CalculateCourseFeeRequest, CalculateCourseFeeResponse
from app.schemas.fee_schema import FeeConfigurations, DiscountConfigurations
from app.exceptions.paymentExceptions import FailedToGetCourseFeeConfig, FailedToGetDiscountConfig
from app.utils.timeFormat import get_remaining_days_month_ratio
from datetime import datetime


class PaymentService:
    def __init__(self, payment_repository:PaymentRepository, logger:Logger) -> None:
        self.logger = logger
        self.repo = payment_repository

        self.course_end_dates_mapping = {
            6: datetime(2026, 2, 28),
            7: datetime(2026, 2, 28),
            8: datetime(2026, 2, 28),
            9: datetime(2026, 2, 28),
            10: datetime(2026, 2, 28),
        }

    def calculate_course_fee(self, studentDetails:CalculateCourseFeeRequest):
        try:
            course_fee = self.get_course_fee_by_class(studentDetails.grade, len(studentDetails.selectedSubjects))
            discount = self.get_discount(
                studentDetails.payment_type.value,
                studentDetails.coaching_mode.value,
                studentDetails.prev_year_results.model_dump()['percentage']
            )

            total_tuition_fee = self.calculate_tuition_fee(
                    studentDetails.date_joined,
                    self.course_end_dates_mapping[studentDetails.grade],
                    course_fee['fee']['monthly_fee']
                ) * (course_fee['subject_preference_fee']/100)
            
            total_fee = course_fee['fee']['admission_fee'] + course_fee['fee']['fixed_amt'] + total_tuition_fee
            total_dicount = discount['payment_type_discount'] + discount['coaching_mode_discount'] + discount['scholarship_discount']
            final_fee = total_fee - (total_tuition_fee * (total_dicount/100))

            response = CalculateCourseFeeResponse(
                admission_fee=course_fee['fee']['admission_fee'],
                fixed_amt=course_fee['fee']['fixed_amt'],
                tuition_fee=total_tuition_fee,
                discount={
                    "total_discount": total_dicount,
                    "discounts_applied": discount
                },
                total_fee=total_fee,
                final_fee=final_fee
            )
            return response

        except FailedToGetCourseFeeConfig as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
        except FailedToGetDiscountConfig as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def get_course_fee_by_class(self, grade:int, number_of_selected_subjects:int):
        course_fee_config:FeeConfigurations = self.repo.get_course_fees_config()

        if course_fee_config is None:
            raise FailedToGetCourseFeeConfig("Failed to get course fee config from the db")

        number_of_selected_subjects = min(len(course_fee_config['subject_preference_fee']), number_of_selected_subjects)
        return {
            "fee": course_fee_config['fees'][f'{grade}'],
            "subject_preference_fee": course_fee_config['subject_preference_fee'][f'{number_of_selected_subjects}']
        }
    
    def get_discount(self, payment_type:str, coaching_mode:str, prev_year_results:int):
        discount_config:DiscountConfigurations = self.repo.get_discount_config()
        if discount_config is None:
            raise FailedToGetDiscountConfig("Failed to get discount config from the db")  

        def calculate_scholarship(prev_year_results:int, scholarship_discount:dict[str, int]):
            if prev_year_results >= 90:
                return scholarship_discount['high']
            elif prev_year_results >= 85:
                return scholarship_discount['medium']
            elif prev_year_results >= 80:
                return scholarship_discount['low']
            else:
                return scholarship_discount['none']
             
        return {
            "payment_type_discount": discount_config['payment_type_discount'][f'{payment_type}'],
            "coaching_mode_discount": discount_config['coaching_mode_discount'][f'{coaching_mode}'],
            "scholarship_discount": calculate_scholarship(prev_year_results, discount_config['scholarship_discount'])
        }
    
    def calculate_tuition_fee(self, current_date:datetime, end_date:datetime, monthly_fee:float):
        
        # If already past end_date
        if current_date >= end_date:
            return 0.0

        total_fee = 0.0

        # 1. Pro-rata for the current partial month
        remaining_days_ratio = get_remaining_days_month_ratio(current_date)
        partial_curr_month_fee = remaining_days_ratio * monthly_fee
        total_fee += partial_curr_month_fee


        # 2. Iterate full months between next month and end_date's previous month
        next_month = (current_date.month % 12) + 1

        # current year will increment only when the current month is December
        # by this we can deciede whether the next month is in the same year or not
        next_month_year = current_date.year + (1 if next_month == 1 else 0)
        
        # 3. Get first of end_date's month
        end_year = end_date.year
        end_month = end_date.month

        # 4. Count full months between next_month_date & end_date's previous month
        full_months = (end_year - next_month_year) * 12 + (end_month - next_month)
        total_fee += full_months * monthly_fee

        # 5. Partial last month (if end_date is not the first of its month)
        days_in_end_month_ratio = get_remaining_days_month_ratio(end_date)
        partial_end_month_fee = days_in_end_month_ratio * monthly_fee
        total_fee += partial_end_month_fee

        return total_fee