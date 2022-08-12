import random


from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

with open('data.txt', 'r') as f:
    API_TOKEN = f.readline()

with open('words.txt', 'r', encoding='utf-8') as f:
    corpus = [i.lower() for i in f.read().split('\n')]
users = {}

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)

dp = Dispatcher(bot, storage=MemoryStorage())


class Form(StatesGroup):
    all = State() #стейт состояния ставим когда вырубить игру
    game = State() #стейт игры включаем когда начинаем играть


class User():
    def __init__(self, id, word):
        self.id = id
        self.word = word #то слово, которое мы взяли из файла
        self.errors = 0

        self.state = '_' * len(self.word) #переменная этапов

    def __repr__(self):
        return f'id: {self.id}, word: {self.word}, state: {self.state}, errors: {self.errors}'


@dp.message_handler(state='*', commands=['start'])
async def send_welcome(message: types.Message):
    '''
    Хэндлер для обработки команд start
    '''
    await bot.send_message(message.chat.id,
                           'Привет) Я бот-виселица, чтобы начать игру, напиши мне /game')


@dp.message_handler(state='*', commands=['game']) # * не смотрит на состояние которое сейчас
async def start_game(message: types.Message):
    await Form.game.set() #устанавливаем состояние игры
    users[message.chat.id] = User(message.chat.id, corpus[random.randint(0, len(corpus) - 1)])
    await bot.send_message(message.chat.id, 'Игра началась! Угадай слово!')

    await bot.send_message(message.chat.id, users[message.chat.id].state)


@dp.message_handler(state=Form.game)
async def game(message: types.Message):
    text = message.text
    id_ = message.chat.id
    print(text, type(text), id_, users)
    if len(text) != 1: # если написали слово целиком
        if users[message.chat.id].word.lower() != text.lower(): # если не угадал проверяем слово пользователя с тем которое он ввел
            await bot.send_message(message.chat.id, 'Ошибка!')
            users[id_].errors += 1
            if users[id_].errors == 6:
                await bot.send_message(message.chat.id, 'Поражение((')
                await bot.send_message(message.chat.id, users[id_].word)
                await bot.send_photo(message.chat.id, open(f'{users[id_].errors + 1}.jpg', 'rb'))
                del users[id_]
                await Form.all.set()
                return
        else: #угадал слово целиком
            await bot.send_message(message.chat.id, 'Победа!')
            await bot.send_message(message.chat.id, users[id_].word)
            await bot.send_photo(message.chat.id, open(f'{users[id_].errors + 1}.jpg', 'rb'))
            del users[id_]
            await Form.all.set()
            return
    else:
        if text in users[id_].word and text not in users[id_].state: # если ввел букву которая есть в слове которую он раньше не угадывал
            idx = [i for i in range(len(users[id_].word)) if users[id_].word[i] == text]
            for i in idx:
                users[id_].state = users[id_].state[:i] + users[id_].word[i] + users[id_].state[i + 1:]
            if users[id_].state == users[id_].word:
                await bot.send_message(message.chat.id, 'Победа!')
                await bot.send_message(message.chat.id, users[id_].word)
                await bot.send_photo(message.chat.id, open(f'{users[id_].errors + 1}.jpg', 'rb'))
                del users[id_]
                await Form.all.set()
                return
        else:
            users[id_].errors += 1
            if users[id_].errors == 6:
                await bot.send_message(message.chat.id, 'Поражение((')
                await bot.send_message(message.chat.id, users[id_].word)
                await bot.send_photo(message.chat.id, open(f'{users[id_].errors + 1}.jpg', 'rb'))
                del users[id_]
                await Form.all.set()
                return
            await bot.send_message(message.chat.id, 'Ошибка!')
        await bot.send_message(message.chat.id, users[id_].state)
        await bot.send_photo(message.chat.id, open(f'{users[id_].errors + 1}.jpg', 'rb'))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
