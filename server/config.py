from os import environ

class Config:
    SECRET_KEY = environ.get('SECRET_KEY')
    print(SECRET_KEY)