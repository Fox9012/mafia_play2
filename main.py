import db
from telebot import TeleBot
from time import sleep

TOKEN = '7188390692:AAHEMx89TLCu-mateIp0pNtGglGOAte2LhM'
game = False
night = False

bot = TeleBot(TOKEN)

@bot.message_handler(commands = ['play'])
def start_game(message):
    if not game:
        bot.send_message(message.chat.id, 'напишите в лс "готов играть"')

@bot.message_handler(func = lambda m : m.text.lower() == 'готов играть' and m.chat.type == 'private')
def send_message(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name} играет')
    bot.send_message(message.from_user.id, 'Вы добавлены в игру')
    db.insert_player(message.from_user.id, message.from_user.first_name)
@bot.message_handler(commands = ['game'])
def game_start(message):
    global game
    players = db.playes_amount()
    if players >= 5 and not game:
        db.set_roles(players)
        players_roles = db.get_players_roles()
        mafia_usernames = db.get_mafia_usernames()
        for player_id, role in players_roles:
            bot.send_message(player_id, text=role)
            if role == 'mafia':
                bot.send_message(player_id, text=f'Все члены Мафии: \n{mafia_usernames}')
                img = open('mafia.jpg', 'rb')
                bot.send_photo(message.chat.id, img)
                img.close()
            elif role == 'citizen':
                img = open('citizen.jpg', 'rb')
                bot.send_photo(message.chat.id, img)
                img.close()
        game = True
        bot.send_message(message.chat.id, text='Игра началась!')
        return

    bot.send_message(message.chat.id, text='Недостаточно людей!')

@bot.message_handler(commands = ['kick'])
def kick(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = db.get_all_alive()
    if not night:
        if not username in usernames:
            bot.send_message(message.chat.id, 'Такого имени нет!')
            return
        voted = db.vote('citizen_vote', username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'Ваш голос учитан!')
            return
        bot.send_message(message.chat.id, 'У вас больше нет права голосовать!')
        return
    bot.send_message(message.chat.id, 'Вы не можете голосовать сейчас ночь!')

@bot.message_handler(commands = ['kill'])
def kill(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = db.get_all_alive()
    mafia_players = db.get_mafia_usernames()
    if night and message.from_user.first_name in mafia_players:
        if not username in usernames:
            bot.send_message(message.chat.id, 'Такого имени нет!')
            return
        voted = db.vote('mafia_vote', username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'Ваш голос учитан!')
            return
        bot.send_message(message.chat.id, 'У вас больше нет права голосовать!')
        return
    bot.send_message(message.chat.id, 'Вы не можете голосовать сейчас день!')

def get_killed(night):
    if not night:
        username_killed = db.citizen_kill()
        return f'Горожане выгнали : {username_killed}'
    username_killed = db.mafia_kill()
    return f'Мафия убила: {username_killed}'

def game_loop(message):
    global night
    bot.send_message(message.chat.id, 'Добро пожаловать! у вас есть 2 минуты чтобы познакомится')
    sleep(5)
    while True:
        username = get_killed(night)
        bot.send_message(message.chat.id, f'Убили:{username}')
        if night:
            bot.send_message(message.chat.id, 'Город засыпает просыпается Мафия. Наступила ночь')
        else:
            bot.send_message(message.chat.id, 'Город просыпается. Наступил день')
        winner = db.check_winner()
        if winner == 'Мафия' or winner == 'Горожане':
            bot.send_message(message.chat.id, f'Победили: {winner}')
            game = False
            return 
        night = not night
        alive = db.get_all_alive()
        alive = '\n'.join(alive)
        bot.send_message(message.chat.id, f'Остались в живых:\n{alive}')
        sleep(2)

if __name__ == "__main__":
    bot.polling(non_stop=True)