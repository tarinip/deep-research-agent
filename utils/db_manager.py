import psycopg2
import json

# Change the definition to include domain=None
def save_mission_to_db(user_query, target, template, research_brief, domain=None):
    try:
        conn = psycopg2.connect("dbname=postgres user=tarinijain host=localhost")
        cur = conn.cursor()
        
        # Make sure your SQL INSERT includes the domain column if you have one
        query = """
            INSERT INTO research_missions (user_query, target, template, research_brief, domain, status)
            VALUES (%s, %s, %s, %s, %s, 'started')
            RETURNING id;
        """
        cur.execute(query, (user_query, target, template, json.dumps(research_brief), domain))
        
        mission_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return mission_id
    except Exception as e:
        print(f"❌ DB Manager Error: {e}")
        return None