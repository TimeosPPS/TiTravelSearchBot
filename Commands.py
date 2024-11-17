from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand

Search_Command = Command('search')


Search_Command_Bot = BotCommand(command="search", description="Знайти місце")