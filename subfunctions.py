import os, datetime, users

def check_username(name):
    if len(name) < 2 or len(name) > 35:
        return "Tunnuksen tulee sisältää 2-35 merkkiä"  
    if users.check_exist(name) > 0:
        return "Tunnus on jo käytössä, valitse toinen tunnus"
    return "ok"

def check_name(name, user_id):
    if len(name) < 2 or len(name) > 35:
        return "Nimen tulee sisältää 2-35 merkkiä"  
    if users.check_exist(name) > 0:
        if name != users.get_username(user_id):
            return "Nimi on jo käytössä, valitse toinen nimi"
    return "ok"

def check_password(password1, password2):
    if password1 != password2:
        return "Salasanoissa oli eroa"
    if password1 == "":
        return "Salasana oli tyhjä"
    return "ok"

def check_times_one(times_of_own_entries_for_day, new_time):
    #for entry_time in times_of_own_entries_for_day:
    #    if entry_time[1] >= new_time[0] and entry_time[0] >= new_time[1]:
     #       return "ok"
     #   if not (new_time[0] >= entry_time[1] or new_time[1] <= entry_time[0]):
     #       return "Aika menee päällekkäin päivän toisen ilmoittautumisesi kanssa, peru ilmoittautumisia tarvittaessa"
   # return "ok"
    if new_time[1] <= times_of_own_entries_for_day[0][0] or new_time[0] >= times_of_own_entries_for_day[-1][1]:
        return "ok"
    for i in range(1, len(times_of_own_entries_for_day)):
        print("--",times_of_own_entries_for_day[i])
        if (times_of_own_entries_for_day[i-1][1] <= new_time[0] and new_time[1] <= times_of_own_entries_for_day[i][0]):
            return "ok"
    return "Aika menee päällekkäin päivän toisen ilmoittautumisesi kanssa, peru ilmoittautumisia tarvittaessa"

def check_times_many(earlier_entry_times, new_entry_times):
    all_times = earlier_entry_times + new_entry_times
    all_times.sort()
    for times in new_entry_times:
        if times[0] >= times[1]:
            return "Ilmoittautumisia ei voinut tallentaa, ilmoittautumisen alku ja loppuaika oli sama tai alkuaika oli suurempi kuin loppuaika"
    for i in range(1, len(all_times)):
        if all_times[i-1][1] > all_times[i][0]:
            return "Aika menee päällekkäin päivän toisen ilmoittautumisesi kanssa, peru ilmoittautumisia tarvittaessa"
    return "ok"

def get_new_entry_times(start_times, finish_times):
    new_entry_times = []
    for i in range(len(start_times)):
        if start_times[i] == "" and finish_times[i] == "":
            continue
        if (start_times[i] == "" and finish_times[i] != "") or (start_times[i] != "" and finish_times[i] == ""):
            return []
        new_entry_times.append((datetime.datetime.strptime(start_times[i], "%H:%M").time(), datetime.datetime.strptime(finish_times[i], "%H:%M").time(), i))
    return new_entry_times

def change_list_to_dict(wanted_key, all_entries):
    all_own_entries = {0:[],1:[],2:[],3:[],4:[],5:[],6:[]}
    for entry in all_entries:
        all_own_entries[entry[wanted_key]].append(entry)
    return all_own_entries

def change_days_dow_to_i_dict(days, today):
    days_i = {}
    for i in range(7):
        dow_wanted = (today + datetime.timedelta(days=i)).strftime("%w")
        days_i[i] = days[int(dow_wanted)]
    return days_i

def add_weekday(friends_plans:list) -> list:
    days = {0:"SU", 1:"MA", 2:"TI", 3:"KE", 4:"TO", 5:"PE", 6:"LA"}
    friends_plans_w = []
    for entry in friends_plans:
        entry = list(entry)
        entry[4] = days[entry[4]]
        friends_plans_w.append(entry)
    return friends_plans_w

def match_day_to_dict_week7i(dow) -> int:
    dow_now = datetime.date.today().weekday() + 1
    if dow < dow_now:
        day = 7 - (dow_now - dow)
    else:
        day = dow - dow_now
    return day
