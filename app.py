import mysql.connector
from flask import Flask, render_template, request, session,url_for,redirect,current_app
from datetime import timedelta
import re
import os
import secrets
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/input'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

horiz={}
verti={}
total={}
univhashmap={}





def save_images(photo):
    hash_photo=secrets.token_urlsafe(10)
    _, file_extension=os.path.splitext(photo.filename)
    photo_name=hash_photo+file_extension
    file_path=os.path.join(current_app.root_path,'static/images',photo_name)
    photo.save(file_path)
    return photo_name

#############       lcs_function          ############# 



def printi(b,X,i,j):
  global count
  count=0
  if i==0 or j==0:
    return
  if b[i][j]=='↖':
    printi(b[:],X,i-1,j-1)
    #print(X[i-1],end=" ")
    count=count+1
  elif b[i][j]=='↑':
    printi(b,X,i-1,j)
  else:
    printi(b,X,i,j-1)

def lcs(X,Y,m,n):
  rows,cols=(m+1,n+1) 
  c = [[0 for i in range(cols)] for j in range(rows)]
  b = [[0 for i in range(cols)] for j in range(rows)]
  for i in range(1,m+1):
    for j in range(1,n+1):
      if X[i-1]==Y[j-1]:
        c[i][j]=c[i-1][j-1]+1
        b[i][j]='↖'
      elif c[i-1][j]>=c[i][j-1]:
        c[i][j]=c[i-1][j]
        b[i][j]='↑'
      else:
        c[i][j]=c[i][j-1]
        b[i][j]='←' 
  #print()
  #print("Final String : ")
  printi(b,X,m,n)
  return count
  #print()

#############       lcs_function          ############# 


def hashing(s):
  if s in univhashmap:
    return (univhashmap[s])
  else:
    s=list(s)
    val=""
    suma=0
    for i in s[1:]:
      suma=suma+ord(i)
    val=val+s[0]+str(round(suma/ord(s[0]),3))
    univhashmap[''.join(map(str, s))]=val
    return (val)


@app.route("/",methods=['GET','POST'])
def index():
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        #password="",
        database="lcs"
    )
    mycursor = mydb.cursor(dictionary=True)
    if request.method == "POST":
        files = request.files.getlist("files")
        y=request.files.get("myfile")
        i=1
        for file in files:
            mycursor.execute("INSERT INTO storage VALUES (%s,%s)",(i,save_images(file)))
            mydb.commit()
            i+=1
        #filename = secure_filename(y.filename)
        y.save(os.path.join(app.config['UPLOAD_FOLDER'], y.filename))
        #if filename:
        f=open(os.path.join(app.config['UPLOAD_FOLDER'], y.filename))
        a=f.readline()
        for i in range(0,int(a)):
            x=[]
            x=f.readline().split()
            for j in range(2,int(x[1])+2):
                x[j]=hashing(str (x[j]))
            total[i+1]=x[1:]
            if x[0]=='H':horiz[i+1]=x[1:]
            else: verti[i+1]=x[1:]
        print("Horiz: ",horiz)
        print("Verti: ",verti)
        print("Univhashmap: ",univhashmap)

          #############       horizontal_photos_dict           #############   

        tagmapidH={}                     #'c2.512':[1,4]
        for li in horiz:
            temp=horiz[li][1:]
            for j in temp:
                if j in tagmapidH:tagmapidH[j].append(li)
                else: tagmapidH[j]=[li]
        print("tagmapidH: ",tagmapidH)


        #############       vertical_photos_dict           #############  
        ##  there should be even vertical photos
        tagmapidV={}                     #'c2.512':[1,4]
        for li in verti:
            temp=verti[li][1:]
            for j in temp:
                if j in tagmapidV:tagmapidV[j].append(li)
                else: tagmapidV[j]=[li]
        print(tagmapidV)

        #############       all_together          #############   
        tagmapidall={}                     #'c2.512':[1,4]
        for li in total:
            temp=total[li][1:]
            for j in temp:
                if j in tagmapidall:tagmapidall[j].append(li)
                else: tagmapidall[j]=[li]
        print(tagmapidall)
        #print(len(tagmapidall))

        score=float('inf')
        listb=[]
        dummyV=[]
        leftoverV=[]    ## contains the pairs of vertical photos
        dummyV.append(2)    ## first pic is always H then second is always V
        for i in dummyV:
            score=float('inf')
            #print("i=",i)
            lista=[]
            temp=verti[i][1:]

            for val in temp:
                listb=tagmapidV[val]
                for j in listb:
                    if i==j: continue
                    if j not in lista:lista.append(j)
            #print("newlista: ",lista)
            newlista=lista.copy()

            for u in verti:
                if u in lista:lista.remove(u)
                elif u==i: continue
                else: lista.append(u)
            #print("lista: ",lista)
            
            if len(lista)==0:
                for g in newlista:
                    value=lcs(verti[i][1:],verti[g][1:],int(verti[i][0]),int(verti[g][0]))
                    if value<=score:
                        score=value
                        saveg=g
                li3=list (set (verti[i][1:]+verti[saveg][1:]))
                li3.insert(0,len(li3))

                for li in verti[i][1:]:
                    tagmapidV[li].remove(i)
                verti.pop(i)

                for li in verti[saveg][1:]:
                    tagmapidV[li].remove(saveg)
                verti.pop(saveg)

                for li in total[saveg][1:]:
                    if i not in tagmapidall[li]:tagmapidall[li].append(i)
                    tagmapidall[li].remove(saveg)
                total.pop(saveg)

                total[i]=li3
                leftoverV.append([i,saveg])

                if len(verti)!=0:
                    for t in verti:
                        dummyV.append(t)
                        break
                continue
                
            else:
                leftoverV.append([i,lista[0]])
                li3=list (set (verti[i][1:]+verti[lista[0]][1:]))
                li3.insert(0,len(li3))
                for li in verti[i][1:]:
                    tagmapidV[li].remove(i)
                verti.pop(i)

                for li in verti[lista[0]][1:]:
                    tagmapidV[li].remove(lista[0])
                verti.pop(lista[0])

                for li in total[lista[0]][1:]:
                    if i not in tagmapidall[li]:tagmapidall[li].append(i)
                    tagmapidall[li].remove(lista[0])
                total.pop(lista[0])

                total[i]=li3
                
                if len(verti)!=0:
                    for t in verti:
                        dummyV.append(t)
                        break
                continue


        print(leftoverV)
        #print(dummyV)
        #print(verti) 
        print(tagmapidall)
        print(total)
        print(verti) 


        dummyall=[]   ## very very imp consists of the final order of photo display
        leftoverall=[]
        score=0
        dummyall.append(1)
        for i in dummyall:
            score=0
            #print("i=",i)
            lista=[]
            temp=total[i][1:]
            for val in temp:
                listb=tagmapidall[val]
                for j in listb:
                    if i==j: continue
                    if j not in lista:lista.append(j)
            #print(lista)

            if len(lista)==0:
                leftoverall.append(i)
                for li in total[i][1:]:
                    tagmapidall[li].remove(i)
                total.pop(i)
                if len(total)!=0:
                    for t in total:
                        dummyall.append(t)
                        break
                continue

            else:
                for h in lista:
                    value=lcs(total[i][1:],total[h][1:],int(total[i][0]),int(total[h][0]))
                    if value>=score:
                        score=value
                        saveh=h
                #for li in total[saveh][1:]:
                #tagmapidall[li].remove(saveh)
                #total.pop(saveh)
                for li in total[i][1:]:
                    tagmapidall[li].remove(i)
                total.pop(i)
                dummyall.append(saveh)
                #print(dummyall)
                #print(total)
                #print(tagmapidall)
                #print(saveh)

        if len(total)!=0:
            for k in total.copy():
                if k not in dummyall: dummyall.append(k)
                for li in total[k][1:]:
                    tagmapidall[li].remove(k)
                total.pop(k)
        print("leftoverall: ",leftoverall)
        print("dummyall: ",dummyall)
        #print(total) 
        for i in leftoverV:
            dummyall.insert(dummyall.index(i[0])+1,i[1])
        print(dummyall)
        img1=[]
        for j in dummyall:
            mycursor.execute("select name from storage where photo_id=%s",(j,))
            dat=mycursor.fetchone()
            path='static/images'
            full = os.path.join(path,dat['name'])
            img1.append(full)
            mycursor.execute("delete from storage where photo_id=%s",(j,))
            mydb.commit()
        return render_template('showi.html',usr_img=img1)
    return render_template('index.html')






if __name__=='__main__':
    app.run(debug=True)