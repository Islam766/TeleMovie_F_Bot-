import pymongo
import time
from  re import compile,IGNORECASE
from conf import *


client = pymongo.MongoClient(database_URI)

#sabt database  va jadval user
mydb = client["TelegramBT"]


myUser = mydb["User"]
#method baray insert user
def db_insert_user(chat_id,Captcha=None,Admin=False,VIP=False,Status=None):
    try:
        user_number_id = int( myUser.find().sort('_id', -1).limit(1)[0]['_id'])
        user_number_id += 1
    except IndexError:
        user_number_id = 0
    mydict = { "_id":user_number_id,"chat_id":chat_id, "Captcha": Captcha,  "Admin": Admin, "VIP":VIP, "Status":Status}
    myUser.insert_one(mydict)
#method for Find user
def db_find_user(F_argu,S_argu):
    return myUser.find_one({ F_argu:S_argu })

def db_update_user(chat_id,F_argu,S_argu):
    myUser.update_one({'chat_id':chat_id}, {"$set": {F_argu:S_argu}}, upsert=False)

#method baray delete User
def db_delete_user(F_argu,S_argu):
    myUser.delete_one({ F_argu:S_argu })

def last_user_id():
    user_number_id = int( myUser.find().sort('_id', -1).limit(1)[0]['_id'] )
    return user_number_id



myCaptcha = mydb["Captcha"]
#method baray insert Captcha
def db_insert_Captcha(Captcha_code,PIC_SRC):
    try:
        user_number_id = int( myCaptcha.find().sort('_id', -1).limit(1)[0]['_id'] )
        user_number_id += 1
    except IndexError:
        user_number_id = 0
    mydict = { "_id":user_number_id, "Captcha_code":Captcha_code, "PIC_SRC":PIC_SRC}
    return myCaptcha.insert_one(mydict)
#method baray Find Captcha
def db_find_Captcha(F_argu,S_argu):
    return myCaptcha.find_one({ F_argu:S_argu })
#method akharin captcha
def db_last_Captcha():
    user_number_id = int( myCaptcha.find().sort('_id', -1).limit(1)[0]['_id'] )
    return user_number_id



MC = mydb["MC"]
#method for Update data movie
def db_update_Movie(Movie_Name,F_argu,S_argu):
    MC.update_one({"Movie_Name":Movie_Name}, {"$set": {F_argu:S_argu}}, upsert=False)
#method for Find all movie
def db_find_Movie(Search):
    yyyy = MC.find({ "$text": { "$search": f"\"{Search}\"" } }).sort('Movie_Name', 1)
    if yyyy=='':
        return[None]
    else:
        return yyyy
def db_find_Movie_regex(Search):
    yyyy = MC.find({ "Movie_Name": { "$regex": compile(Search, IGNORECASE)}  }).sort('_id', -1)
    if yyyy=='':
        return[None]
    else:
        return yyyy
def db_find_one_Movie(Search):
    yyyy = MC.find_one({ "$text": { "$search": f"\"{Search}\"" } })
    if yyyy=='':
        return None
    else:
        return yyyy
def db_find_Movie_one_regex(Search):
    yyyy = MC.find_one({ "Movie_Name": { "$regex": compile(Search, IGNORECASE)}  })
    if yyyy=='':
        return None
    else:
        return yyyy
#method for Find movie white id
def db_find_Movie_by_id(F_argu,S_argu):
    return MC.find_one({ F_argu:S_argu })
#method for insert movie
def db_insert_Movie(File_id,Movie_Name,series,P,More_info,PIC_SRC,S=None,E=None):
    #find whit the name of show and retern that show if exist
    xxxx=MC.find_one({ "Movie_Name":Movie_Name })
    if xxxx != None and xxxx['Movie_Name']==Movie_Name:
        if series=="True":
            db_update_Movie(Movie_Name,f"VID_SRC.{S}.{E}.{P}",File_id)
        elif series=="False":
            db_update_Movie(Movie_Name,f"VID_SRC.{P}",File_id)
        return "it's Update yohoooo"
    else:
        try:
            user_number_id = int( MC.find().sort('_id', -1).limit(1)[0]['_id'] )
            user_number_id += 1
        except IndexError:
            user_number_id = 0
        mydict = { "_id":user_number_id, "Movie_Name":Movie_Name,"VID_SRC":{},"series":series,"PIC_SRC":PIC_SRC,"More_info":More_info}
        MC.insert_one(mydict)
        db_insert_Movie(File_id,Movie_Name,series,P,More_info,PIC_SRC,S,E)
        return "it's Create yohoooo"
        


#test or ...
#if __name__=="__main__":
#    db_=db_find_Movie_regex("you")
#    for i in db_:
#        print(i)
            

        

