from sqlalchemy import create_engine
from secret_keys import Settings
from sqlalchemy.orm import sessionmaker

settings = Settings()

engine = create_engine(settings.POSTGRES_URL) # creates a connection to the database

SessionLocal = sessionmaker(
  autocommit=False, # prevents the auto commit of the transactions
  autoflush=False, # prevents the auto flush of the transactions
  bind=engine
)

def get_db():
    db = SessionLocal()
    '''
    the reason why we make get_db a function instead of calling it directly
    because it enables us to close the connection

    so whenever it is callse it yields the db that means it will 
    go to the function which called the get_db() and when that finishes the 

    "finally" inside get_db() will be executed
    '''
    try:
        yield db
    finally:
        db.close()
