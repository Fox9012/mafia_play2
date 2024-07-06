import sqlite3
from random import shuffle


def insert_player(player_id, username):
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = f'INSERT INTO players (player_id, username) VALUES ("{player_id}", "{username}")'
    cur.execute(sql)
    con.commit()
    con.close()

def playes_amount():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = f"SELECT * FROM players"
    cur.execute(sql)
    res = cur.fetchall()
    con.close()
    return len(res)

def get_all_alive():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = f"SELECT username FROM players WHERE dead = 0"
    cur.execute(sql)
    res = cur.fetchall()
    con.close()
    names = [name[0] for name in res]
    return names
def get_mafia_usernames():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = f"SELECT username FROM players WHERE role = 'mafia'"
    cur.execute(sql)
    data = cur.fetchall()
    names = ''
    for row in data:
        name = row[0]
        names += name + '\n'
    con.close()
    return names

def get_players_roles():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = f"SELECT player_id, role FROM players"
    cur.execute(sql)
    data = cur.fetchall()
    con.close()
    return data

def set_roles(amount):
    game_roles = ['citizen']*amount
    mafies = int(amount * 0.3)
    for i in range(mafies):
        game_roles[i] = 'mafia' 
    shuffle(game_roles)
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = f"SELECT player_id FROM players"
    cur.execute(sql)
    players_ids = cur.fetchall()
    for role, row in zip(game_roles, players_ids):
        sql = f'UPDATE players SET role = "{role}" WHERE player_id = {row[0]}'
        cur.execute(sql)
    con.commit()
    con.close()

def vote(type, username, player_id):
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    #выбираем имя из таблицы игроков по айди где игрок еще не умер и не голосовал 
    sql = f"SELECT username FROM players WHERE player_id = {player_id} AND voted = 0 AND dead = 0"
    cur.execute(sql)
    can_vote = cur.fetchone()#выбираем только одного игрока
    if can_vote:#если может голосавать
        #голосуем за игрока передаем имя за которого проголосовали и ставим плюс один что за него проголосовали 
        cur.execute(f'UPDATE players SET {type} = {type} + 1 WHERE username = "{username}"')
        #ставим значене что он уже проголосовал
        cur.execute(f'UPDATE players SET voted = 1 WHERE player_id = {player_id}')
        con.commit()
        con.close()
        return True#возвращяем тру что он смог проголосовать
    con.close()
    return False#иначе если он не смог проголосовать то фалсе
    
def mafia_kill():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    #выбираем за кого больше всего отдала голосов мафия
    cur.execute(f'SELECT MAX(mafia_vote) FROM players')
    max_votes = cur.fetchone()[0]
    #выбираем кол-во игроков за мафию которых не убили
    cur.execute(f"SELECT COUNT(*) FROM players WHERE dead = 0 and role = 'mafia'")
    mafia_alive = cur.fetchone()[0]
    username_killed = 'никого'
    #максимальное кол-во голосов мафии должно быть равно кол-ву мафии
    if max_votes == mafia_alive:
        #получаем пользователя за которого проголосовали
        cur.execute(f"SELECT username FROM players WHERE mafia_vote = {max_votes}")
        username_killed = cur.fetchone()[0]
        #делаем update БД ставим что игрок мертв
        cur.execute(f"UPDATE players SET dead = 1 WHERE username = '{username_killed}'")
        con.commit()
    con.close()
    return username_killed

def citizen_kill():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    #выбираем за кого больше всего отдали голосов горожане  
    cur.execute(f'SELECT MAX(citizen_vote) FROM players')
    max_votes = cur.fetchone()[0]
    #выбираем кол-во игроков за горожан которых не убили
    cur.execute(f"SELECT COUNT(*) FROM players WHERE citizen_vote = {max_votes}")
    max_votes_count = cur.fetchone()[0]
    username_killed = 'никого'
    #ставим условие что если максимальное кол голосов равно 1
    if max_votes_count == 1:
        #выбираем имя пользователя из таблицы игроков где число проголосовавших горожан равно максимальному кол голосов
        cur.execute(f"SELECT username FROM players WHERE citizen_vote = {max_votes}")
        username_killed = cur.fetchone()[0]
        #обновляем таблицу ставим что игрок мертв и передаем его имя что он мертв 
        cur.execute(f"UPDATE players SET dead = 1 WHERE username = '{username_killed}'")
        con.commit()#сохраняем
    con.close()#закрываем
    return username_killed #возвращяем имя пользователя который умер
    

def check_winner():
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    cur.execute(f"SELECT COUNT(*) FROM players WHERE dead = 0 AND role = 'mafia'")
    mafia_alive = cur.fetchone()[0]
    cur.execute(f"SELECT COUNT(*) FROM players WHERE dead = 0 AND role != 'mafia'")
    citizen_alive = cur.fetchone()[0]
    con.close()
    if mafia_alive >= citizen_alive:
        return 'Мафия'
    elif mafia_alive == 0:
        return 'Горожане'

def clear(dead = False):
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    sql = f"UPDATE players SET citizen_vote = 0, mafia_vote = 0, voted = 0"
    if dead:
        sql += ', dead = 0'
    cur.execute(sql)
    con.commit()
    con.close()



if __name__ == "__main__":
    print(check_winner())