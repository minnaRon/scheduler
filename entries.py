from db import db
import datetime
        
def add_entry(date, user_id, event_id, time1, time2):
    sql = """INSERT INTO entries (user_id, event_id, date, start_time, finish_time) 
                VALUES (:user_id, :event_id, :date, :time1, :time2)
                RETURNING id"""
    entry_id = db.session.execute(sql, {"user_id":user_id, "event_id":event_id, "date":date, "time1":time1, "time2":time2}).fetchone()[0]
    db.session.commit()
    return entry_id

###Tämän funktiohässäkän tilalle suora vastaus tietokannasta, onkohan mahdollista? 
#Saako vastauksen jaoteltua, kun nyt tarvitaan sanakirja ja listoja HTML:ssä?
#kts.jos ehtii..

def get_week(user_id:int, week_wanted:int) -> dict:
    first_day = 0 if week_wanted == 1 else 6
    last_day = 6 if week_wanted == 1 else 13
    sql = """SELECT DISTINCT ev.id, ev.name, en.user_id,
                        COALESCE(weekly, (SELECT DATE_PART('dow', en.date))) dow,
                        en.start_time, en.finish_time, en.extra_participants, en.event_id
                FROM users_in_events ue 
                LEFT JOIN events ev ON ue.event_id=ev.id 
                LEFT JOIN entries en ON ev.id=en.event_id
                
                WHERE ((en.date BETWEEN ((SELECT CURRENT_DATE) + INTEGER ':first_day') AND ((SELECT CURRENT_DATE) + INTEGER ':last_day'))
                        OR en.weekly IS NOT NULL)
                AND ue.role < 4
                AND en.active > 0
                AND ev.event_level <= ue.user_level
                ORDER BY dow, en.event_id"""
#näyttää kaikki ryhmät, suodata; vain user_id:n valitsemat, kts. kuntoon kunhan ehtii..
    result = db.session.execute(sql, {"user_id":user_id, "first_day":first_day, "last_day":last_day}).fetchall()
    week = prepare_dict_with_days(week_wanted)
    times_and_changes = []
    dow = 0 if not result else result[0][3] 
    event_id = 0 if not result else result[0][0]
    entries_all_events = []
    for i in range(len(result)):
        if user_id == result[i][2]:
            today = datetime.datetime.today()                    #pvm, event.name, alkuaika, loppuaika, dow, day
            entries_all_events.append(((today + datetime.timedelta(days=match_day_to_dict_week7i(result[i][3]))), result[i][1], result[i][4], result[i][5], result[i][3], match_day_to_dict_week7i(result[i][3])))
        if dow != result[i][3] or event_id != result[i][0]:
            day = match_day_to_dict_week7i(dow)
            store_events = week[day][:-1] 
            store_day = week[day][-1]
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
        times_and_changes.append([result[i][4].strftime("%H:%M"), result[i][1], result[i][3], result[i][6] + 1])
        times_and_changes.append([result[i][5].strftime("%H:%M"), result[i][1], result[i][3], - (result[i][6] + 1)])
        if i == len(result) - 1:
            day = match_day_to_dict_week7i(dow)
            store_events = week[day][:-1] 
            store_day = week[day][-1]
            week[day] = [store_events[:]+calc_participants(sorted(times_and_changes))]+[store_day]
    print("---week",week)
    print("---entries_all_events", entries_all_events)
    return week, sorted(entries_all_events) 

#TÄMÄ KYSELY KESKENERÄINEN
def friends_planning(user_id):
    first_day = 7
    last_day = 13
    sql = """SELECT u.name, e.name, en.start_time, en.finish_time, 
                COALESCE(weekly, (SELECT DATE_PART('dow', en.date))) dow
                FROM users_in_events ue, friends f, entries en, users u, events e
                WHERE ue.user_id=:user_id
                AND ue.role < 4
                AND ((en.date BETWEEN ((SELECT CURRENT_DATE) + INTEGER ':first_day') AND ((SELECT CURRENT_DATE) + INTEGER ':last_day'))
                        OR en.weekly IS NOT NULL)
                AND (f.user_id1=:user_id OR f.user_id2=:user_id)
                AND f.active=1
                AND en.active > 0
                ORDER BY dow, en.event_id, u.name"""
    return db.session.execute(sql, {"user_id":user_id, "first_day":first_day, "last_day":last_day}).fetchall()

def prepare_dict_with_days(week_wanted:int) -> dict:
    today = datetime.date.today()
    weekdays = {}
    for i in range(7):
        weekdays[i] = [today + datetime.timedelta(days=i)] if week_wanted == 1 else [today + datetime.timedelta(days=i+7)]
    return weekdays

def match_day_to_dict_week7i(dow) -> int:
    dow_now = datetime.date.today().weekday() + 1
    if dow < dow_now:
        day = 7 - (dow_now - dow)
    else:
        day = dow - dow_now
    return day

def calc_participants(sorted_times_and_changes:list) -> list:
    participant_count = 0
    for i in range(len(sorted_times_and_changes)-1):
        participant_count = participant_count + sorted_times_and_changes[i][3]
        sorted_times_and_changes[i][3] = participant_count
        sorted_times_and_changes[i].append(sorted_times_and_changes[i+1][0])
    sorted_times_and_changes.pop(-1)
    times_and_changes = []
    for row in sorted_times_and_changes:
        if row[0] != row[4]:
            times_and_changes.append(row)
    return times_and_changes
