import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import streamlit as st
from bson.objectid import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection string
MONGO_URI = os.getenv("mongodb+srv://migdracios:tun852469@<cluster-url>/test?retryWrites=true&w=majority")

@st.cache_resource
def init_connection():
    # Create a new client and connect to the server
    return MongoClient(MONGO_URI, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        st.success("Successfully connected to MongoDB!")
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")
    return client

def get_database():
    client = init_connection()
    return client.get_database()

def load_team_members():
    db = get_database()
    return list(db.team_members.find().sort("name", 1))

def load_projects():
    db = get_database()
    return list(db.projects.find())

def save_project(project):
    db = get_database()
    result = db.projects.insert_one(project)
    return result.inserted_id

def update_project(project):
    db = get_database()
    project_id = project.pop('_id', None)
    if project_id:
        db.projects.update_one({"_id": ObjectId(project_id)}, {"$set": project})

def delete_project(project_id):
    db = get_database()
    db.projects.delete_one({"_id": ObjectId(project_id)})

def load_tasks(project_id):
    db = get_database()
    return list(db.tasks.find({"project_id": ObjectId(project_id)}))

def save_task(task):
    db = get_database()
    result = db.tasks.insert_one(task)
    return result.inserted_id

def update_task(task):
    db = get_database()
    task_id = task.pop('_id', None)
    if task_id:
        db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": task})

def delete_task(task_id):
    db = get_database()
    db.tasks.delete_one({"_id": ObjectId(task_id)})