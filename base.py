""" Small file, that exports a base class for SqlAlchemy things"""
from sqlalchemy.ext.declarative import declarative_base

# Includes a base super constructor
Base = declarative_base()
