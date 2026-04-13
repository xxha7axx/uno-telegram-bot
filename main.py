import os
import random
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Отримуємо токен з Railway
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Сховище для ігор: {chat_id: {players: [], deck: [], current_card: ""}}
games = {}

def create_deck():
    colors = ['🔴', '🟢', '🔵', '🟡']
    values = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    return [f"{c} {v}" for c in colors for v in values]

@dp.message(Command("new_uno"))
async def create_game(message: types.Message):
    chat_id = message.chat.id
    games[chat_id] = {'players': [message.from_user.id], 'status': 'lobby'}
    
    builder = InlineKeyboardBuilder()
    builder.button(text="Приєднатися 🙋‍♂️", callback_data="join_game")
    builder.button(text="Почати гру 🚀", callback_data="start_game")
    
    await message.answer(f"🎮 **Гра Уно створюється!**\nГравців у лобі: 1", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "join_game")
async def join_game(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    
    if user_id not in games[chat_id]['players']:
        games[chat_id]['players'].append(user_id)
        await callback.answer("Ви приєдналися!")
        await callback.message.edit_text(f"🎮 **Гра Уно створюється!**\nГравців у лобі: {len(games[chat_id]['players'])}", 
                                        reply_markup=callback.message.reply_markup)
    else:
        await callback.answer("Ви вже у грі!", show_alert=True)

@dp.callback_query(F.data == "start_game")
async def start_game(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    if len(games[chat_id]['players']) < 2:
        await callback.answer("Потрібно хоча б 2 гравці!", show_alert=True)
        return

    deck = create_deck()
    random.shuffle(deck)
    start_card = deck.pop()
    
    games[chat_id].update({'deck': deck, 'status': 'playing', 'current_card': start_card})
    
    await callback.message.answer(f"🚀 **Гру розпочато!**\nПерша карта на столі: **{start_card}**\n\n(Логіка ходів буде в наступному оновленні)")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
