from db import db
import datetime

def add_entry(date, user_id, event_id, time1, time2):
    try:
        sql = """INSERT INTO entries (user_id, event_id, date, start_time, finish_time)
                VALUES (:user_id, :event_id, :date, :time1, :time2)
                RETURNING id"""
        entry_id = db.session.execute(sql, {"user_id":user_id, "event_id":event_id, "date":date, "time1":time1, "time2":time2}).fetchone()[0]
        db.session.commit()
        return entry_id
    except:
        return -1

def add_entry_with_extras(date, user_id, event_id, time1, time2, extras):
    try:
        sql = """INSERT INTO entries (user_id, event_id, date, start_time, finish_time, extra_participants)
                VALUES (:user_id, :event_id, :date, :time1, :time2, :extras)
                RETURNING id"""
        entry_id = db.session.execute(sql, {"user_id":user_id, "event_id":event_id, "date":date, "time1":time1, "time2":time2, "extras":extras}).fetchone()[0]
        db.session.commit()
        return entry_id
    except:
        return -1

def add_weekly_entry(user_id, event_id, time_start, time_end, dow):
    try:
        sql = """INSERT INTO entries (user_id, event_id, start_time, finish_time, weekly)
                VALUES (:user_id, :event_id, :time_start, :time_end, :dow)"""
        db.session.execute(sql, {"user_id":user_id, "event_id":event_id, "time_start":time_start, "time_end":time_end, "dow":dow})
        db.session.commit()
        return True
    except:
        return False

def get_weekly_entries_for_user(user_id):
    sql = """SELECT en.weekly, e.id, e.name, en.start_time, en.finish_time, en.id
                FROM entries en LEFT JOIN events e ON en.event_id=e.id
                WHERE en.user_id=:user_id
                AND en.weekly IS NOT NULL
                ORDER BY en.weekly """
    return db.session.execute(sql, {"user_id":user_id}).fetchall()

def get_times_of_own_entries_for_week(user_id, week_wanted):
    first_day = 0 if week_wanted == 1 else 6
    last_day = 6 if week_wanted == 1 else 13
    sql = """SELECT DISTINCT COALESCE(en.weekly, (SELECT DATE_PART('dow', en.date))) dow,
                        en.start_time, en.finish_time, en.event_id
                FROM entries en
                LEFT JOIN users_in_events ue ON en.user_id=ue.user_id
                WHERE ((en.date BETWEEN ((SELECT CURRENT_DATE) + INTEGER ':first_day') AND ((SELECT CURRENT_DATE) + INTEGER ':last_day'))
                        OR en.weekly IS NOT NULL)
                AND en.user_id=:user_id
                AND ue.role < 4
                AND en.active > 0
                ORDER BY dow, en.event_id"""
    return db.session.execute(sql, {"user_id":user_id, "first_day":first_day, "last_day":last_day}).fetchall()

def delete_own_entry(entry_id, user_id):
    try:
        sql = """DELETE FROM entries WHERE id=:entry_id AND user_id=:user_id"""
        db.session.execute(sql, {"entry_id":entry_id, "user_id":user_id})
        db.session.commit()
        return True
    except:
        return False

def friends_planning(user_id):
    first_day = 7
    last_day = 13
    sql = """SELECT DISTINCT u.name, e.name, en.start_time, en.finish_time,
                COALESCE(weekly, (SELECT DATE_PART('dow', en.date))) dow, en.event_id, en.date, en.weekly
                FROM users_in_events ue
                JOIN friends f ON ue.user_id=f.user_id1 OR ue.user_id=f.user_id2
                JOIN entries en ON en.user_id=f.user_id1 OR en.user_id=f.user_id2
                JOIN users u ON u.id=en.user_id
                JOIN events e ON en.event_id=e.id
                WHERE ue.user_id=:user_id
                AND ue.role < 4
                AND u.id <> :user_id
                AND ((en.date BETWEEN ((SELECT CURRENT_DATE) + INTEGER ':first_day') AND ((SELECT CURRENT_DATE) + INTEGER ':last_day'))
                        OR en.weekly IS NOT NULL)
                AND (f.user_id1=:user_id OR f.user_id2=:user_id)
                AND (f.active=1 AND (f.user_id1=:user_id OR f.user_id2=:user_id))
                AND en.active > 0
                ORDER BY dow, en.event_id, u.name"""
    return db.session.execute(sql, {"user_id":user_id, "first_day":first_day, "last_day":last_day}).fetchall()

def get_participants(user_id, date):
    sql = """SELECT e.name, u.name, en.start_time, en.finish_time, extra_participants, m.content
                FROM entries en LEFT JOIN users u ON en.user_id=u.id
                LEFT JOIN events e ON en.event_id=e.id
                LEFT JOIN messages m ON en.id=m.entries_id
                WHERE (EXTRACT (day from en.date)=EXTRACT(day from :date)
                OR en.weekly=(SELECT DATE_PART('dow', :date)))
                AND en.active=1
                AND e.id IN (SELECT event_id
                                FROM users_in_events
                                WHERE user_id=:user_id
                                AND role < 4)
                ORDER BY e.name, en.start_time"""
    return db.session.execute(sql, {"user_id":user_id, "date":date}).fetchall()

#----------------------------------------------------------------------------------------------------------------------
#-KALENTERIN "MOOTTORI"------------------------------------------------------------------------------------------------
#haetaan tietokannasta yhdellä kyselyllä kaikkien osallistumiset viikoksi eteenpäin kaikille päiville niistä tapahtumista,
#joita käyttäjä seuraa, sekä eritellään käyttäjän omat ilmoittautumiset omaksi listakseen.
#----------------------------------------------------------------------------------------------------------------------

#1/5 haetaan tiedot
def get_week(user_id:int, week_wanted:int) -> dict:
    first_day = 0 if week_wanted == 1 else 6
    last_day = 6 if week_wanted == 1 else 13
    sql = """SELECT DISTINCT ev.id, ev.name, en.user_id,
                        COALESCE(weekly, (SELECT DATE_PART('dow', en.date))) dow,
                        en.start_time, en.finish_time, en.extra_participants, en.event_id, en.id
                FROM users_in_events ue 
                LEFT JOIN events ev ON ue.event_id=ev.id 
                LEFT JOIN entries en ON ev.id=en.event_id
                WHERE ((en.date BETWEEN ((SELECT CURRENT_DATE) + INTEGER ':first_day') AND ((SELECT CURRENT_DATE) + INTEGER ':last_day'))
                        OR en.weekly IS NOT NULL)
                AND ue.role < 4
                AND en.active > 0
                AND (ev.event_level <= ue.user_level AND ue.user_id=:user_id)
                ORDER BY dow, en.event_id"""
    result = db.session.execute(sql, {"user_id":user_id, "first_day":first_day, "last_day":last_day}).fetchall()
    return add_structure(result, user_id, week_wanted)

#2/5 jaetaan tieto tietorakenteisiin
def add_structure(result, user_id, week_wanted):
    week = prepare_dict_with_days(week_wanted)
    times_and_changes = []
    dow = 0 if not result else result[0][3] 
    event_id = 0 if not result else result[0][0]
    entries_all_events = []
    for i in range(len(result)):
        if user_id == result[i][2]:
            today = datetime.datetime.today()                    #pvm, event.name, alkuaika, loppuaika, dow, day_i, event_id, en.id
            entries_all_events.append(((today + datetime.timedelta(days=match_day_to_dict_week7i(result[i][3]))), result[i][1], result[i][4], result[i][5], result[i][3], match_day_to_dict_week7i(result[i][3]), result[i][0], result[i][8]))
        if dow != result[i][3] or event_id != result[i][0]:
            day = match_day_to_dict_week7i(dow)
            store_events = week[day][:-1] 
            store_day = week[day][-1]
            if dow != result[i][3] and event_id != result[i][0]:
                week[day] = [store_events[:]+calc_participants(sorted(times_and_changes))]+[store_day]
                times_and_changes = []
                dow = result[i][3]
                event_id = result[i][0]
            elif dow != result[i][3]:
                week[day] = [store_events[:]+calc_participants(sorted(times_and_changes))]+[store_day]
                times_and_changes = []
                dow = result[i][3]
            elif event_id != result[i][0]:
                week[day] = store_events[:]+calc_participants(sorted(times_and_changes))+[store_day]
                times_and_changes = []
                event_id = result[i][0]
        times_and_changes.append([result[i][4].strftime("%H:%M"), result[i][1], result[i][3], result[i][6] + 1, result[i][0]])
        times_and_changes.append([result[i][5].strftime("%H:%M"), result[i][1], result[i][3], - (result[i][6] + 1), result[i][0]])
        if i == len(result) - 1:
            day = match_day_to_dict_week7i(dow)
            store_events = week[day][:-1]
            store_day = week[day][-1]
            week[day] = [store_events[:]+calc_participants(sorted(times_and_changes))]+[store_day]
    return week, sorted(entries_all_events) 

#3/5 alustetaan week -sanakirja
def prepare_dict_with_days(week_wanted:int) -> dict:
    today = datetime.date.today()
    weekdays = {}
    for i in range(7):
        weekdays[i] = [today + datetime.timedelta(days=i)] if week_wanted == 1 else [today + datetime.timedelta(days=i+7)]
    return weekdays

#4/5 haetaan viikonpäivää vastaava sanakirjan avain
def match_day_to_dict_week7i(dow) -> int:
    dow_now = datetime.date.today().weekday() + 1
    if dow < dow_now:
        day = 7 - (dow_now - dow)
    else:
        day = dow - dow_now
    return day

#5/5 lasketaan yksittäisen tapahtuman osallistujien määrä
def calc_participants(sorted_times_and_changes:list) -> list:
    participant_count = 0
    times_and_participants = []
    for i in range(len(sorted_times_and_changes)-1):
        participant_count = participant_count + sorted_times_and_changes[i][3]
        sorted_times_and_changes[i][3] = participant_count
        sorted_times_and_changes[i].append(sorted_times_and_changes[i+1][0])
        if sorted_times_and_changes[i][0] != sorted_times_and_changes[i][5] and sorted_times_and_changes[i][3] != 0:
            times_and_participants.append(sorted_times_and_changes[i])
    return times_and_participants

#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
