from flask import Flask, url_for
from flask import render_template,request,session,redirect
import config
import sqlite3


app=Flask(__name__)
app.config.from_object(config)

@app.route("/back2front")
def b2f():
    dictdata={
        'name':'wei',
        'columns':(1,2,3,4),
        'data':['data1','data2','data3','data4']
    }
    return render_template("back2front.html",**dictdata)

@app.route("/front2back", methods=['GET', 'POST'])
def f2b():
    if request.method=='POST':
        a=request.form["client_name"]
        print(type(a))
        return a +'你好'
    return render_template("front2back.html")

@app.route("/URL2back/name/<name>")
def U2b_name(name):
    print(f"name型別:{type(name)}")
    return f"我的名字:{name}"

@app.route("/URL2back/money/<int:money>")
def U2b_money(money):
    print(f"money型別:{type(money)}")
    return f"我有多少錢:{money}"

@app.route("/URL2back/dollars/<float:dollars>")
def U2b_dollars(dollars):
    print(f"dollars型別:{type(dollars)}")
    return f"換算成美金:{dollars}"

@app.route("/URL2back/all/<name>/<int:money>/<float:dollars>")
def U2b_all(name,money,dollars):
    return f"我的名字:{name}，我有多少錢:{money}，換算成美金:{dollars}"

#---------------以上基本教學-----------------
#---------------以下實作教學-----------------

@app.route("/")
def home():
    goodName=[]
    goodPrice=[]
    goodImg=[]

    conn = sqlite3.connect('schoolflask.db')
    db = conn.cursor()
    db.execute("select * from goods ")
    dbList=db.fetchall()
    conn.close()
    goodCount=len(dbList)
    for dbTuple in dbList:
        goodName.append(dbTuple[0])
        goodPrice.append(dbTuple[1])
        goodImg.append(dbTuple[2])

    dictdata={
        'goodName':goodName,
        'goodPrice':goodPrice,
        'goodImg':goodImg,
        'goodCount':goodCount
        }
    return render_template("home.html",**dictdata)

@app.route("/loginpage")
def loginpage():
    return render_template("login.html",notMatch=False)

@app.route("/logingo", methods=['POST'])
def logingo():
    email=request.form["InputEmail"]
    pwd=request.form["InputPassword"]

    conn = sqlite3.connect('schoolflask.db')
    db = conn.cursor()
    db.execute("select email,password from client ")

    dbList=db.fetchall()
    conn.close()
    for dbTuple in dbList:
        dbEmail=dbTuple[0]
        dbPwd=dbTuple[1]
        if dbEmail==email and dbPwd==pwd:
            session['email'] = email
            return redirect(url_for('home'))

    return render_template("login.html",notMatch=True)

@app.route("/logout")
def logout():
    if session.get('email')==None:
        return redirect(url_for('home'))
    del session['email']
    return redirect(url_for('home'))

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    sameEmail=False
    pwdNotMatch=False
    signupDone=False
    
    if request.method=='POST':
        email=request.form["InputEmail"]
        pwd=request.form["InputPassword"]
        check=request.form["InputPasswordCheck"]

        if pwd!=check:
            pwdNotMatch=True
            
        #------資料庫on---------
        conn = sqlite3.connect('schoolflask.db')
        db = conn.cursor()
        db.execute("select email from client")

        dbEmailList=db.fetchall()
        for dbEmailTuple in dbEmailList:
            dbEmailStr=dbEmailTuple[0]
            if email==dbEmailStr:
                sameEmail=True
                break
        
        if sameEmail==False and pwdNotMatch==False:
            signupDone=True
            db.execute(f"insert into client(email,password) values('{email}','{pwd}')")
            conn.commit()
        conn.close()
        #------資料庫off---------

        dictdata={
        'sameEmail':sameEmail,
        'pwdNotMatch':pwdNotMatch,
        'signupDone':signupDone,
        'email':email
        }
        return render_template("signup.html",**dictdata)

    dictdata={
        'sameEmail':sameEmail,
        'pwdNotMatch':pwdNotMatch,
        'signupDone':signupDone
        }
    return render_template("signup.html",**dictdata)

@app.route("/changepwd", methods=['GET', 'POST'])
def changepwd():
    if session.get('email')==None:
        return redirect(url_for('loginpage'))

    elif request.method=='POST':
        oldPwd=request.form["InputOldPassword"]
        pwd=request.form["InputPassword"]
        check=request.form["InputPasswordCheck"]

        #------資料庫on---------
        conn = sqlite3.connect('schoolflask.db')
        db = conn.cursor()
        db.execute(f"select password from client where email='{session['email']}'")
        dbOldPwd=db.fetchone()
        conn.close()
        #------資料庫off---------

        if oldPwd!=dbOldPwd[0]:
            return render_template("changepwd.html",oldPwdNotMatch=True,pwdNotMatch=False,changPwdDone=False)
        elif pwd!=check:
            return render_template("changepwd.html",oldPwdNotMatch=False,pwdNotMatch=True,changPwdDone=False)

        #------資料庫on---------
        conn = sqlite3.connect('schoolflask.db')
        db = conn.cursor()
        db.execute(f"update client set password ='{pwd}' where email='{session['email']}'")
        conn.commit()
        conn.close()
        #------資料庫off---------
        return render_template("changepwd.html",oldPwdNotMatch=False,pwdNotMatch=False,changePwdDone=True)

    return render_template("changepwd.html",oldPwdNotMatch=False,pwdNotMatch=False,changPwdDone=False)

@app.route("/cartpage")
def cartpage():
    if session.get('email')==None:
        return redirect(url_for('loginpage'))
    
    cartGoodDetialList=[]
    #------資料庫on---------
    conn = sqlite3.connect('schoolflask.db')
    db = conn.cursor()
    db.execute(f"select cart from client where email='{session['email']}'")
    dbCart=db.fetchone()

    dbCartSplit=dbCart[0].split(',')
    dbCartSplit.sort()
    # print(dbCartSplit)

    for cartGoodName in dbCartSplit:
        db.execute(f"select * from goods where name='{cartGoodName}'")
        dbCartGoodDetial=db.fetchone()
        # print(dbCartGoodDetial)
        cartGoodDetialList.append(dbCartGoodDetial)
    conn.close()
    #------資料庫off---------
    # print(dbCartGoodDetial)
    return render_template("cart.html",cartGoodDetialList=cartGoodDetialList)

@app.route("/cartAdd/<name>")
def cartAdd(name):
    if session.get('email')==None:
        return redirect(url_for('loginpage'))

    #------資料庫on---------
    conn = sqlite3.connect('schoolflask.db')
    db = conn.cursor()
    db.execute(f"select cart from client where email='{session['email']}'")
    dbOldCart=db.fetchone()
    if dbOldCart[0]==None:
        newCart=name
    else:
        newCart=dbOldCart[0]+','+name
    db.execute(f"update client set cart ='{newCart}' where email='{session['email']}'")
    conn.commit()
    conn.close()
    #------資料庫off---------
    return redirect(url_for('home'))

@app.route("/cartdel/<name>")
def cartdel(name):
    print("name",name)

    #------資料庫on---------
    conn = sqlite3.connect('schoolflask.db')
    db = conn.cursor()
    db.execute(f"select cart from client where email='{session['email']}'")
    dbOldCart=db.fetchone()
    dbOldCartSplit=dbOldCart[0].split(",")
    print(dbOldCartSplit)
    dbOldCartSplit.remove(name)
    newCart=",".join(dbOldCartSplit)
    print(newCart)
    db.execute(f"update client set cart ='{newCart}' where email='{session['email']}'")
    conn.commit()
    conn.close()
    #------資料庫off---------
    return redirect(url_for('cartpage'))

@app.route("/search")
def search():
    keyword=request.args.get("InputKeyword")
    goodName=[]
    goodPrice=[]
    goodImg=[]
    #------資料庫on---------
    conn = sqlite3.connect('schoolflask.db')
    db = conn.cursor()
    db.execute(f"select * from goods where name like '%{keyword}%'")
    resultList=db.fetchall()
    conn.close()
    resultCount=len(resultList)
    for resultTuple in resultList:
        goodName.append(resultTuple[0])
        goodPrice.append(resultTuple[1])
        goodImg.append(resultTuple[2])

    dictdata={
        'goodName':goodName,
        'goodPrice':goodPrice,
        'goodImg':goodImg,
        'resultCount':resultCount
        }

    return render_template("search.html",**dictdata)


if __name__=='__main__':
    app.run()