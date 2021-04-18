from db import db
from werkzeug.security import check_password_hash, generate_password_hash
import os 

def get_info():
    sql = """SELECT name, description, admin_info FROM group_info"""
    return db.session.execute(sql).fetchone()

def check_password(password_group):
    sql = """SELECT password 
                FROM group_info"""
    group_password = db.session.execute(sql).fetchone()[0]
    return check_password_hash(group_password, password_group)

def add(name, description, password):
    hash_value = generate_password_hash(password)
    sql = """INSERT INTO group_info (name, description, password, founded) 
                VALUES (:name, :description, :password, NOW()) RETURNING id"""
    result = db.session.execute(sql, {"name":name, "description":description,"password":hash_value})
    group_id = result.fetchone()[0]
    db.session.commit()
    return group_id

def set_founder(user_id):
    sql = """UPDATE group_info 
                SET founder_id=:user_id"""
    db.session.execute(sql, {"user_id":user_id})
    db.session.commit()
    return
 
def change_group_name(name:str):
    try:
        sql = """UPDATE group_info 
                    SET name=:name"""
        db.session.execute(sql, {"name":name})
        db.session.commit()
        return True
    except:
        return False

def change_group_description(description:str):
    try:
        sql = """UPDATE group_info 
                    SET description=:description"""
        db.session.execute(sql, {"description":description})
        db.session.commit()
        return True
    except:
        return False

def change_group_password(new_password:str, old_password:str):
    try:
        sql = """SELECT password FROM group_info"""
        password = db.session.execute(sql).fetchone()[0]
        if check_password_hash(password, old_password):
            sql = """UPDATE group_info 
                        SET password=:new_password"""
            db.session.execute(sql, {"new_password":new_password})
        db.session.commit()
        return True
    except:
        return False

def add_admin_message(admin_info):
    try: 
        sql = """UPDATE group_info SET admin_info=:admin_info"""
        db.session.execute(sql, {"admin_info":admin_info})
        db.session.commit()
        return True
    except:
        return False


#keskeneräinen
def get_admin_info() -> list:
    sql = """SELECT admin_info
                FROM group_info"""
    return db.session.execute(sql).fetchone()

#jos perustaa uuden ryhmän ja rekisteröityminen ei onnistu kokonaisuudessaan
#silloin ryhmä poistetaan tietokannasta tällä
def delete():
    sql = """DELETE 
             FROM group_info"""
    db.session.execute(sql)
    db.session.commit()
    return
