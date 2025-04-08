import os
import psycopg2

# Get the database URL from environment variables
db_url = os.environ.get('DATABASE_URL')
print(f"Database URL: {db_url}")

try:
    # Attempt to connect to the database
    conn = psycopg2.connect(db_url)
    
    # Create a cursor
    cur = conn.cursor()
    
    # Execute a simple query
    cur.execute("SELECT current_database();")
    
    # Fetch the result
    result = cur.fetchone()
    
    print(f"Successfully connected to database: {result[0]}")
    
    # Close cursor and connection
    cur.close()
    conn.close()
    
    print("Connection test completed successfully!")
    
except Exception as e:
    print(f"Error connecting to database: {e}")