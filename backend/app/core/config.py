from dotenv import load_dotenv

from os import getenv

load_dotenv()

SECRET = getenv("SECRET", "asdfghjkl")
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ALGORITHM = "HS256"