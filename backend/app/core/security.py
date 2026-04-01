from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer


password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(password, hashed):
    return password_hash.verify(password, hashed)

def get_password_hash(password):
    return password_hash.hash(password)
