from db import db
from flask import render_template

#lisää scheman tauluun messages, sarakkeeseen entries_id, määritys ON DELETE CASCADE ja ota entry_id kyselyssä käyttöön
def add_entry_comment(user_id:int, entry_id:int, event_id:int, comment:str):
    try:
        #print("---viesti", user_id, entry_id, event_id, comment)
        sql = """INSERT INTO messages (user_id, event_id, content, sent_at)
                    VALUES (:user_id, :event_id, :content, NOW())"""
        db.session.execute(sql, {"user_id":user_id, "event_id":event_id, "content":comment})
        db.session.commit()
        return True
    except:
        return False

def add(user_id:int, content:str):
    #print("-- 2", user_id, content)
    try:
        sql = """INSERT INTO messages (user_id, content, sent_at) 
                    VALUES (:user_id, :content, NOW())"""
        db.session.execute(sql, {"user_id":user_id, "content":content})
        db.session.commit()
        return True
    except:
        return False

def get_newest(number:int, user_id:int) -> list:
    sql = """SELECT u.name, content, sent_at
                FROM messages m 
                LEFT JOIN users u ON m.user_id=u.id 
                ORDER BY m.id DESC
                LIMIT :number"""
    return db.session.execute(sql, {"number":number,"user_id":user_id}).fetchall()
