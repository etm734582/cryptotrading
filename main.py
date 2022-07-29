import discord
import creditss
import random
from discord.ext import commands
import json
import requests

client = discord.Client()
bot = commands.Bot(command_prefix='!', help_command=None)
token = creditss.token

#consts
moneydifflist = [25000.0, 10000.0, 5000.0, 1000.0, 500.0]
comissiondifflist = [0.1*0.01, 0.2*0.01, 0.5*0.01, 1*0.01, 3*0.01]

# system funcs
def getrate(c1, c2):
    response = json.loads(requests.get(f'https://api.bittrex.com/api/v1.1/public/getticker?market={c2}-{c1}').text)
    if response['success'] == False:
        response = json.loads(requests.get(f'https://api.bittrex.com/api/v1.1/public/getticker?market={c1}-{c2}').text)
        if response['success'] == False:
            print(f'Ошибка:\n{response}')
            return (f'Произошла ошибка. Это могло произойти потому что:\n1. Такой пары не существует\n2. Вы ввели неверный индекс', False)
        else:
            return (f'Курс {c1} к {c2} равен: 1 к {1/response["result"]["Bid"]}', 1/response["result"]["Bid"])
    else:
        return (f'Курс {c1} к {c2} равен: 1 к {response["result"]["Bid"]}', response["result"]["Bid"])


def isuserreg(name):
    with open('data.json', 'r') as file:
        jsons = json.load(file)
    if name in jsons['users'].keys():
        return True
    return False

def isuserplaying(name):
    with open('data.json', 'r') as file:
        jsons = json.load(file)
    if jsons['users'][name]['settings']['ingame']:
        return True
    return False
    # with open('data.json', 'r') as file:
    #     jsons = json.load(file)
    # if name in jsons['users'].keys():
    #     print(1)

# sys bot funcs
@bot.command(name='help')
async def help(ctx):
    await ctx.send(f'Данный бот симулирует торговлю криптовалютой, используя реальные курсы (курсы берутся с api.bittrex.com)\n\
    Системны команды:\n\
     - !help - помощь\n\
     - !reg - зарегистрироваться в системе\n\
     - !info - доп. информация\n\
     - !leavethesys - удалить данные о себе из системы\n\
     - !play (сложность по комиссии, сложность по начальному капиталу) - начать торговлю, выбрать уровень сложности от 0 до 4 (см. !info)\n\
     - !leavethegame - окончить игру (**!прогресс не сохраниится!**)\n\
     - !settings - показать настройки\n\
    "Геймплейные" команды:\n\
     - !balance - узнать ваш текущий по всем криптовалютам и доллару\n\
     - !sell (продаваемая валюта) (кол-во продаваемой валюты (all - обмять всю валюту)) (покупаемая валюта) - продать криптовалюту или доллар, с комиссией (Нужно указывать индекс вылюты, например: usd, eth, ltc)\n\
     - !rate (продаваемая валюта) (покупаемая валюта) - узнать цену одной валюты относительно другой БЕЗ КОМИССИИ (Нужно указывать индекс вылюты, например: usd, eth, ltc)\n\
     - !buy (покупаемая валюта) (количество покупаемой валюты) (продаваемая валюта) - покупка криптовалюты или доллара, при этом комиссия будет добавлена к продаваемой валюте')

@bot.command(name='info')
async def info(ctx):
    with open('info.txt', 'r', encoding='utf-8') as file:
        text = file.read()
        await ctx.send(text)

@bot.command(name='reg')
async def reg(ctx):
    name = str(ctx.author)
    if isuserreg(name):
        await ctx.send('Вы уже зарегестрированны в системе')
        return
    with open('data.json', 'r') as file:
        jsons = json.load(file)
    with open('data.json', 'w') as file:
        jsons['users'][name] = {
            'money': {
            },
            'settings': {
                'ingame': False
            }
        }
        jsons['users_amount']+=1

        json.dump(jsons, file, indent=3)

        await ctx.send('Вы зарегестрированны в системе')

@bot.command(name='leavethesys')
async def leavethesys(ctx):
    name = str(ctx.author)
    if not isuserreg(name):
        await ctx.send('*"Вы не можете выйти пока не вошли"* - Жак Фреско')
        return

    with open('data.json', 'r') as file:
        jsons = json.load(file)
    with open('data.json', 'w') as file:
        del jsons['users'][name]
        jsons['users_amount']-=1

        json.dump(jsons, file, indent=3)
        jsons['users_amount'] -= 1
        await ctx.send('Мы *гарантируем* что ваши данные были удалены, и *уверены*, что они *сто процентов* не будут переданы фсб или проданы')

@bot.command(name='play')
async def play(ctx, *args):
    name = str(ctx.author)
    if len(args) != 2:
        await ctx.send('Вы не ввели все нужные значения или ввели лишние')
        return
    cmsdfclt, mndfclt = args
    if not (cmsdfclt in '01234' and mndfclt in '01234'):
        await ctx.send('Вы ввели неправильное значение сложности')
        return
    if not isuserreg(name):
        await ctx.send('Если вы хотите потрейдить, то зарегистрируйтесь пожалуйста сначала (!reg), а то как мне фиксировать ваши сделки?')
        return
    if isuserplaying(name):
        await ctx.send('Вы уже в игре, зачем ещё раз в неё входить?')
        return


    with open('data.json', 'r') as file:
        jsons = json.load(file)
    with open('data.json', 'w') as file:
        jsons['users'][name] = {
            'money': {
                'usd': moneydifflist[int(cmsdfclt)]
            },
            'settings': {
                'ingame': True,
                'comissiondiff': int(cmsdfclt),
                'moneydiff': int(mndfclt),
                'comission': comissiondifflist[int(cmsdfclt)],
                'comission_factor': 1-comissiondifflist[int(cmsdfclt)],
                'comission_percent': f'{comissiondifflist[int(cmsdfclt)] * 100}%'
            }
        }
        json.dump(jsons, file, indent=3)
    await ctx.send('Вы в игре!')

@bot.command(name='leavethegame')
async def leavethegame(ctx):
    name = str(ctx.author)
    with open('data.json', 'r') as file:
        jsons = json.load(file)
    if not isuserreg(name):
        await ctx.send('Эмм... вы не в игре, да и... не зарегистрированы')
        return
    if not isuserplaying(name):
        await ctx.send('Вы даже не вошли в игру, а уже хотите выйти? 😟')
        return
    with open('data.json', 'w') as file:
        jsons['users'][name] = {
            'money': {
            },
            'settings': {
                'ingame': False
            }
        }
        # print(jsons)

        json.dump(jsons, file, indent=3)

        await ctx.send('Вы вышли из игры')


# gameplay bot funcs

@bot.command(name='rate')
async def rate(ctx, *args):
    if len(args) != 2:
        await ctx.send('Вы не ввели все нужные значения или ввели лишние')
        return
    coin1, coin2 = args
    rate = getrate(coin1, coin2)
    await ctx.send(rate[0])

@bot.command(name='sell')
async def sell(ctx, *args):
    name = str(ctx.author)
    with open('data.json', 'r') as file:
        jsons = json.load(file)
    money = jsons['users'][name]['money']
    comission_factor = jsons['users'][name]['settings']['comission_factor']
    if len(args) != 3:
        await ctx.send('Вы не ввели все нужные значения или ввели лишние')
        return
    coin1, qnty, coin2 = args

    if not isuserreg(name):
        await ctx.send('Если вы хотите потрейдить, то зарегистрируйтесь пожалуйста сначала (!reg), а то как мне фиксировать ваши сделки?')
    if not isuserplaying(name):
        await ctx.send('Эта команда доступна только в игре')
    if qnty == 'all':
        qnty = money[coin1]
    else:
        try:
            qnty = float(qnty)
        except:
            await ctx.send('Вы ввели неверное количество')
            return

    rate = getrate(coin1, coin2)

    if not rate[1]:
        await ctx.send(rate[0])
        return
    # with open('data.json', 'r') as file:
    #     jsons = json.load(file)
    # money = jsons['users'][name]['money']
    # comission_factor = jsons['users'][name]['settings']['comission_factor']
    #
    # if qnty == 'all':
    #     qnty = money[coin1]
    # else:
    #     qnty = float(qnty)

    if (not coin1 in money.keys()) or money[coin1] < qnty:
        await ctx.send(f'На вашем счёте недостаточно {coin1} для совершения такой сделки')
        return

    if not coin2 in money.keys():
        money[coin2] = 0

    money[coin1] -= qnty
    com_qnty = qnty*comission_factor
    money[coin2] += com_qnty*rate[1]

    if money[coin1] == 0.0:
        del money[coin1]

    await ctx.send(f'Вы успешно продали {qnty} (с учётом комиссии {com_qnty}) {coin1} за {qnty*rate[1]} {coin2}')

    with open('data.json', 'w') as file:
        json.dump(jsons, file, indent=3)

@bot.command(name='buy')
async def buy(ctx, *args):
    name = str(ctx.author)
    if len(args) != 3:
        await ctx.send('Вы не ввели все нужные значения или ввели лишние')
        return
    coin1, qnty, coin2 = args
    if not isuserreg(name):
        await ctx.send('Если вы хотите потрейдить, то зарегистрируйтесь пожалуйста сначала (!reg), а то как мне фиксировать ваши сделки?')
        return
    if not isuserplaying(name):
        await ctx.send('Эта команда доступна только в игре')
        return
    try:
        qnty = float(qnty)
    except:
        await ctx.send('Вы ввели неверное количество')
        return

    rate = getrate(coin1, coin2)

    if not rate[1]:
        await ctx.send(rate[0])
        return
    with open('data.json', 'r') as file:
        jsons = json.load(file)
    money = jsons['users'][name]['money']
    comission_factor = jsons['users'][name]['settings']['comission_factor']

    qnty = float(qnty)
    price = qnty*rate[1]/(1/comission_factor)

    if (not coin2 in money.keys()) or money[coin2] < price:
        await ctx.send(f'На вашем счёте недостаточно {coin2} для совершения такой сделки')
        return

    if not coin1 in money.keys():
        money[coin1] = 0

    money[coin2] -= price
    money[coin1] += qnty

    if money[coin2] == 0.0:
        del money[coin2]

    await ctx.send(f'Вы успешно купили {qnty} {coin1} за {price} {coin2}')

    with open('data.json', 'w') as file:
        json.dump(jsons, file, indent=3)

@bot.command(name='balance')
async def balance(ctx):
    name = str(ctx.author)

    if not isuserreg(name):
        await ctx.send('Ваших данных нет в нашей базе, вы похоже не зарегистрированы')
    if not isuserplaying(name):
        await ctx.send('Эта команда доступна только в игре')

    with open ('data.json', 'r') as file:
        jsons = json.load(file)
    msg = 'Ваши счета:\n'
    for i, j in jsons['users'][name]['money'].items():
        msg+=f' - {i}: {j}\n'
    await ctx.send(msg)

@bot.command(name='settings')
async def showsettings(ctx):
    name = str(ctx.author)
    if not isuserreg(name):
        await ctx.send('Ваших данных нет в нашей базе, вы похоже не зарегистрированы')
    with open ('data.json', 'r') as file:
        jsons = json.load(file)

    showing_settings = jsons['bot_settings']['showing_settings']
    user_settings = jsons['users'][name]['settings']

    msg = 'Ваши настройки:\n'
    for i, j in user_settings.items():
        if i in showing_settings.keys():
            if not isuserplaying(name):
                j = '*вы не в игре*'
            msg+=f' - {showing_settings[i]}: {j}\n'
    await ctx.send(msg)

bot.run(token)


























# users_info = {'users_amount': 1,
#               'users':{
#                   'Квакша':{
#                       'money':{
#                           'USD': 500,
#                           'BTC': 0.001
#                       },
#                       'settings':{
#                           'hide_moneyquantity': False
#                       }
#                   }
#               }
#           }
# with open('data.json', 'w') as file:
#     jsonl = json.dump(users_info, file, indent=3)
# with open('data.json', 'r') as file:
#     # a = file.read()
#     # print(a)
#     data = json.load(file)
# print(data)

# оч крутая фигня
# users_info_json = json.loads(json.dumps(users_info, indent=3))
# a = [j['money'] for i, j in users_info_json['users'].items()]
# for i in a:
#     i['USD'] +=357
