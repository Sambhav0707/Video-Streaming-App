from db.base import Base
from sqlalchemy import Column, Integer, TEXT

"""
This class represents the 'users' table in our database.
By inheriting from 'Base', SQLAlchemy knows this is a database model.

NOTE:- we are not using cognito_sub  as primary key because it is not a good practice to use external provider's id as primary key
"""


class User(Base):
    # This tells SQLAlchemy the actual name of the table in the database will be 'users'.
    __tablename__ = "users"

    # These are the columns (fields) in the table:
    # id: Unique ID for each user (primary key), automatically indexed for fast lookups.
    id = Column(Integer, primary_key=True, index=True)
    # name: The user's full name. Cannot be empty (nullable=False).
    name = Column(TEXT, nullable=False)
    # email: User's email address. Must be unique and is indexed for fast searching.
    email = Column(TEXT, nullable=False, unique=True, index=True)
    # cognito_sub: A unique ID from AWS Cognito (our auth provider) to link this user to their login.
    cognito_sub = Column(TEXT, nullable=False, unique=True, index=True)
