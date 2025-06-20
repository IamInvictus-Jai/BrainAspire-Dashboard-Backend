from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Union

class Settings(BaseSettings):
    # App info
    PROJECT_NAME: str = "BrainAspire Dashboard"
    VERSION: str = "0.1.1"

    # JWT Settings
    jwt_secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = Field(..., env="ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # MongoDB Settings
    mongodb_user: str = Field(..., env="MONGODB_USER")
    mongodb_password: str = Field(..., env="MONGODB_PASSWORD")
    mongodb_cluster: str = Field(..., env="MONGODB_CLUSTER")

    # Email Settings
    email: str = Field(..., env="EMAIL")
    email_to: str = Field(..., env="EMAIL_TO")
    google_app_password: str = Field(..., env="GOOGLE_APP_PASSWORD")
    email_smtp_server: str = Field(..., env="EMAIL_SMTP_SERVER")
    server_port: int = Field(..., env="SERVER_PORT")

    # CORS Settings
    allowed_origins: Union[str, List[str]] = Field(
        default=["*"],
        env="ALLOWED_ORIGINS",
        description="Allowed CORS origins as string or list"
    )
    allowed_methods: Union[str, List[str]] = Field(
        default=["*"],
        env="ALLOWED_METHODS",
        description="Allowed HTTP methods as string or list"
    )
    allowed_headers: Union[str, List[str]] = Field(
        default=["*"],
        env="ALLOWED_HEADERS",
        description="Allowed headers as string or list"
    )
    @field_validator("allowed_origins", "allowed_methods", "allowed_headers")
    @classmethod
    def parse_cors_settings(cls, v) -> List[str]:
        if isinstance(v, str):
            # Handle comma-separated string
            if ',' in v:
                return [x.strip() for x in v.split(',') if x.strip()]
            # Handle single string
            return [v.strip()]
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        return ["*"]  # Default fallback


    # Log directory
    LOGS_DIR: str = "app/logs"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Usage example:
if __name__ == "__main__":
    try:
        settings = get_settings()
        print("JWT Secret Key:", settings.jwt_secret_key)
        print("Allowed Origins:", settings.allowed_origins)
        print("Server Port:", settings.server_port)
    except ValidationError as e:
        print("Settings validation error:", e)
    except Exception as e:
        print("Error loading settings:", e)