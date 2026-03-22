from pydantic import BaseModel

# THis is the model or form of request structure that we
# are expecting from the user 
# and we are inheritinh from the BaseModel class 
# because pydantic automatically convert the user request into the python objects 
class SignUpRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ConfirmUserRequest(BaseModel):
    email: str
    otp: str
