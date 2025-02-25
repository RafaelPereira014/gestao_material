import csv
import pymysql

def read_csv_and_write_to_db(csv_file_path, db_config, table_name):
    try:
        # Step 1: Analyze the CSV file
        with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            header = next(csv_reader)  # Read the header row
            
            # Print header for debugging
            print(f"CSV Header: {header}")
            
            # Map CSV columns to database columns for monitores
            csv_to_db_mapping = {
                "coluna1": "atribuido_a",     # Maps to 'atribuido_a'
                "coluna2": "marca_modelo",    # Maps to 'marca_modelo'
                "coluna3": "cod_nit"    # Maps to 'polegadas'
                
                
    
            }
            
            # Extract database columns based on the CSV header
            db_columns = [csv_to_db_mapping.get(col, None) for col in header]
            
            # Check for unmapped columns
            unmapped_columns = [col for col in header if col not in csv_to_db_mapping]
            if unmapped_columns:
                print(f"Warning: The following columns are not mapped to the database: {unmapped_columns}")
            
            # Remove None values from db_columns
            db_columns = [col for col in db_columns if col]
            
            if not db_columns:
                raise ValueError("No CSV columns are mapped to database columns. Check the mapping.")
            
            print(f"Mapped database columns: {db_columns}")
            
            # Prepare rows for insertion
            rows = []
            for row_number, row in enumerate(csv_reader, start=1):
                if len(row) != len(header):
                    print(f"Skipping row {row_number} due to column mismatch: {row}")
                    continue
                sanitized_row = [value.strip() if value.strip() else " - " for value in row]
                rows.append(sanitized_row)
        
        print(f"Total rows to insert: {len(rows)}")
        
        # Step 2: Prepare the database insertion
        connection = pymysql.connect(**db_config)
        print("Connected to the database")
        
        with connection.cursor() as cursor:
            # Prepare the SQL query dynamically based on the mapped columns
            query = f"""
                INSERT INTO {table_name} ({", ".join(db_columns)}, estado) 
                VALUES ({", ".join(["%s"] * len(db_columns))}, 'Em uso')
            """
            print(f"SQL Query: {query}")
            
            # Insert each sanitized row
            for row in rows:
                try:
                    # Match the number of columns to the query
                    cursor.execute(query, row[:len(db_columns)])
                except Exception as e:
                    print(f"Error inserting row {row}: {e}")
            
            # Commit the transaction
            connection.commit()
            print("Data inserted successfully")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the database connection
        if 'connection' in locals() and connection:
            connection.close()
            print("Database connection closed")

# Configuration and execution
if __name__ == "__main__":
    # CSV file path
    csv_file_path = "static/files/cameras.csv"

    # Database configuration
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "passroot",
        "database": "material_management"
    }

    # Table name
    table_name = "cameras"

    # Execute the function
    read_csv_and_write_to_db(csv_file_path, db_config, table_name)