# def test1(func):
#     def wrapper():
#         func()
#
#     return wrapper
#
#
# def test2(func):
#     def wrapper():
#         func()
#
#     return wrapper
#
#
# def test3(func):
#     def wrapper():
#         func()
#
#     return wrapper
#
#
# def test4(func):
#     def wrapper():
#         func()
#
#     return wrapper
#
#
# @test1
# @test2
# @test3
# @test4
# def printt():
#     print(1)
#
#
# printt()
from telegram import Bot

bot = Bot('796415072:AAEHU0clqJOYQJlSHxMfJOmxcY_E6JgbZGs')
admins = bot.get_chat_administrators(-1001461432821)
print([a.user.id for a in admins if not a.user.is_bot])
