import bcrypt
import psycopg2
import os

# Database Connection Utility
def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

# Password Hashing
def hash_password(password: str) -> str:
    # Generates a salt and hashes the password
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Password Verification
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Database Action: Register
def register_user(username, email, password):
    hashed = hash_password(password)
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, hashed)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Registration Error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

# Database Action: Login
def authenticate_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    if user and verify_password(password, user[1]):
        return user[0] # Returns the user_id
    return None
def get_user_history(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id as mission_id, user_query, created_at 
        FROM research_missions 
        WHERE user_id = %s 
        ORDER BY created_at DESC LIMIT 10
    """, (user_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def load_past_research(mission_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT final_report FROM research_missions WHERE id = %s", (mission_id,))
    report = cur.fetchone()
    cur.close()
    conn.close()
    return report[0] if report else "Report not found."
def save_final_report_to_db(user_id, mission_id, user_query, report_text):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # We use an UPSERT (Update on Conflict) so it works for 
        # both new records and existing ones.
        cur.execute("""
            INSERT INTO research_missions (id, user_id, user_query, final_report, status)
            VALUES (%s, %s, %s, %s, 'completed')
            ON CONFLICT (id) DO UPDATE 
            SET final_report = EXCLUDED.final_report, 
                status = 'completed';
        """, (mission_id, user_id, user_query, report_text))
        conn.commit()
    except Exception as e:
        print(f"❌ Database Error: {e}")
    finally:
        cur.close()
        conn.close()