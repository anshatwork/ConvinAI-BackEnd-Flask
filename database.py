from app import mongo

# Database operations can be defined here
from flask_pymongo import PyMongo
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId
from datetime import datetime

# This will be imported and initialized in __init__.py
mongo = PyMongo()

def init_db(app):
    """Initialize database connection"""
    mongo.init_app(app)
    try:
        # The ismaster command is cheap and does not require auth.
        mongo.db.command('ismaster')
        print("MongoDB connection successful")
    except ConnectionFailure:
        print("MongoDB connection failed")

def get_db():
    """Get database connection"""
    return mongo.db

# Helper functions for common database operations

def insert_one(collection, data):
    """Insert one document into a collection"""
    return get_db()[collection].insert_one(data)

def find_one(collection, query):
    """Find one document in a collection"""
    return get_db()[collection].find_one(query)

def find_many(collection, query=None, limit=0):
    """Find multiple documents in a collection"""
    return get_db()[collection].find(query).limit(limit)

def update_one(collection, query, update_data):
    """Update one document in a collection"""
    return get_db()[collection].update_one(query, {'$set': update_data})

def delete_one(collection, query):
    """Delete one document from a collection"""
    return get_db()[collection].delete_one(query)

def aggregate(collection, pipeline):
    """Perform an aggregation on a collection"""
    return get_db()[collection].aggregate(pipeline)

# Utility functions

def object_id(id_str):
    """Convert string to ObjectId"""
    return ObjectId(id_str)

def format_date(date):
    """Format date for database insertion"""
    if isinstance(date, str):
        return datetime.strptime(date, '%Y-%m-%d')
    return date

# Example of a more specific function for your application
def get_user_expenses(user_id, start_date=None, end_date=None):
    """Get expenses for a specific user within a date range"""
    query = {'user_id': object_id(user_id)}
    if start_date and end_date:
        query['date'] = {
            '$gte': format_date(start_date),
            '$lte': format_date(end_date)
        }
    return find_many('daily_expenses', query)
    