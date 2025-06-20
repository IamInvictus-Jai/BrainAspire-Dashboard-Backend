from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.exceptions.authExceptions import InvalidCredentials, TokenExpired

from app.config.settings import Settings
from logging import Logger

# from app.utils.code_profiler import log_timeit

class Security:

    def __init__(self, settings:Settings, logger:Logger):
        self.logger = logger
        self.SECRET_KEY = settings.jwt_secret_key
        self.ALGORITHM = settings.jwt_algorithm
        self.ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes

        self.pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """
        Hash password
        
        Args:
            password (str): Password to hash
            
        Returns:
            str: Hashed password
        """
        return self.pwd_context.hash(password)
    
    # @log_timeit("Verify Password")
    def verify_password(self, plain: str, hashed: str) -> bool:
        """
        Verify if password is correct
        
        Args:
            plain (str): Plain password
            hashed (str): Hashed password
            
        Returns:
            bool: True if password is correct, False otherwise
        """
        return self.pwd_context.verify(plain, hashed)

    # @log_timeit("Create Access Token")
    def create_access_token(self, user_id: str, expires_delta: timedelta = None):
        """
        Create JWT token from user data
        
        Args:
            data (dict): User data to encode in token
            expires_delta (timedelta, optional): Token expiration time. Defaults to None.
            
        Returns:
            str: JWT token
        """
        to_encode = {"sub": user_id}
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
    
    def decode_token(self, token: str) -> str:
        """
        Decode and validate JWT token
        
        Args:
            token (str): JWT token to decode
            
        Returns:
            str: Subject identifier from token
            
        Raises:
            TokenExpired: When token has expired
            InvalidCredentials: When token is invalid
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload["sub"]
        except ExpiredSignatureError:
            # self.logger.warning(f"Expired token attempt")
            raise TokenExpired("Token has expired")
        except JWTError as e:
            self.logger.error(f"Invalid token: {str(e)}")
            raise InvalidCredentials("Token is invalid")
        
    
if __name__ == "__main__":
    security = Security()
    my_password = "password"