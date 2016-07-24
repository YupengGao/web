import os
from bottle import route, run
from bottle import static_file
from bottle import error
from bottle import route, abort,request,template
#from bottle_sqlite import SQLitePlugin
import imageServer
import time
import json
from bottle import static_file
import codecs
import mysql
import uuid
from bottle import error
import utils
import stripepay

@route('/createAccount', method='post')
def create(): 
    response={}
    try:
        reader = codecs.getreader("utf-8")
        data = json.load(reader(request.body))
        #data=json.load(request.body.read().decode('utf8'))
        firstName='\''+data['firstName']+'\''
        lastName='\''+data['lastName']+'\''
        nickName='\''+data['nickName']+'\''
        telephone='\''+data['telephone']+'\''
        email='\''+data['email']+'\''
        userPass='\''+utils.md5(data['userPass'])+'\''
        sql="insert into User (firstName, lastName, nickName, telephone,email,userPass) values(%s, %s,%s, %s,%s, %s)" %(firstName,lastName,nickName,telephone,email, userPass)
        userID=mysql.query(sql,0)[0]
        #print (userID)        
        token=uuid.uuid4().hex
        response['userID']=userID
        response['token']=token
        userIDstr='\''+str(userID)+'\''
        token='\''+token+'\''
        sql="insert into Token (created_at, userID, generatedToken) values (TIMESTAMPADD(MONTH,1,CURRENT_TIMESTAMP), %s, %s)" % (userIDstr, token)
        mysql.query(sql,1)        
    #return "created success"
    except:
        response['status']="Server error, your email or telephone may have been used"
    return json.dumps(response)

@route('/login', method='post')
def login():
    reader = codecs.getreader("utf-8")
    data = json.load(reader(request.body))
    email=data['email']
    userPass=utils.md5(data['userPass'])
    sql="select * from User where email='%s' and userPass='%s'" %(email, userPass)
    #return sql
    response={}
    result=mysql.query(sql,1)
    if result:
        response['status']="login successful"
    else:
        response['status']="wrong password or username"
    return response


@route('/tokenLogin', method='post')
def tokenLogin():
    reader = codecs.getreader("utf-8")
    data = json.load(reader(request.body))
    userID=data['userID']
    token=data['token']
    sql="select * from Token where userID ='%s' and generatedToken='%s'" %(userID, token)
    #return sql
    response={}
    result=mysql.query(sql,1)
    if result:
        response['status']="login successful"
    else:
        response['status']="wrong password or username"
    return response


@route('/restricted')
def restricted():
    abort(401, "Sorry, access denied.")

@route('/my_ip')
def show_ip():
    ip = request.environ.get('REMOTE_ADDR')
         # or ip = request.get('REMOTE_ADDR')
        # or ip = request['REMOTE_ADDR']
    return template("Your IP is: {{ip}}", ip=ip)
#@route('/static/<filename>')
#def server_static(filename):
#	return static_file(filename, root='C:/book/bottleTest/static')

@route('/')
@route('/hello/<name>')
def index(name='stranger'):
	return "hello "+name



@error(404)
def error404(error):
    return json.dumps('Nothing here, sorry')

@route('/images/<filename:path>')
def callback(filename):
   return static_file(filename,root='e:\\images')

@route('/forum')
def callback():
    id0=request.query.id
    page=request.query.page
    return "page "+page+ " id "+id0


def now():
  return str(int(time.time()))

def produceFileID():
    return str(time.time()).split('.')[1]

@route('/notify', method='post')
def notify():
    reader = codecs.getreader("utf-8")
    data = json.load(reader(request.body))
    userID=data['userID']    
    token=data['token']
    sql="select * from Token where userID ='%s' and generatedToken='%s'" % (userID, token)
    result=mysql.query(sql,1)
    if not result:
        return json.dumps({"status":"wrong"})
    toUserID=data['toUserID']
    message=data['message']
    sql="select regID from androidRegID where userID ='%s' " %(toUserID);
    regID=mysql.query(sql,1)
    utils.push(regID, message)


@route('/sign')
def sign():
    #numImages=int(request.query.numImages)
    userID=request.query.userID
    token='\''+request.query.token+'\''
    sql="select * from Token where userID =%s and generatedToken=%s" % (userID, token)
    #return sql
    result=mysql.query(sql,1)
    if not result:
        return json.dumps({"status":"wrong"})
    params={}

    params["public_id"]=uuid.uuid4().hex[:-7]+produceFileID()
    #for i in range(0, numImages):
    #    params["public_ids"][i]=uuid.uuid4().hex[:-7]+produceFileID()
    params["timestamp"] = now()
    api_key="739771188655879"
    api_secret= "jXP-X6O9aK_FnZEWe8viRLVQXyU"
    #global params
    params = imageServer.cleanup_params(params)
    params["signature"] = imageServer.api_sign_request(params, api_secret)
    params["api_key"] = api_key
    sql="insert into photos(userId, link) values('%s', '%s')"%(userID, params["public_id"])
    mysql.query(sql,0)
    return params

@route('/postMessage', method='post')
def postMessage():
    reader = codecs.getreader("utf-8")
    data = json.load(reader(request.body))
    userID=data['userID']
    token=data['token']
    sql="select * from Token where userID ='%s' and generatedToken='%s'" % (userID, token)
    result=mysql.query(sql,1)
    if not result:
        return json.dumps({"status":"wrong"})
    toUserID=data['toUserID']
    message=data['message']
    sql="insert into messages (fromUserID, toUserID, content) values('%s','%s','%s')"%(userID,toUserID,message)
    mysql.query(sql,0)
    return json.dumps({"status":"message inertion successful"})

@route('/charge', method='post')
def charge(): 
    reader = codecs.getreader("utf-8")
    data = json.load(reader(request.body))
    amount=data['amount']
    stripeToken=data['stripeToken']
    #email=data['email']
    #stripepay.chargeCard(email,stripeToken,amount)
    return stripepay.charge2(amount,stripeToken)

@route('/addLocation', method='post')
def addLocation():
    reader = codecs.getreader("utf-8")
    data = json.load(reader(request.body))
    phoneNumber=data['phoneNumber']
    website=data['website']
    name=data['name']
    placeType=data['placeType']
    address=data['address']
    city=data['city']
    zipcode=data['zipcode']
    state=data['state']
    latitude=data['latitude']
    longtitude=data['longtitude']
    sql="insert into location(name, website,phoneNumber,placeType, address, city,zipcode,state,latitude,longtitude) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(name, website,phoneNumber,placeType, address, city,zipcode,state,latitude,longtitude)
    result=mysql.query(sql,0)
    if result:
        return ("successful")
    else:
        return ("server error")

@route('/getGym')
def getGym():
    #sql="select * from location"
    results={}
    #results=mysql.query(sql,2)
    return json.dumps(results)


@route('/getImg/<id>')
def getImg(id):
    sql="select * from photos where userID='%s'" %(id)
    results={}
    results=mysql.query(sql,2)
    return json.dumps(results)

@route('/coachInfo/<id>')
def getCoachInfo(id):
    response={}
    sql="select * from trainerPlaces join location where trainerPlaces.gymID=location.id and trainerPlaces.trainerID='%s'" %(id)
    response['locations']=mysql.query(sql,2)
    sql="select * from reviews where toUserID='%s'" %(id)
    response['reviews']=mysql.query(sql,2)
    sql="select * from photos where userID='%s'" %(id)
    response['images']=mysql.query(sql,2)
    sql="select * from TrainerTime where trainerID='%s'" %(id)
    response['timeslots']=str(mysql.query(sql,2))
    return json.dumps(response)
    #return response

@route('/searchGym', method='post')
def searchGym():
    reader = codecs.getreader("utf-8")
    data = json.load(reader(request.body))
    userID=data['userID']
    token=data['token']
    sql="select * from Token where userID ='%s' and generatedToken='%s'" %(userID, token)
    #return sql
    response={}
    result=mysql.query(sql,1)
    if not result:
        response['status']="wrong password or username"
        return response
    latitude=data['latitude']
    longtitude=data['longtitude']
    sql="""SET @lat = '%s';SET @lon = '%s'; """%(latitude,longtitude)
    mysql.query(sql,0)
    sql="""select * from location join
    (SELECT id, (6371 * acos( cos( radians(latitude) ) * cos( radians( @lat ) ) * 
    cos( radians( @lon ) - radians(longtitude) ) + sin( radians(latitude) ) * sin( radians( @lat ) ) ) ) as distance
    FROM location
    where latitude between @lat-1 and @lat+1
    and longtitude between @lon-1 and @lon+1
    having distance<50) as dis
    on location.id=dis.id"""
    response['locations']=mysql.query(sql,2)
    return json.dumps(response)


run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))root@ubuntu-512mb-sfo1-01:/home/coopals# more manage.py 
import os
from bottle import route, run
from bottle import static_file
from bottle import error
from bottle import route, abort,request,template
#from bottle_sqlite import SQLitePlugin
import imageServer
import time
import json
from bottle import static_file
import codecs
import mysql
import uuid
from bottle import error
import utils
import stripepay

@route('/createAccount', method='post')
def create(): 
    response={}
    try:
        reader = codecs.getreader("utf-8")
        data = json.load(reader(request.body))
        #data=json.load(request.body.read().decode('utf8'))
        firstName='\''+data['firstName']+'\''
        lastName='\''+data['lastName']+'\''
        nickName='\''+data['nickName']+'\''
        telephone='\''+data['telephone']+'\''
        email='\''+data['email']+'\''
        userPass='\''+utils.md5(data['userPass'])+'\''
        sql="insert into User (firstName, lastName, nickName, telephone,email,us
erPass) values(%s, %s,%s, %s,%s, %s)" %(firstName,lastName,nickName,telephone,em
ail, userPass)
        userID=mysql.query(sql,0)[0]
        #print (userID)        
        token=uuid.uuid4().hex
        response['userID']=userID
        response['token']=token
        userIDstr='\''+str(userID)+'\''
        token='\''+token+'\''
        sql="insert into Token (created_at, userID, generatedToken) values (TIME
STAMPADD(MONTH,1,CURRENT_TIMESTAMP), %s, %s)" % (userIDstr, token)
        mysql.query(sql,1)        
    #return "created success"
    except:
        response['status']="Server error, your email or telephone may have been 
used"
    return json.dumps(response)

@route('/login', method='post')
def login():
    reader = codecs.getreader("utf-8")
    data = json.load(reader(request.body))
    email=data['email']
    userPass=utils.md5(data['userPass'])
    sql="select * from User where email='%s' and userPass='%s'" %(email, userPas
s)
    #return sql
    response={}
    result=mysql.query(sql,1)
    if result:
        response['status']="login successful"
    else:
        response['status']="wrong password or username"
    return response


@route('/tokenLogin', method='post')
def tokenLogin():
    reader = codecs.getreader("utf-8")
    data = json.load(reader(request.body))
    userID=data['userID']
    token=data['token']
    sql="select * from Token where userID ='%s' and generatedToken='%s'" %(userI
D, token)
    #return sql
    response={}
    result=mysql.query(sql,1)
    if result:
        response['status']="login successful"
    else:
        response['status']="wrong password or username"
    return response


@route('/restricted')
def restricted():
    abort(401, "Sorry, access denied.")

@route('/my_ip')
def show_ip():
    ip = request.environ.get('REMOTE_ADDR')
         # or ip = request.get('REMOTE_ADDR')
        # or ip = request['REMOTE_ADDR']
    return template("Your IP is: {{ip}}", ip=ip)
#@route('/static/<filename>')
#def server_static(filename):
#	return static_file(filename, root='C:/book/bottleTest/static')

@route('/')
@route('/hello/<name>')
def index(name='stranger'):
	return "hello "+name



@error(404)
def error404(error):
    return json.dumps('Nothing here, sorry')

@route('/images/<filename:path>')
def callback(filename):
   return static_file(filename,root='e:\\images')

@route('/forum')
def callback():
    id0=request.query.id
    page=request.query.page
    return "page "+page+ " id "+id0


def now():
  return str(int(time.time()))

def produceFileID():
    return str(time.time()).split('.')[1]

@route('/notify', method='post')
def notify():
    reader = codecs.getreader("utf-8")
    data = json.load(reader(request.body))
    userID=data['userID']    
    token=data['token']
    sql="select * from Token where userID ='%s' and generatedToken='%s'" % (user
ID, token)
    result=mysql.query(sql,1)
    if not result:
        return json.dumps({"status":"wrong"})
    toUserID=data['toUserID']
    message=data['message']
    sql="select regID from androidRegID where userID ='%s' " %(toUserID);
    regID=mysql.query(sql,1)
    utils.push(regID, message)


@route('/sign')
def sign():
    #numImages=int(request.query.numImages)
    userID=request.query.userID
    token='\''+request.query.token+'\''
    sql="select * from Token where userID =%s and generatedToken=%s" % (userID, 
token)
    #return sql
    result=mysql.query(sql,1)
    if not result:
        return json.dumps({"status":"wrong"})
    params={}

    params["public_id"]=uuid.uuid4().hex[:-7]+produceFileID()
    #for i in range(0, numImages):
    #    params["public_ids"][i]=uuid.uuid4().hex[:-7]+produceFileID()
    params["timestamp"] = now()
    api_key="739771188655879"
    api_secret= "jXP-X6O9aK_FnZEWe8viRLVQXyU"
    #global params
    params = imageServer.cleanup_params(params)
    params["signature"] = imageServer.api_sign_request(params, api_secret)
    params["api_key"] = api_key
    sql="insert into photos(userId, link) values('%s', '%s')"%(userID, params["p
ublic_id"])
    mysql.query(sql,0)
    return params

@route('/postMessage', method='post')
def postMessage():
    reader = codecs.getreader("utf-8")
    data = json.load(reader(request.body))
    userID=data['userID']
    token=data['token']
    sql="select * from Token where userID ='%s' and generatedToken='%s'" % (user
ID, token)
    result=mysql.query(sql,1)
    if not result:
        return json.dumps({"status":"wrong"})
    toUserID=data['toUserID']
    message=data['message']
    sql="insert into messages (fromUserID, toUserID, content) values('%s','%s','
%s')"%(userID,toUserID,message)
    mysql.query(sql,0)
    return json.dumps({"status":"message inertion successful"})

@route('/charge', method='post')
def charge(): 
    reader = codecs.getreader("utf-8")
    data = json.load(reader(request.body))
    amount=data['amount']
    stripeToken=data['stripeToken']
    #email=data['email']
    #stripepay.chargeCard(email,stripeToken,amount)
    return stripepay.charge2(amount,stripeToken)

@route('/addLocation', method='post')
def addLocation():
    reader = codecs.getreader("utf-8")
    data = json.load(reader(request.body))
    phoneNumber=data['phoneNumber']
    website=data['website']
    name=data['name']
    placeType=data['placeType']
    address=data['address']
    city=data['city']
    zipcode=data['zipcode']
    state=data['state']
    latitude=data['latitude']
    longtitude=data['longtitude']
    sql="insert into location(name, website,phoneNumber,placeType, address, city
,zipcode,state,latitude,longtitude) values('%s','%s','%s','%s','%s','%s','%s','%
s','%s','%s')"%(name, website,phoneNumber,placeType, address, city,zipcode,state
,latitude,longtitude)
    result=mysql.query(sql,0)
    if result:
        return ("successful")
    else:
        return ("server error")

@route('/getGym')
def getGym():
    #sql="select * from location"
    results={}
    #results=mysql.query(sql,2)
    return json.dumps(results)


@route('/getImg/<id>')
def getImg(id):
    sql="select * from photos where userID='%s'" %(id)
    results={}
    results=mysql.query(sql,2)
    return json.dumps(results)

@route('/coachInfo/<id>')
def getCoachInfo(id):
    response={}
    sql="select * from trainerPlaces join location where trainerPlaces.gymID=loc
ation.id and trainerPlaces.trainerID='%s'" %(id)
    response['locations']=mysql.query(sql,2)
    sql="select * from reviews where toUserID='%s'" %(id)
    response['reviews']=mysql.query(sql,2)
    sql="select * from photos where userID='%s'" %(id)
    response['images']=mysql.query(sql,2)
    sql="select * from TrainerTime where trainerID='%s'" %(id)
    response['timeslots']=str(mysql.query(sql,2))
    return json.dumps(response)
    #return response

@route('/searchGym', method='post')
def searchGym():
    reader = codecs.getreader("utf-8")
    data = json.load(reader(request.body))
    userID=data['userID']
    token=data['token']
    sql="select * from Token where userID ='%s' and generatedToken='%s'" %(userI
D, token)
    #return sql
    response={}
    result=mysql.query(sql,1)
    if not result:
        response['status']="wrong password or username"
        return response
    latitude=data['latitude']
    longtitude=data['longtitude']
    sql="""SET @lat = '%s';SET @lon = '%s'; """%(latitude,longtitude)
    mysql.query(sql,0)
    sql="""select * from location join
    (SELECT id, (6371 * acos( cos( radians(latitude) ) * cos( radians( @lat ) ) 
* 
    cos( radians( @lon ) - radians(longtitude) ) + sin( radians(latitude) ) * si
n( radians( @lat ) ) ) ) as distance
    FROM location
    where latitude between @lat-1 and @lat+1
    and longtitude between @lon-1 and @lon+1
    having distance<50) as dis
    on location.id=dis.id"""
    response['locations']=mysql.query(sql,2)
    return json.dumps(response)


run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
root@ubuntu-512mb-sfo1-01:/home/coopals# more manage.py 
import os
from bottle import route, run
from bottle import static_file
from bottle import error
from bottle import route, abort,request,template
#from bottle_sqlite import SQLitePlugin
import imageServer
import time
import json
from bottle import static_file
import codecs
import mysql
import uuid
from bottle import error
import utils
import stripepay

@route('/createAccount', method='post')
def create(): 
    response={}
    try:
        reader = codecs.getreader("utf-8")
        data = json.load(reader(request.body))
        #data=json.load(request.body.read().decode('utf8'))
        firstName='\''+data['firstName']+'\''
        lastName='\''+data['lastName']+'\''
        nickName='\''+data['nickName']+'\''
        telephone='\''+data['telephone']+'\''
        email='\''+data['email']+'\''
        userPass='\''+utils.md5(data['userPass'])+'\''
        sql="insert into User (firstName, lastName, nickName, telephone,email,us
erPass) values(%s, %s,%s, %s,%s, %s)" %(firstName,lastName,nickName,telephone,em
ail, userPass)
        userID=mysql.query(sql,0)[0]
        #print (userID)        
        token=uuid.uuid4().hex
        response['userID']=userID
        response['token']=token
        userIDstr='\''+str(userID)+'\''
        token='\''+token+'\''
        sql="insert into Token (created_at, userID, generatedToken) values (TIME
STAMPADD(MONTH,1,CURRENT_TIMESTAMP), %s, %s)" % (userIDstr, token)
        mysql.query(sql,1)        
    #return "created success"

