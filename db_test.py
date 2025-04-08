#!/usr/bin/env python3
import os
import sys
import asyncio
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus

async def test_db_connection():
    load_dotenv()
    
    # Get the database URL from environment variables
    database_url = os.environ.get("DATABASE_URI", os.environ.get("DATABASE_URL"))
    if not database_url:
        print("Error: Neither DATABASE_URI nor DATABASE_URL environment variable is set.")
        return False
    
    print(f"Using database URL: {database_url}")
    
    # Ensure the URL starts with 'mongodb://' or 'mongodb+srv://'
    if not database_url.startswith(('mongodb://', 'mongodb+srv://')):
        print("Error: Invalid database URL format. Must start with 'mongodb://' or 'mongodb+srv://'")
        return False
    
    try:
        # Extract the database name from the environment variable
        database_name = os.environ.get("DATABASE_NAME", "Cluster0")
        print(f"Using database name: {database_name}")
        
        # Create a MongoDB client without the database name in URL
        # Strip the database name from the URL if present
        base_url = database_url
        if "?" in base_url:
            base_url = base_url.split("?")[0]
            if "/" in base_url:
                parts = base_url.split("/")
                if len(parts) > 3:  # mongodb+srv://user:pass@host/dbname
                    base_url = "/".join(parts[:-1])  # Remove database name
                
        # Create a new client and connect to the server
        client = MongoClient(database_url, server_api=ServerApi('1'))
        
        # Send a ping to confirm a successful connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB database!")
        
        # Get database stats using the specified database name
        db = client[database_name]
        collections = db.list_collection_names()
        
        print(f"Database: {database_name}")
        print(f"Collections: {collections}")
        
        return True
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_db_connection())