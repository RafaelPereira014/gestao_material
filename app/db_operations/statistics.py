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
        
def get_equipment_name(category, equipment_id):
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        
        # Check which columns exist in the table
        cursor.execute(f"SHOW COLUMNS FROM {category}")
        columns = [row[0] for row in cursor.fetchall()]
        
        # Determine the column to use
        if "marca_modelo" in columns:
            column_to_select = "marca_modelo"
        elif "nome_ad" in columns:
            column_to_select = "nome_ad"
        else:
            raise ValueError(f"No relevant columns found in table {category}.")
        
        # Build and execute the query
        query = f"""
            SELECT {column_to_select} AS equipment_name
            FROM {category}
            WHERE id = %s
        """
        cursor.execute(query, (equipment_id,))
        result = cursor.fetchone()
        
        return result[0] if result else None
    finally:
        cursor.close()
        connection.close()
