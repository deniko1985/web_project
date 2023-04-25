from passlib.context import CryptContext

SECRET_KEY = '06e1d84c3b43c04563a416e68cf2eab6ba36b66d82e7fd49124bd96dae18abdc'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_WEEKS = 2

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
