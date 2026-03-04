from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from config.config import ARGON2_SALT


class Password:
    
    def __init__(self):
        self.ph = PasswordHasher()
    
    def hash(self, password: str) -> str:
        return self.ph.hash(password, salt=ARGON2_SALT.encode("utf-8"))
    
    def verify(self, password: str, hash: str) -> bool:
        try:
            return self.ph.verify(hash, password)
        except VerifyMismatchError:
            return False



if __name__ == "__main__":
    password = Password()
    print(password.hash("123123"))