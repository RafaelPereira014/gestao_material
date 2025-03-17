import csv
import pymysql
from config import DB_CONFIG



def connect_to_database():
    """Establishes a connection to the MySQL database."""
    return pymysql.connect(**DB_CONFIG)

def update_names_from_csv(csv_file_path, table_name, column_name):
    
    try:
        # Establish database connection
        connection = connect_to_database()
        cursor = connection.cursor()

        # Read the CSV file
        with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file, delimiter=';')  
            
            # Update database rows for each valid CSV entry
            for row in reader:
                if len(row) != 2:
                    print(f"Skipping invalid row: {row}")
                    continue  # Skip rows that don't have exactly two values
                
                nome1, nome2 = row  # Extract `nome1` and `nome2` from each row
                cursor.execute(
                    f"""
                    UPDATE {table_name}
                    SET {column_name} = %s
                    WHERE nome = %s
                    """,
                    (nome2, nome1)
                )

        # Commit the changes to the database
        connection.commit()
        return "Names updated successfully!"
    except Exception as e:
        # Rollback in case of an error
        if 'connection' in locals():
            connection.rollback()
        return f"Error occurred: {e}"
    finally:
        # Close the connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


if __name__ == "__main__":
    # Configuration
    csv_path = "static/files/utilizadores.csv"  # Replace with the actual path to your CSV file
    table = "users_a_atribuir"          # Replace with your table name
    column = "nome"   # Replace with the column name to update

    # Execute the function
    result = update_names_from_csv(csv_path, table, column)
    print(result)