import pymysql
from config import DB_CONFIG

def connect_to_database():
    """Establishes a connection to the MySQL database."""
    return pymysql.connect(**DB_CONFIG)


def get_equipment_counts(escola_id=None):
    connection = connect_to_database()
    cursor = connection.cursor(pymysql.cursors.DictCursor)  
    try:
        # Base query
        query = "SELECT status, COUNT(*) as total FROM equipamentos"
        
        # Filter by escola_id if provided
        if escola_id:
            query += " WHERE escola_id = %s"
        
        query += " GROUP BY status;"
        
        # Execute query with or without escola_id
        if escola_id:
            cursor.execute(query, (escola_id,))
        else:
            cursor.execute(query)
        
        results = cursor.fetchall()
        
        # Convert results to a dictionary for easier use
        counts = {row['status']: row['total'] for row in results}
        return counts
    except Exception as e:
        print(f"Error fetching equipment counts: {e}")
        return {}
    finally:
        cursor.close()
        connection.close()
        

def total_equip(escola_id=None):
    connection = connect_to_database()
    cursor = connection.cursor()
    
    try: 
        # Base query
        query = "SELECT COUNT(*) FROM equipamentos"
        
        # Add filter for escola_id if provided
        if escola_id:
            query += " WHERE escola_id = %s"
        
        # Execute query with or without escola_id
        if escola_id:
            cursor.execute(query, (escola_id,))
        else:
            cursor.execute(query)
        
        # Fetch the first result (single row, single column)
        result = cursor.fetchone()
        
        # Extract the count from the tuple
        return result[0] if result else 0
    except Exception as e:
        print(f"Error fetching equipment count: {e}")
        return 0  # Return 0 in case of an error
    finally:
        cursor.close()
        connection.close()