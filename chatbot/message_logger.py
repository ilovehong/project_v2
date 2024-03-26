import psycopg2
from psycopg2 import sql

class MessageLogger:
    def __init__(self, db_config):
        self.db_config = db_config
        self.connect()
        self.setup_database()  # Ensure the table exists on initialization

    def connect(self):
        """Establish a connection to the PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cur = self.conn.cursor()
            print("Database connection established.")
        except Exception as e:
            print(f"Unable to connect to the database: {e}")

    def setup_database(self):
        """Check if the required table exists, and create it if not."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS message_logs (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            self.cur.execute(create_table_query)
            self.conn.commit()
            print("Database table checked/created successfully.")
        except Exception as e:
            print(f"Failed to create table: {e}")
            self.conn.rollback()

    def log_message(self, user_id, message):
        """Log a user's message to the PostgreSQL database."""
        try:
            query = sql.SQL("INSERT INTO message_logs (user_id, message) VALUES (%s, %s)")
            self.cur.execute(query, (user_id, message))
            self.conn.commit()
        except Exception as e:
            print(f"Failed to insert log into database: {e}")
            self.conn.rollback()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.cur.close()
            self.conn.close()
            print("Database connection closed.")
