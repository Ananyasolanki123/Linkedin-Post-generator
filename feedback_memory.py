import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class FeedbackMemory:
    def __init__(self):
        self.conn_params = {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
        }

    def get_connection(self):
        return psycopg2.connect(**self.conn_params)

    def save_feedback(self, user_email, post_content, ai_feedback, engagement_rate):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO posts_feedback_memory (user_email, post_content, ai_feedback, engagement_rate)
            VALUES (%s, %s, %s, %s)
        """, (user_email, post_content, ai_feedback, engagement_rate))
        conn.commit()
        cur.close()
        conn.close()

    def fetch_feedback(self, user_email):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT post_content, ai_feedback, engagement_rate, created_at
            FROM posts_feedback_memory
            WHERE user_email = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_email,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

# ---------------- TEST BLOCK ----------------
    if __name__ == "__main__":
        test_email = "test@example.com"
        test_post = "This is a test LinkedIn post"
        test_feedback = "Add a catchy hook at the start!"
        test_rate = 7.5

        save_feedback(test_email, test_post, test_feedback, test_rate)

        print("\n📌 Recent feedback for user:")
        for row in fetch_feedback(test_email):
            print(row)
