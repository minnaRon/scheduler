from db import db
from flask import render_template
import os 

#keskeneräinen
def add_event(event_name:str, description:str):
    print("---tapahtuma",event_name, description)
    try:
        sql = """INSERT INTO events (name, description, min_participants, max_participants, event_level)
                    VALUES (:name, :description, 0, 100, 0) RETURNING id"""
        event_id = db.session.execute(sql, {"name":event_name, "description":description}).fetchone()[0]
        db.session.commit()  
        return event_id
    except:
        return render_template("error.html", message="Tapahtuman lisäys ei onnistunut")

def get_all_0_level_events():
    try:
        sql = """SELECT id, name, description, min_participants, max_participants
                    FROM events
                    WHERE event_level = 0
                    ORDER BY name"""
        return db.session.execute(sql).fetchall()
    except:
        return []

def get_events(user_id):
    try:
        sql = """SELECT e.id, e.name, e.description, e.min_participants, e.max_participants, e.event_level
                    FROM users u 
                    LEFT JOIN users_in_events ue ON u.id=ue.user_id
                    LEFT JOIN events e ON e.id=ue.event_id
                    WHERE u.id=:user_id
                    AND e.event_level <= ue.user_level
                    AND ue.role < 4
                    ORDER BY e.id"""
        return db.session.execute(sql, {"user_id":user_id}).fetchall()  
    except:
        return []

def delete(group_id):
    sql = """DELETE 
            FROM groups 
            WHERE id=:group_id"""
    db.session.execute(sql, {"group_id":group_id})
    db.session.commit()
    return

