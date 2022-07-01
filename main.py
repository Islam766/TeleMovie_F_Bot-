import logging
import os
import datetime
from re import findall
from time import sleep
from flask import Flask, request
from telebot import AsyncTeleBot,logger,console_output_handler,types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from conf import *
from model import *
from farsi_text_google import *

# create app
bot = AsyncTeleBot(bot_token)

# logging and save in log file
formatter = logging.Formatter('%(asctime)s (%(filename)s:%(lineno)d' + \
  ' %(threadName)s) %(levelname)s - %(name)s: "%(message)s"', \
  '%Y.%m.%d %H:%M:%S')
console_output_handler.setFormatter(formatter)
if not os.path.exists("logs"):
  os.mkdir("logs")
fh = logging.FileHandler("logs/"+\
  datetime.datetime.now().strftime("%Y.%m.%d-%H.%M.%S")+".log")
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)  # or use logging.INFO


#this is method which add ad and send that to user
@bot.message_handler(func=lambda m: m.caption[:11] == "advertising" and m.chat.id == admin_chat_id ,content_types=['photo'])
def advertising_just_work_for_admin(message):
    try:
        cap=message.caption[12:]
        last_one=last_user_id()
        for a in range(last_one+1):
            user=db_find_user("_id",a)
            sleep(0.25)
            bot.send_photo(user["chat_id"],message.json['photo'][0]['file_id'],caption=cap)
        bot.send_message(admin_chat_id,'ad its done')
    except Exception as e:
        bot.send_message(admin_chat_id,e)

#this is method which return photo file_id
@bot.message_handler(func=lambda m: m.caption[:15] == "photo_for_cover" and m.chat.id == admin_chat_id ,content_types=['photo'])
def photo_just_work_for_admin(message):
    try:
        bot.send_message(admin_chat_id,str(message.json['photo'][0]['file_id']))
    except Exception as e:
        bot.send_message(admin_chat_id,e)

#add video method
@bot.message_handler(func=lambda m: m.chat.id == admin_chat_id or admin_chat_id_two ,content_types=['video','document'])
def video_admin_handler(message):
    if message.caption == None:
        bot.send_message(message.chat.id,"caption is not exist" )
        return None
    if message.content_type=="document":
        file_id_src = message.document.file_id
        if message.document.file_name[-4:] == ".mkv" or ".avi" or ".mp4":
            bot.send_message(message.chat.id,"document movie is done" )
            # return None
            # print(message)
        elif message.document.file_name[-4:] == ".srt" or ".ssa" or ".sub" or ".zip" or ".rar":
            bot.send_message(message.chat.id,"subtitle is done" )
        else:
            bot.send_message(message.chat.id,"extension is not familiar" )
            return None
    elif message.content_type=="video":
        file_id_src=message.video.file_id

    caption=str(message.caption)
    caption2=caption.split("</R>")

    try:
        sleep(0.3)
        if caption2[1]=="True":
            #File_id,Movie_Name,series,P,More_info,PIC_SRC,S=None,E=None
            cccc = db_insert_Movie(file_id_src,caption2[0],caption2[1],caption2[2],caption2[3],caption2[4],caption2[5],caption2[6])
            bot.reply_to(message,cccc )
        elif caption2[1] == "False":
            # File_id,Movie_Name,series,P,More_info,PIC_SRC
            cccc = db_insert_Movie(file_id_src,caption2[0],caption2[1],caption2[2],caption2[3],caption2[4])
            bot.reply_to(message,cccc)
        # send as doc or video in to backup GRP and CHAN
        try:
            bot.send_video(backup_caht,file_id_src,caption=message.caption)
            bot.send_video(backup_caht_Gr,file_id_src,caption=message.caption)
        except:
            bot.send_document(backup_caht,file_id_src,caption=message.caption)
            bot.send_document(backup_caht_Gr,file_id_src,caption=message.caption)
    except Exception as errr:
        bot.send_message(admin_chat_id,errr)
        bot.reply_to(message,"لطفا دوباره تلاش کنید")

#log comand which work just for admin and so bad on heruku
@bot.message_handler(func=lambda m: int(m.chat.id) == admin_chat_id ,commands=["log_admin"])
def log_send_for_admin(message):  
    try:
        path=os.listdir("logs")
        for x in path:
            pathname = os.path.join("logs",x)
            file = open(pathname, 'r')
            bot.send_document(message.chat.id,file)
            sleep(0.5)
            file.close()
    except Exception as e:
        bot.send_message(admin_chat_id,e)


# this is help method for how to use bot 
@bot.message_handler(commands=["help"])
def help_method(message):
    text=f"""
اگر نمیتونی از ربات استفاده کنی روی لینک زیر بزن و
آموزش رو بخون (به همراه تصویر)
https://telegra.ph/How-to-use-telemove-11-17"""
    bot.send_message(message.chat.id,text)


# this is start method
@bot.message_handler(commands=["start"])
def send_welcome(message):
    if str(message.text)=='/start':
        text1="""سلام به تله مووی خوش آمدید 
برای دریافت فیلم و سریال فقط کافیه اسم فیلم و به انگلیسی یا فارسی برام بفرستی 
مثلا مردگان متحرک یا  the walking dead  
توی کانال مون هم میتونی عضو بشی 

❤️ @TeleMovie_Channel ❤️"""

        text2=f"""اگر به مشکلی خوردی یا نمیتونی از ربات استفاده کنی 
از کامند /help استفاده کن
یا میتونی به ادمین پیام بدی {admin_user_id}"""

        get_user=db_find_user("chat_id",message.chat.id)
        # agar user mojood nabashad
        if get_user == None:
            db_insert_user(message.chat.id,False,False,False,None)
            bot.send_photo(message.chat.id,baner_pic,text1)
        else:
            bot.send_message(message.chat.id,text2)
    elif str(message.text)[:11]=='/start DLMS':
        
        get_user=db_find_user("chat_id",message.chat.id)
        # agar user mojood nabashad
        if get_user == None: db_insert_user(message.chat.id,False,False,False,None)
        if str(message.text)[11:]!='':
            try:
                film=db_find_Movie_by_id('_id',int(message.text[11:]))
                def gen_markup():
                    #this is the glass buttom evrry time crate a net buttom after that you can click on it and after that yuo call callback_query method
                    markup = InlineKeyboardMarkup()
                    markup.row_width = 1
                    markup.add(InlineKeyboardButton(film["Movie_Name"], callback_data="<N>$^{0}$^{1}".format(film["Movie_Name"],film["_id"])))
                    return markup
                bot.send_message(message.chat.id, "همین و میخواستی ؟؟؟", reply_markup=gen_markup())
            except:
                bot.send_message(message.chat.id,'لینک نا معتبر')
        else:
            bot.send_message(message.chat.id,'لینک نا معتبر')

# this text_me which you can text me whit that
@bot.message_handler(commands=["text_me"])
def help_method(message):
    try:
        if message.text=='/text_me':
            if message.reply_to_message==None:
                bot.send_message(message.chat.id,'اگر میخوای پیام یا درخواستی به ادمین بفرستی میتونی از این کامند اسنفاده کنی\nفقط کافیه اول پیامت این کامند رو بنویسی یا  بعد از اینکه پیامتو برای ربات فرستادی این کامند رو ریپلای کنی')
            elif message.reply_to_message!=None:
                if message.reply_to_message.content_type=='text':
                    bot.send_message(admin_chat_id,f"#new_text_me {message.reply_to_message.text}")
                    bot.reply_to(message,'پیامت ارسال شد')
        else:
            bot.send_message(admin_chat_id,f"#new_text_me {message.text[8:]}")
            bot.reply_to(message,'پیامت ارسال شد')
    except:
        bot.send_message(message.chat.id,"پیامت ارسال نشد :((((")


#this is methos for share galss buttom
@bot.callback_query_handler(func=lambda call: call.data[:5] == '<URL>')
def callback_query_channel(call):
    qforall=call.data.split("$^")
    text3=f"""لینک زیر را به اشتراک بگذارید

`https://t.me/{link_of_robot_}?start=DLMS{qforall[1]}`
"""
    bot.send_message(call.from_user.id,text3, parse_mode="MARKDOWN")

#this is methos for galss buttom
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    #return persian text
    def persian(x:str):
        x=x.lower()
        x=x.replace('more than one sub','زیرنویس چند زبانه')
        x=x.replace('persian & english sub','زیرنویس فارسی وانگلیسی')
        x=x.replace('persian sub','زیرنویس فارسی')
        x=x.replace('all sub','دانلود تمام زیرنویس ها')
        x=x.replace('english softsub','سافت ساب انگلیسی')
        x=x.replace('persian softsub','سافت ساب فارسی')
        x=x.replace('persian hardsub','زیرنویس چسبیده فارسی')
        x=x.replace('dubbed in persian','دوبله فارسی')
        x=x.replace('no subtitles','بدون زیرنویس')
        x=x.replace('movie trailer','پیش ‌پرده')
        x=x.replace('unknown','نامشخص')
        return x
    back_buttom="بازگشت"
    # try: 
    qforall=call.data.split("$^")
    if qforall[0] == "<A>":
        bot.delete_message(call.from_user.id,call.message.message_id)
        text_finder(call.from_user.id,qforall[1])
        
    else:
        xyxy=db_find_Movie_by_id("_id",int(qforall[2]))
        if xyxy["series"]=='True':
            #this is for seriaes and show
            if qforall[0] == "<N>":
                bot.delete_message(call.from_user.id,call.message.message_id)
                def gen_markup():
                    markup = InlineKeyboardMarkup()
                    markup.row_width = 2
                    for x in dict(sorted(xyxy['VID_SRC'].items(), key=lambda item: item[0])):
                        y=persian(x)  #translate to farsi
                        markup.add(InlineKeyboardButton(y, callback_data= "<S>$^{0}$^{1}$^{2}".format(qforall[1],xyxy["_id"],x)))
                    markup.add(InlineKeyboardButton('اشتراک گذاری...',callback_data="<URL>$^{0}".format(qforall[2])),
                        InlineKeyboardButton(back_buttom, callback_data= "<A>$^{0}".format(qforall[1])))
                    return markup
                bot.send_photo(call.from_user.id,photo=xyxy["PIC_SRC"], caption="کدوم فصل ؟؟؟", reply_markup=gen_markup())
            elif qforall[0] == "<S>":
                def gen_markup_2():
                    markup = InlineKeyboardMarkup()
                    markup.row_width = 3
                    listforep=[]
                    for episode in dict(sorted(xyxy["VID_SRC"][qforall[3]].items(), key=lambda item: item[0])):
                        listforep.append(InlineKeyboardButton(episode, callback_data= "<E>$^{0}$^{1}$^{2}$^{3}".format(qforall[1],qforall[2],qforall[3],episode)))
                    markup.add(*listforep)
                    markup.add(InlineKeyboardButton(back_buttom, callback_data= "<N>$^{0}$^{1}".format(qforall[1],xyxy["_id"])))
                    return markup
                bot.edit_message_caption(caption="کدوم قسمت؟؟؟",chat_id=call.from_user.id,message_id=call.message.message_id,reply_markup=gen_markup_2())
            elif qforall[0] == "<E>":
                def gen_markup_3():
                    markup = InlineKeyboardMarkup()
                    markup.row_width = 1
                    for Resolution in dict(sorted(xyxy["VID_SRC"][qforall[3]][qforall[4]].items(), key=lambda item: item[0])):
                        regex1=findall(r'movie trailer|144p|240p|360p',Resolution)
                        if regex1==[]:
                            markup.add(InlineKeyboardButton(Resolution, callback_data= "<P>$^{0}$^{1}$^{2}$^{3}$^{4}".format(qforall[1],qforall[2],qforall[3],qforall[4],Resolution)))
                    markup.add(InlineKeyboardButton(back_buttom, callback_data= "<S>$^{0}$^{1}$^{2}".format(qforall[1],qforall[2],qforall[3])))          
                    return markup
                bot.edit_message_caption(caption="چه کیفیتی میخوای؟؟؟",chat_id=call.from_user.id,message_id=call.message.message_id,reply_markup=gen_markup_3())
            elif qforall[0] == "<P>":
                caption1=f"""
                نام سریال: {xyxy['Movie_Name']}\nاطلاعات بیشتر: {xyxy['More_info']}\n\n دانلود فیلم و سریال به همراه زیرنویس👇👇❤️\n {link_of_robot}
                """

                caption2=f"""
                نام سریال: {xyxy['Movie_Name']}\nفصل: {qforall[3]}\nقسمت: {qforall[4]}\nکیفیت: {qforall[5]}\nاطلاعات بیشتر: {xyxy['More_info']}\n\n دانلود فیلم و سریال به همراه زیرنویس👇👇❤️\n {link_of_robot}
                """
                def gen_markup_5():
                    markup = InlineKeyboardMarkup()
                    markup.row_width = 1
                    markup.add(InlineKeyboardButton(back_buttom, callback_data= "<E>$^{0}$^{1}$^{2}$^{3}".format(qforall[1],qforall[2],qforall[3],qforall[4])))
                    return markup
                bot.edit_message_caption(caption1,chat_id=call.from_user.id,message_id=call.message.message_id,reply_markup=gen_markup_5())
                data1=xyxy['VID_SRC'][qforall[3]][qforall[4]][qforall[5]]
                # send as doc or video
                # try:
                bot.send_video(chat_id=call.from_user.id,data=data1,caption=caption2)
                # except:
                bot.send_document(chat_id=call.from_user.id,data=data1,caption=caption2)

        elif xyxy["series"]=='False':
            if qforall[0] == "<N>":
                bot.delete_message(call.from_user.id,call.message.message_id)
                def gen_markup_4():
                    markup = InlineKeyboardMarkup()
                    markup.row_width = 2
                    for Resolution in dict(sorted(xyxy['VID_SRC'].items(), key=lambda item: item[0])):
                        regex1=findall(r'movie trailer|144p|240p|360p',Resolution)
                        if regex1==[]:
                            y=persian(Resolution)
                            markup.add(InlineKeyboardButton(y, callback_data= "<P>$^{0}$^{1}$^{2}".format(qforall[1],qforall[2],Resolution)))
                    markup.add(InlineKeyboardButton('اشتراک گذاری...',callback_data="<URL>$^{0}".format(qforall[2])),
                        InlineKeyboardButton(back_buttom, callback_data= "<A>$^{0}".format(qforall[1])))
                    return markup
                bot.send_photo(call.from_user.id,photo=xyxy["PIC_SRC"], caption="چه کیفیتی میخوای؟؟؟", reply_markup=gen_markup_4())
            elif qforall[0] == "<P>":
                caption1=f"""
                نام فیلم: {xyxy['Movie_Name']}\nاطلاعات بیشتر: {xyxy['More_info']}\n\n دانلود فیلم و سریال به همراه زیرنویس👇👇❤️\n {link_of_robot}
                """
                caption2=f"""
                نام فیلم: {xyxy['Movie_Name']}\nکیفیت: {qforall[3]}\nاطلاعات بیشتر: {xyxy['More_info']}\n\n دانلود فیلم و سریال به همراه زیرنویس👇👇❤️\n {link_of_robot}
                """
                def gen_markup_6():
                    markup = InlineKeyboardMarkup()
                    markup.row_width = 1
                    markup.add(InlineKeyboardButton(back_buttom, callback_data="<N>$^{0}$^{1}".format(qforall[1],qforall[2])))
                    return markup

                bot.edit_message_caption(caption=caption1,chat_id=call.from_user.id,message_id=call.message.message_id,reply_markup=gen_markup_6())
                data1=xyxy['VID_SRC'][qforall[3]]
                # send as doc or video
                try:
                    bot.send_video(chat_id=call.from_user.id,data=data1,caption=caption2)
                except:
                    bot.send_document(chat_id=call.from_user.id,data=data1,caption=caption2)
    # except Exception as e:
    #     bot.send_message(admin_chat_id,e)
    #     bot.answer_callback_query(call.id, "مشکلی بوجود آمده است دوباره تلاش کنید")


#handle all english and persian text for search in movie
@bot.message_handler(content_types=['text'])
def farsi_text_method(message):
    text_finder(message.chat.id,message.text)

#for query handling need have other func
def text_finder(message_chat_id,message_text):
    get_user=db_find_user("chat_id",message_chat_id)
    finnnnn=findall(r'^[ آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهیئ\s]+$',message_text)
    if finnnnn!=[]:
        fa_en_text='چیزی پیدا نکردم :(((\n شاید برا اینه که فارسی زدی'
        farsi_or_english = translate( message_text )
    elif finnnnn==[]:
        fa_en_text='پیدانکردم :(((('
        farsi_or_english = message_text
    if get_user != None:
        #find movie or ...
        find_in_mov=db_find_one_Movie( farsi_or_english )
        def gen_markup():
            #this is the glass buttom evrry time crate a net buttom after that you can click on it and after that yuo call callback_query method
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            for x in db_find_Movie( farsi_or_english ):
                markup.add(InlineKeyboardButton(x["Movie_Name"], callback_data="<N>$^{0}$^{1}".format(farsi_or_english,x["_id"])))
            return markup
        def gen_markup_regex():
            #this is the glass buttom evrry time crate a net buttom after that you can click on it and after that yuo call callback_query method
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            for x in db_find_Movie_regex( farsi_or_english ):
                markup.add(InlineKeyboardButton(x["Movie_Name"], callback_data="<N>$^{0}$^{1}".format(farsi_or_english,x["_id"])))
            return markup
        #if name of movie not fine or find
        if find_in_mov==None:
            finde_regexx=db_find_Movie_one_regex( farsi_or_english )
            bot.send_message(message_chat_id, "نـتایج ؟؟؟؟ اگر پیدا نمیکنی دقیق تر وارد کن.", reply_markup=gen_markup_regex())
            if finde_regexx== None:
                bot.send_message(message_chat_id, fa_en_text)
        else:
            bot.send_message(message_chat_id, "نـتایج ؟؟؟؟", reply_markup=gen_markup())



#this is method whith  forse user join to channel
@bot.chat_member_handler()
def chat_m(message: types.ChatMemberUpdated):
    if message.chat.id == chat_id_of_channel:
        # agar user mojood nabashad
        get_user=db_find_user("chat_id",message.from_user.id)
        if get_user == None: db_insert_user(message.from_user.id,True,False,False,None)
        else:
            user=bot.get_chat_member(chat_id_of_channel,message.from_user.id)
            if user.wait().status == 'member':
                db_update_user(message.from_user.id,'Captcha',True)
            elif user.wait().status == 'left':
                db_update_user(message.from_user.id,'Captcha',False)


# # this is pooling which call api in loop
# bot.remove_webhook()
# bot.infinity_polling()



# create app for falsk
server = Flask(__name__)

@server.route('/' + bot_token, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "its run", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://tmoviebot.herokuapp.com/' + bot_token)
    return "its run as fuck 0.1.1", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
