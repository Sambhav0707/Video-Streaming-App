from sqlalchemy.ext.declarative import declarative_base

# declarative_base() returns a base class for declarative models.
# Any class that inherits from this 'Base' will be automatically mapped to a database table.
# It maintains a registry of all your model classes and their corresponding tables.
Base = declarative_base()
