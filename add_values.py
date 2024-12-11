import csv
import pymysql

def read_csv_and_write_to_db(csv_file_path, db_config, table_name):
    try:
        # Connect to the database
        connection = pymysql.connect(**db_config)
        print("Connected to the database")
        
        with connection.cursor() as cursor:
            # Open and read the CSV file
            with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=';')
                header = next(csv_reader)  # Skip the header row
                
                # Prepare the SQL query
                query = f"""
                INSERT INTO {table_name} (
                    atribuido_a, nome_ad, marca, modelo, processador, ram, 
                    disco, cod_nit, n_serie, data_aq, garantia, firma, 
                    so, office
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """
                
                # Loop through the CSV and insert each row into the database
                for row in csv_reader:
                    cursor.execute(query, row)
                
                # Commit the transaction
                connection.commit()
                print("Data inserted successfully")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the database connection
        if connection:
            connection.close()
            print("Database connection closed")

# Configuration and execution
if __name__ == "__main__":
    # CSV file path
    csv_file_path = "static/files/Computadores2.csv"

    # Database configuration
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "passroot",
        "database": "material_management"
    }

    # Table name
    table_name = "computadores"

    # Execute the function
    read_csv_and_write_to_db(csv_file_path, db_config, table_name)