import discord
from discord.ext import commands, tasks
import datetime
import pyrebase
from config import firebaseConfig, token, channelId

bot = commands.Bot(command_prefix='.')
date = datetime.date.today()
ordinal = date.toordinal()

firebase=pyrebase.initialize_app(firebaseConfig)

db = firebase.database()

@bot.event
async  def on_ready():
    change_status.start()

@tasks.loop(hours=24)
async def change_status():
    channel = bot.get_channel(channelId)
    global date
    date = datetime.date.today()
    global ordinal
    ordinal = date.toordinal()
    global firebase
    global db
    msj = ""
    paraHoy = ""
    paraManana = ""
    fechas = db.get()
    if(type(fechas.each()) == 'list'):
        for fecha in fechas.each():
            fechaSt = fecha.key()
            year, month, day = fechaSt.split('-')
            fechaStr = month + '-' + day + '-' + year
            dateObj = datetime.datetime.strptime(fechaStr, '%m-%d-%Y').date()
            if(date == dateObj):
                for sse in fecha.val():
                    tarea = (fecha.val())[sse]
                    paraHoy = paraHoy + '\n' + '**-' + tarea + '**'
            if(date + datetime.timedelta(days=1) == dateObj):
                for sse in fecha.val():
                    tarea = (fecha.val())[sse]
                    paraManana = paraManana + '\n' + '**-' + tarea + '**'

    if(paraHoy != "" or paraManana != ""):
        msj = "***Recordatorios*** \U0001F4C5\n"
        if(paraHoy != ""):
            msj = msj + "Para hoy: " + paraHoy
        if(paraManana != ""):
            if(paraHoy != ""):
                msj = msj + "\n"    
            msj = msj + "Para mañana: " + paraManana
    else:
        msj = "**"

    await channel.send(msj)

@bot.command()
async def n(ctx, fecha, desc):
    global firebase
    global db
    epoch = datetime.datetime.now().timestamp()
    day, month, year = fecha.split('-')
    key = year + "-" + month + "-" + day
    db.child(key).child(str(int(epoch))).set(desc);

@bot.command()
async def cal(ctx):
    global firebase
    global db
    msj = "***Calendario*** \U0001F4C5"
    fechas = db.get()
    index = 1
    for fecha in fechas.each():
        fechaSt = fecha.key()
        year, month, day = fechaSt.split('-')
        fechaStr = day + '-' + month + '-' + year
        for sse in fecha.val():
            tarea = (fecha.val())[sse]
            msj = msj + '\n\n' + '**' + str(index) + ". " + tarea + '**\n' + "*para el " + fechaStr + '*'
            index += 1
    channel = bot.get_channel(channelId)
    await channel.send(msj)

@bot.command()
async def r(ctx, arg):
    global firebase
    global db
    fechas = db.get()
    index = 1
    for fecha in fechas.each():
        fechaSt = fecha.key()
        year, month, day = fechaSt.split('-')
        fechaStr = day + '-' + month + '-' + year
        for sse in fecha.val():
            if(index == int(arg)):
                db.child(fechaSt).child(sse).remove()
            index += 1

@bot.command()
async def m(ctx, arg, arg2):
    global firebase
    global db
    fechas = db.get()
    index = 1
    for fecha in fechas.each():
        fechaSt = fecha.key()
        year, month, day = fechaSt.split('-')
        fechaStr = day + '-' + month + '-' + year
        for sse in fecha.val():
            if(index == int(arg)):
                db.child(fechaSt).update({sse:arg2})
            index += 1

bot.run(token)
