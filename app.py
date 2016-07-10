from flask import Flask, render_template, json, request, redirect
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
import cloudinary
import cloudinary.uploader
import cloudinary.api
import hashlib
from datetime import datetime

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Books154pm'
app.config['MYSQL_DATABASE_DB'] = 'coopals'
app.config['MYSQL_DATABASE_HOST'] = '159.203.212.22'
mysql.init_app(app)

def md5(str):
    str=str.encode('utf-8')
    m = hashlib.md5()   
    m.update(str)
    return m.hexdigest()


def deleteImg(public_id, **options):
    cloudinary.config( 
      cloud_name = "coopals", 
      api_key="739771188655879",
      api_secret= "jXP-X6O9aK_FnZEWe8viRLVQXyU"
    )
    cloudinary.uploader.destroy(public_id)


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/showSignin')
def showSignIn():
    return render_template('signin.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/ShowverifyTrainer')
def ShowverifyTrainer():
    return render_template('ShowverifyTrainer.html')

@app.route('/login',methods=['POST','GET'])
def login():
    try:
        # _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        # validate the received values
        if _email and _password:
            conn = mysql.connect()
            cursor = conn.cursor()
            _md5_password = md5(_password)
            cursor.callproc('sp_login',[_email])
            # cursor.execute("select Password from Staff where EmailAddress = '%s'" %(_email))
            data = cursor.fetchall()
            for list in data:
                for elem in list:
                    password = elem
            if str(password) == _md5_password:
                return redirect('/userHome')
            else:
                return json.dumps({'error':'wrong email address or password'})
        else:
            
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()

@app.route('/userHome')
def userHome():
    return render_template('userHome.html')

@app.route('/ShowSearchPhoto')
def ShowSearchPhoto():
    return render_template('getphoto.html')

@app.route('/searchPhoto',methods=['POST','GET'])
def SearchPhotoByUserId():
    
    try:
        
        _userId = request.form['UserId']
        
        # validate the received values
        if _userId:
            
            # All Good, let's call MySQL
            conn = mysql.connect()
            cursor = conn.cursor()

            # _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_getPhotoByUserid',[_userId])
            print _userId
            data = cursor.fetchall()
            # data = data.decode(utf8)

            photos_dict = []
            for photo in data:
                    # print type(a)
                    photo_dict = {
                            'url': photo,
                            }
                    photos_dict.append(photo_dict)
            print photos_dict
            if len(data) is 0:                
                return json.dumps({'message':'There is no photos for the user !'})
                
                # return render_template('getphoto.html')
            else:
                # conn.commit()
                return json.dumps(photos_dict)
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':"asd"+str(e)})
    finally:
        cursor.close() 
        conn.close()

@app.route('/deletePhoto',methods=['POST','GET'])
def deletePhoto():
    try:
        _photoName = request.form['url']
        if _photoName:
            conn = mysql.connect()
            cursor = conn.cursor()
            # _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_delete',[_photoName])
            data = cursor.fetchall()
            if len(data) is 0:
                conn.commit()
                # get off the .jpg postfix
                deleteImg(_photoName[:-4])
                return json.dumps({'status':'OK'})
                # json.dumps({'html':'<span>did not get the photo name</span>'})
            else:
                return json.dumps({'status':'An Error occured'})
        else:
            return json.dumps({'html':'<span>did not get the photo name</span>'})

    except Exception as e:
        return json.dumps({'error':+str(e)})
    finally:
        cursor.close() 
        conn.close()

@app.route('/verifyTrainer',methods=['POST','GET'])
def verify():
    try:
        _userId = request.form['id']
        if _userId:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_verify',[_userId])
            data = cursor.fetchall()
            if len(data) == 0:
                conn.commit()
                return json.dumps({'status':'OK'})
            else:
                return json.dumps({'status':'error'})
        else:
            return json.dumps({'html':'<span>did not get the user Id</span>'})

    except Exception as e:
        return json.dumps({'error':+str(e)})
    finally:
        cursor.close() 
        conn.close()


@app.route('/getTrainerList',methods = ['POST','GET'])
def getTrainerList():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_TrainerNeedVerify')
        data = cursor.fetchall()
        Trainers_dict = []
        for trainer in data:
                # print type(a)
                photo_dict = {
                        'trainerId': trainer,
                        }
                Trainers_dict.append(photo_dict)

        if len(data) == 0:
            json.dumps({'No trainer need to be verify'})
        else:
            return json.dumps(Trainers_dict)
    except Exception as e:
        return json.dumps({'error':+str(e)})
    finally:
        cursor.close() 
        conn.close()

@app.route('/showverifyPhoto',methods = ['POST','GET'])
def showverifyPhoto():
    return render_template('showverifyPhoto.html')

@app.route('/getUserInfo', methods = ['POST','GET'])
def getUserInfo():
    try:
        _userID = request.form['userID']
        if _userID:
            conn = mysql.connect()
            cursor = conn.cursor()
            # _hashed_password = generate_password_hash(_password)
            # cursor.callproc('sp_getVerifyPhotoforUserId',[_userID])
            cursor.callproc('sp_getUserInfo',[_userID])
            data = cursor.fetchall()
            info_dict = []
            for elem in data:
                    print elem[0]
                    dict = {
                            'firstName': elem[2],
                            'lastName': elem[3],
                            # 'telephone':elem[6],
                            # 'email':elem[7],
                            # 'memberSince':elem[9].isoformat(),
                            # 'location':elem[10],
                            # 'workinfo':elem[11],
                            # 'school':elem[12],
                            # 'birthday':elem[13].isoformat(),
                            # 'gender':elem[16],
                            # 'average_rate':elem[17]
                            }
                    info_dict.append(dict)
            if len(data) is 0:                
                return json.dumps({'message':'There is no infor for the user !'})
            else:
                print info_dict
                return json.dumps(info_dict)
        else:
            return json.dumps({'html':'<span>no userinfo'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()

@app.route('/getVerifyPhotoList', methods = ['POST','GET'])
def getVerifyPhotoList():
    try:
        _userID = request.form['userID']
        if _userID:
            conn = mysql.connect()
            cursor = conn.cursor()
            # _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_getVerifyPhotoforUserId',[_userID])
            
            data = cursor.fetchall()
            info_dict = []
            for elem in data:
                    dict = {
                            'url':elem
                            }
                    info_dict.append(dict)
            if len(data) is 0:                
                return json.dumps({'message':'There is no verify photos for the user !'})
            else:
                print info_dict
                return json.dumps(info_dict)
        else:
            return json.dumps({'html':'<span>no userid'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()



if __name__ == "__main__":
    app.run(port=5002)
