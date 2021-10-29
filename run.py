import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash,send_from_directory, session
from flask_session import Session
import random
import re
from datetime import datetime
from operator import itemgetter, attrgetter
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash 
#from flaskext.mysql import MySQL
import pymysql
import pymysql.cursors
from flask_mail import Mail, Message
from threading import Thread
import jwt
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from PIL import Image
import smtplib



#import itertools

def connectDatabase():
    return pymysql.connect(host='localhost', user = 'root', password = '', database = 'diccionari')
    '''return pymysql.connect(host='sql11.freemysqlhosting.net', user = 'sql11440739', password = 'Yv3qDs7JI4', database = 'sql11440739')'''
    '''return pymysql.connect(host='yahabla.mysql.pythonanywhere-services.com', user = 'yahabla', password = '43552115gGg.', database = 'yahabla$diccionari')'''


UPLOAD_FOLDER = './audios'
UPLOAD_FOLDER_IMG = './images'
'''UPLOAD_FOLDER = './yahabla/audios'
UPLOAD_FOLDER_IMG = './yahabla/images' '''
ALLOWED_EXTENSIONS = {'ogg', 'mp3', 'wma', 'aac', 'wav', 'opus', 'oga',''}
ALLOWED_EXTENSIONS_IMG = {'jpg', 'jpeg', 'png', 'tiff'}

app = Flask(__name__)
app.config['SECRET_KEY']='mysecretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_IMG'] = UPLOAD_FOLDER_IMG

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024


'''app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "yahablaweb@gmail.com"
app.config['MAIL_PASSWORD'] = "43552114gGg."'''

app.config['MAIL_SERVER'] = "smtp.ionos.es"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "yahabla@yahabla.com"
app.config['MAIL_PASSWORD'] = "43552114gGg.."




mail = Mail()
mail.init_app(app)

@app.errorhandler(413)
def request_entity_too_large(error):
    return 'El tamaño del archivo no puede pasar los 5mb. Vuelve atrás y selecciona uno más pequeño, por favor', 413


@app.route('/')
def inici():
    # Check if user is loggedin
    if 'loggedin' in session:
        # if User is loggedin show them the home page
        return render_template ("inici.html")
    # if User is not loggedin redirect to login page   
    return redirect(url_for ('login'))

@app.route('/formulari')
def formulari():
    if 'loggedin' in session:
        return render_template ("formulari.html")

    return redirect(url_for ('login'))

@app.route('/diccionari', methods=['GET','POST'])
def consultar():

    
    if 'loggedin' in session:
        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM diccionari WHERE id_usuari = '{0}' ".format(session['id']) 
        #print(sql)
        #sql = "CREATE TABLE novaprova (nova VARCHAR(200), prova VARCHAR(200))"
        cursor.execute(sql)
        definicions = cursor.fetchall()
        print(definicions)
        definicionsordenades=sorted(definicions, key=itemgetter(1))
        print(definicionsordenades)
        ultimesparaules = definicions[-4:]
        print(ultimesparaules)
        ultimesalreves = []
        for ultimaparaula in ultimesparaules:
            ultimes = ultimaparaula[1]
            ultimesalreves.append(ultimes)
        ultimesalreves.reverse()
        #print(ultimes)
        #print(ultimesalreves)


        #ultimesparaules.reverse()
        totalparaules = len(definicions)
        #print(totalparaules)
        #print(definicions)
        #con.commit()
        con.close()
        #print(sql)

        return render_template("diccionari.html", definicions=definicionsordenades , totalparaules=totalparaules, ultimesalreves=ultimesalreves)
    
    return redirect(url_for ('login'))

@app.route('/diccionariaudios', methods=['GET','POST'])
def consultaraudios():

    if 'loggedin' in session:

        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM diccionari WHERE id_usuari = '{0}' ".format(session['id']) 
        cursor.execute(sql)
        definicions = cursor.fetchall()
        #print(definicions)
        
        #print(definicionsordenades)
        ultimesparaules = definicions[-4:]
        #print(ultimesparaules)
        ultimesalreves = []
        for ultimaparaula in ultimesparaules:
            ultimes = ultimaparaula[1]
            ultimesalreves.append(ultimes)
        ultimesalreves.reverse()
        #print(ultimes)
        #print(ultimesalreves)

        nomesambaudios = []
        for definicio in definicions:
            if definicio[3] != '':
                nomesambaudios.append(definicio)

        print(nomesambaudios)

        definicionsordenades=sorted(nomesambaudios, key=itemgetter(1))

        #ultimesparaules.reverse()
        totalparaules = len(nomesambaudios)
        #print(totalparaules)
        #print(definicions)
        #con.commit()
        con.close()
        #print(sql)


        return render_template("diccionariaudios.html", definicions=definicionsordenades , totalparaules=totalparaules, ultimesalreves=ultimesalreves)

    return redirect(url_for ('login'))

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_file_img(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS_IMG

def allowed_size(filename):
    sizefile = os.stat('filename').st_size
    return sizefile
    
@app.route('/afegir',methods=['GET','POST'])    
def afegir():

    if 'loggedin' in session:
        if request.method == 'POST':

            if 'audio' not in request.files:
                #print(id)
                flash('No hay opción para enviar archivos')
                return redirect(url_for('formulari'))

            arxiu = request.files['audio']
            #print(arxiu)
            if arxiu.filename == '':

                quediu = request.form['quediu'].capitalize().strip()
                quevoldir = request.form['quevoldir'].capitalize().strip()
                quediu = quediu.replace("'","´") 
                quevoldir = quevoldir.replace("'","´") 
                print(quediu)
                print(quevoldir)

                con = connectDatabase()
                cursor = con.cursor()
                sql = "INSERT INTO diccionari (quediu, quevoldir, id_usuari) VALUES ('{0}','{1}', '{2}')".format(quediu, quevoldir, session['id'])
                #sql = "CREATE TABLE novaprova (nova VARCHAR(200), prova VARCHAR(200))"
                print(sql)
                cursor.execute(sql)
                print(cursor)
                con.commit()
                con.close()

                '''conn = mysql.connect() 
                cursor = mysql.get_db().cursor()
                cursor.execute(INSERT INTO diccionari (quediu, quevoldir) VALUES (%s, %s),(quediu, quevoldir))
                                                
                conn.commit()
                cursor.close()'''
                
                '''diccionari= open('diccionari.txt', 'a')
                diccionari.write(quevoldir + ';' + quediu + ';' + '_' + '\n')
                diccionari.close()
                print(quediu)
                print(quevoldir)'''



                flash('Palabra añadida '+ ' ' + quediu + ': '+ quevoldir + '. Sin audio')
                #print(arxiu.filename)
                print('sense arxiu')


                return redirect(url_for('consultar'))
            
            if arxiu and allowed_file(arxiu.filename):

                quediu = request.form['quediu'].capitalize().strip()
                quevoldir = request.form['quevoldir'].capitalize().strip()
                quediu = quediu.replace("'","´") 
                quevoldir = quevoldir.replace("'","´") 
                
                print(arxiu)
                #renombrem l'arxiu original sumant-li el temps de creació (en segons) perquè tingui un nom únic
                data = str(datetime.now())
                arxiusegur = secure_filename(quediu + '_' + quevoldir + '_' + data + '_' + arxiu.filename)
                
                print(arxiu.filename)
                print(arxiusegur)
                arxiu.save(os.path.join(UPLOAD_FOLDER,arxiusegur))

                #rennombre l'arxiu segur original sumant-li el temps de creació (en segons) perquè tingui un nom únic
                '''arxiusensetemps = './audios/arxiusegur'
                print(arxiusensetemps)
                arxiuambtemps = arxiusegur + os.path.getctime('./audios/arxiusegur')
                os.rename(arxiusensetemps,arxiuambtemps)'''

                


                con = connectDatabase()
                cursor = con.cursor()
                sql = "INSERT INTO diccionari (quediu, quevoldir, arxiu, id_usuari) VALUES ('{0}','{1}','{2}','{3}')".format(quediu, quevoldir, arxiusegur, session['id'])
                #sql = "CREATE TABLE novaprova (nova VARCHAR(200), prova VARCHAR(200))"
                cursor.execute(sql)
                con.commit()
                con.close()
                
                '''quediu=quediu.replace(' ',('_'))
                quevoldir=quevoldir.replace(' ',('_'))
                diccionari= open('diccionari.txt', 'a')
                diccionari.write(quevoldir + ';' + quediu + ';' + arxiusegur + '\n')
                diccionari.close()'''

                print(quediu)
                print(quevoldir)
                flash('Palabra y audio añadidos '+ ' ' + quediu + ': '+ quevoldir)
                print('correcte!')
                return redirect(url_for('consultar'))

            else:
                quediu = request.form['quediu'].capitalize().strip()        
                quevoldir = request.form['quevoldir']
                quediu = quediu.replace("'","´") 
                quevoldir = quevoldir.replace("'","´") 

                flash('Formato no admitido. Debe ser .mp3, .wav, .aac, .wav, .ogg, .oga o .opus')
                return render_template('formulari.html', quediu=quediu, quevoldir=quevoldir)
            
            
        return redirect(url_for('formulari'))

    return redirect(url_for ('login'))

@app.route('/audios/<arxiusegur>')
def get_file(arxiusegur):
    if 'loggedin' in session:
        return send_from_directory(UPLOAD_FOLDER, arxiusegur)
        #return send_from_directory("../yahabla/audios", arxiusegur)
    return redirect(url_for ('login'))

@app.route('/images/<fotosegura>')
def get_file_img(fotosegura):
    if 'loggedin' in session:
        return send_from_directory(UPLOAD_FOLDER_IMG, fotosegura)
        #return send_from_directory("../yahabla/images", fotosegura)     
    return redirect(url_for ('login'))

@app.route('/confirmareliminar/<id>')
def confirmareliminar(id):
    if 'loggedin' in session:
        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM diccionari WHERE ID = {0}".format(id)
        print(sql)
        #sql = "INSERT INTO diccionari (quediu, quevoldir, arxiu) VALUES ('{0}','{1}','{2}')".format(quediu, quevoldir, arxiusegur)
        #sql = "CREATE TABLE novaprova (nova VARCHAR(200), prova VARCHAR(200))"
        cursor.execute(sql)
        id2 = cursor.fetchall()
        print(id2)
        id3=id2[0]
        print(id3)
        id4=id3[2]
        print(id4)
        con.commit()
        con.close()

        flash(id4)
        return render_template("confirmacio.html", id = id)
    return redirect(url_for ('login'))

@app.route('/eliminar/<id>')
def eliminar(id):

    if 'loggedin' in session:
        print(id)

        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM diccionari WHERE ID = {0}".format(id)
        print(sql)
        cursor.execute(sql)
        id2 = cursor.fetchall()
        print(id2)
        id3=id2[0]
        print(id3)
        id4=id3[3]
        print(id4)
        #sql = "INSERT INTO diccionari (quediu, quevoldir, arxiu) VALUES ('{0}','{1}','{2}')".format(quediu, quevoldir, arxiusegur)
        #sql = "CREATE TABLE novaprova (nova VARCHAR(200), prova VARCHAR(200))"
        con.commit()
        con.close()

        #esborrar l'arxiu de la carpeta 'audios'
        # File location
        '''location = "audios"'''
        # Path
        if id4 != '':
            path = os.path.join(UPLOAD_FOLDER, id4)
            # Remove the file
            # 'file.txt'
            os.remove(path)

        
        con = connectDatabase()
        cursor = con.cursor()
        sql = "DELETE FROM diccionari WHERE ID = {0}".format(id)
        #print(sql)
        #sql = "INSERT INTO diccionari (quediu, quevoldir, arxiu) VALUES ('{0}','{1}','{2}')".format(quediu, quevoldir, arxiusegur)
        #sql = "CREATE TABLE novaprova (nova VARCHAR(200), prova VARCHAR(200))"
        cursor.execute(sql)
        con.commit()
        con.close()

        

        flash('Palabra eliminada')
        return redirect(url_for('consultar'))
        
    return redirect(url_for ('login'))
        
@app.route('/editar/<id>')
def editar(id):

    if 'loggedin' in session:
        print(id)


        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM diccionari WHERE ID = {0}".format(id)
        #print(sql)
        cursor.execute(sql)
        editar = cursor.fetchall()
        #print(editar)
        editar = editar[0]
        quevoldir = editar[2]
        quediu = editar[1]
        arxiu = editar[3]
        #sql = "INSERT INTO diccionari (quediu, quevoldir, arxiu) VALUES ('{0}','{1}','{2}')".format(quediu, quevoldir, arxiusegur)
        #sql = "CREATE TABLE novaprova (nova VARCHAR(200), prova VARCHAR(200))"
        cursor.execute(sql)
        con.commit()
        con.close()
        
        return render_template('editar.html', quediu = quediu , quevoldir = quevoldir, arxiu = arxiu, id=id)
        #return 'ok'
    return redirect(url_for ('login'))

@app.route('/editar/<id>', methods=['POST'])
def actualitzar(id):
    if 'loggedin' in session:    
        #print(id)
        if request.method == 'POST':

            if 'audio' not in request.files:
                print('holahola')
                quediu = request.form['quediu'].capitalize().strip()
                quevoldir = request.form['quevoldir'].capitalize().strip()
                quediu = quediu.replace("'","´") 
                quevoldir = quevoldir.replace("'","´") 
                
                con = connectDatabase()
                cursor = con.cursor()
                sql = "UPDATE diccionari SET quediu = '{0}', quevoldir = '{1}' WHERE ID = {2}".format(quediu, quevoldir, id)
                print(sql)
                #sql = "INSERT INTO diccionari (quediu, quevoldir, arxiu) VALUES ('{0}','{1}','{2}')".format(quediu, quevoldir, arxiusegur)
                #sql = "CREATE TABLE novaprova (nova VARCHAR(200), prova VARCHAR(200))"
                cursor.execute(sql)
                con.commit()
                con.close()
                flash('Palabra modificada')
                

                return redirect(url_for('consultar'))
            



            arxiu = request.files['audio']
            print(arxiu)
            if arxiu.filename == '':
                print('hola')
                quediu = request.form['quediu'].capitalize().strip()
                quevoldir = request.form['quevoldir'].capitalize().strip()
                quediu = quediu.replace("'","´") 
                quevoldir = quevoldir.replace("'","´") 

                con = connectDatabase()
                cursor = con.cursor()
                sql = "UPDATE diccionari SET quediu = '{0}', quevoldir = '{1}' WHERE ID = {2}".format(quediu, quevoldir, id)
                print(sql)
                #sql = "INSERT INTO diccionari (quediu, quevoldir, arxiu) VALUES ('{0}','{1}','{2}')".format(quediu, quevoldir, arxiusegur)
                #sql = "CREATE TABLE novaprova (nova VARCHAR(200), prova VARCHAR(200))"
                cursor.execute(sql)
                con.commit()
                con.close()
                flash('Palabra modificada')

                return redirect(url_for('consultar'))
            
            if arxiu and allowed_file(arxiu.filename):
                #renombrem l'arxiu original sumant-li el temps de creació (en segons) perquè tingui un nom únic
                data = str(datetime.now())
                arxiusegur = secure_filename(data + '_' + arxiu.filename)
                
                #print(arxiu.filename)
                #print(arxiusegur)
                arxiu.save(os.path.join(app.config['UPLOAD_FOLDER'],arxiusegur))
                
                quediu = request.form['quediu'].capitalize().strip()
                quevoldir = request.form['quevoldir'].capitalize().strip()
                quediu = quediu.replace("'","´") 
                quevoldir = quevoldir.replace("'","´") 
                
                con = connectDatabase()
                cursor = con.cursor()
                sql = "UPDATE diccionari SET quediu = '{0}', quevoldir = '{1}', arxiu = '{2}' WHERE ID = {3}".format(quediu, quevoldir, arxiusegur, id)
                print(sql)
                #sql = "INSERT INTO diccionari (quediu, quevoldir, arxiu) VALUES ('{0}','{1}','{2}')".format(quediu, quevoldir, arxiusegur)
                #sql = "CREATE TABLE novaprova (nova VARCHAR(200), prova VARCHAR(200))"
                cursor.execute(sql)
                con.commit()
                con.close()
                
                flash('Palabra y audio modificados')
            

                return redirect(url_for('consultar'))


            else:
                quediu = request.form['quediu'].capitalize().strip()        
                quevoldir = request.form['quevoldir']
                quediu = quediu.replace("'","´") 
                quevoldir = quevoldir.replace("'","´") 

                flash('Format no admitido. Debe ser .mp3, .wav, .aac, .ogg, .oga, .opus o .wav')
                return render_template('formulari.html', quediu=quediu, quevoldir=quevoldir)
            
            
        return redirect(url_for('diccionari'))

    return redirect(url_for ('login'))

@app.route('/eliminaraudio/<string:id>' , methods = ['GET','POST'])
def eliminaraudio(id):
    if 'loggedin' in session:
        print(id)

        con = connectDatabase()
        cursor = con.cursor()
        sql = "UPDATE diccionari SET arxiu = '{0}' WHERE arxiu = '{1}'".format('', id)
        print(sql)
        #sql = "INSERT INTO diccionari (quediu, quevoldir, arxiu) VALUES ('{0}','{1}','{2}')".format(quediu, quevoldir, arxiusegur)
        #sql = "CREATE TABLE novaprova (nova VARCHAR(200), prova VARCHAR(200))"
        cursor.execute(sql)
        con.commit()
        con.close()
    
        #esborrar l'arxiu de la carpeta 'audios'
        # File location
        '''location = "audios"'''
        # Path
        path = os.path.join(UPLOAD_FOLDER, id)
        # Remove the file
        os.remove(path)
        
        print("%s s'ha esborrat" %id)


        flash('Audio eliminado')
        
        return redirect(url_for('consultar'))
        #return render_template('formulari.html', quediu=quediu, quevoldir=quevoldir, arxiu=editar3)
    
    return redirect(url_for ('login'))

@app.route('/joc')
def joc():
    if 'loggedin' in session:


        #nom del nen
        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM infokid WHERE id_kid = '{0}' ".format(session['id']) 
        cursor.execute(sql)
        nomnen = cursor.fetchone()
        con.close()

        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM diccionari WHERE id_usuari = '{0}' ".format(session['id']) 
        cursor.execute(sql)
        definicions = cursor.fetchall()
        con.close()

        #print(definicions)
        #print(definicions[1])

        llistanomsmarti=[]
        diccionarideltxt={}

        for definicio in definicions:
            #print(definicio[1])
            diccionarideltxt[definicio[1]] = definicio[3]
        #print(llistanomsmarti)  
        print(diccionarideltxt)
        totalparaules = len(llistanomsmarti)
        #print(definicions)
        #print(llistanomsmarti)

        llistanomsmarti = list(diccionarideltxt.keys())
        print(llistanomsmarti)
        #llistaarxius = list(diccionarideltxt.values())
        totalparaules = len(llistanomsmarti)
        #print(totalparaules)

        if totalparaules == 0:
            return render_template('joc.html', totalparaules=totalparaules)

        aleatori = random.choice(llistanomsmarti)
        #print(diccionarideltxt)
        print(aleatori)

        global diccionarisenserepetits
        diccionarisenserepetits = []
    
        if aleatori in diccionarideltxt:
            print('ok')
            arxiualeatori = diccionarideltxt[aleatori]
        print(arxiualeatori)
        marcador = 0
        compteenrere = 5
        diccionarisenserepetits.append(aleatori)
        print(marcador)
        print(compteenrere)

        
        return render_template('joc.html', aleatori=aleatori, arxiualeatori=arxiualeatori, marcador=marcador, compteenrere=compteenrere, totalparaules=totalparaules)
    return redirect(url_for ('login'))

@app.route('/joc', methods=['POST'])
def jugant():
    if 'loggedin' in session:

        #nom del nen
        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM infokid WHERE id_kid = '{0}' ".format(session['id']) 
        cursor.execute(sql)
        nomnen = cursor.fetchone()
        con.close()

        if request.method == 'POST':
            quevoldir = request.form['quevoldir'].capitalize().strip()
            print(quevoldir)
            #quevoldir=quevoldir.replace(' ',('_'))
            marcador = request.form['marcador']
            compteenrere = request.form['compteenrere']
            aleatori = request.form['aleatori']
            
        #print(marcador)
        #print(compteenrere
        #diccionarisenserepetits.append(aleatori)
        llistanomsbons = []
        diccionarideltxt = {}
        


        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT quevoldir FROM diccionari WHERE id_usuari = '{0}' and quediu = '{1}' ".format(session['id'], aleatori) 
        cursor.execute(sql)
        respostacorrecta = cursor.fetchone()
        con.close()
        #print(respostacorrecta[0])

    

        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM diccionari WHERE id_usuari = '{0}' ".format(session['id']) 
        cursor.execute(sql)
        definicions = cursor.fetchall()
        con.close()

        for definicio in definicions:
            #print(definicio[1])
            diccionarideltxt[definicio[1]] = definicio[3]
            llistanomsbons.append(definicio[2])
        #print(llistanomsmarti)  
        #print(diccionarideltxt)
        llistanomsmarti = list(diccionarideltxt.keys())
        #llistaarxius = list(diccionarideltxt.values())
        totalparaules = len(llistanomsmarti)

        #print(llistanomsbons)
        #print(llistaquevoldir)

        if quevoldir == respostacorrecta[0]:
            print(quevoldir)
            print(respostacorrecta[0])
            print('Correcte!')
            flash('¡Correcto!')
            marcador = int(marcador) + 1
        else:
            print('No és correcte!')
            flash('¡No es correcto!')

        compteenrere = int(compteenrere) - 1    
        
        
        validacio = False

        while validacio == False:
            aleatori = random.choice(llistanomsmarti)
            if aleatori in diccionarisenserepetits:
                validacio = False
            else:
                
                diccionarisenserepetits.append(aleatori)
                print(diccionarisenserepetits)
                validacio = True
        print(marcador)    
        print(compteenrere)
        if aleatori in diccionarideltxt:
            arxiualeatori = diccionarideltxt[aleatori]
        print(arxiualeatori)
        
        return render_template('joc.html', aleatori=aleatori, arxiualeatori=arxiualeatori, marcador=marcador, compteenrere=compteenrere, totalparaules=totalparaules)

    return redirect(url_for ('login'))

@app.route('/calaix', methods=['GET','POST'])
def calaix():
    if 'loggedin' in session:   

        if request.method == 'POST':

            if 'audio' not in request.files:
                #print(id)
                flash('No hay opción para enviar archivos')
                return redirect(url_for('calaix'))

            arxiu = request.files['audio']
            #print(arxiu)
            
            if arxiu and allowed_file(arxiu.filename):
                
                #renombrem l'arxiu original sumant-li el temps de creació (en segons) perquè tingui un nom únic
                data = str(datetime.now())
                arxiusegur = secure_filename(data + '_' + arxiu.filename)

                print(arxiu.filename)
                print(arxiusegur)
                arxiu.save(os.path.join(app.config['UPLOAD_FOLDER'],arxiusegur))
                
                descripcio = request.form['descripcio'].capitalize().strip()

                con = connectDatabase()
                cursor = con.cursor()
                sql = "INSERT INTO calaix (descripcio, arxiu, id_usuaricalaix) VALUES ('{0}','{1}','{2}')".format(descripcio, arxiusegur, session['id'])
                cursor.execute(sql)
                con.commit()
                con.close()

                print(descripcio)
                flash('Descripción y audio añadidos '+ ' ' + descripcio)
                print('correcte!')
                return redirect(url_for('calaix'))

            else:
                descripcio = request.form['descripcio'].capitalize().strip()

                flash('Formato no admitido. Debe ser .mp3, .wav, .aac, .wav, .ogg, .oga o .opus')
                return render_template('calaix.html', descripcio=descripcio)
            
        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM calaix WHERE id_usuaricalaix = '{0}' ".format(session['id'])
        #sql = "CREATE TABLE novaprova (nova VARCHAR(200), prova VARCHAR(200))"
        cursor.execute(sql)
        definicions = cursor.fetchall()
        definicions=sorted(definicions, key=itemgetter(1))
        con.close()


        return render_template("calaix.html" , definicions=definicions)

    return redirect(url_for ('login'))

@app.route('/confirmareliminarcalaix/<string:id>')
def confirmareliminarcalaix(id):

    if 'loggedin' in session:   
        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM calaix WHERE ID = {0}".format(id)
        print(sql)
        cursor.execute(sql)
        id2 = cursor.fetchall()
        print(id2)
        id3=id2[0]
        print(id3)
        id4=id3[1]
        print(id4)
        #sql = "INSERT INTO diccionari (quediu, quevoldir, arxiu) VALUES ('{0}','{1}','{2}')".format(quediu, quevoldir, arxiusegur)
        #sql = "CREATE TABLE novaprova (nova VARCHAR(200), prova VARCHAR(200))"
        con.commit()
        con.close()

        flash(id)
        return render_template("confirmaciocalaix.html", id4=id4)

    return redirect(url_for ('login'))

@app.route('/eliminarcalaix/<string:id>')
def eliminarcalaix(id):
    if 'loggedin' in session:   
        #print(id)

        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM calaix WHERE ID = {0}".format(id)
        print(sql)
        cursor.execute(sql)
        id2 = cursor.fetchall()
        print(id2)
        id3=id2[0]
        print(id3)
        id4=id3[2]
        print(id4)
        #sql = "INSERT INTO diccionari (quediu, quevoldir, arxiu) VALUES ('{0}','{1}','{2}')".format(quediu, quevoldir, arxiusegur)
        #sql = "CREATE TABLE novaprova (nova VARCHAR(200), prova VARCHAR(200))"
        con.commit()
        con.close()

        #esborrar l'arxiu de la carpeta 'audios'
        # File location
        '''location = "audios"'''
        # Path
        if id4 != '':
            path = os.path.join(UPLOAD_FOLDER, id4)
            # Remove the file
            # 'file.txt'
            os.remove(path)
        
        con = connectDatabase()
        cursor = con.cursor()
        sql = "DELETE FROM calaix WHERE ID = {0}".format(id)
        print(sql)
        #sql = "INSERT INTO diccionari (quediu, quevoldir, arxiu) VALUES ('{0}','{1}','{2}')".format(quediu, quevoldir, arxiusegur)
        #sql = "CREATE TABLE novaprova (nova VARCHAR(200), prova VARCHAR(200))"
        cursor.execute(sql)
        con.commit()
        con.close()

        flash('Palabra eliminada')
        return redirect(url_for('calaix'))
    return redirect(url_for ('login'))

@app.route('/signup', methods=['GET','POST'])   
def signup():
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['pwd']
        print(pwd)
        pwd2 = request.form['pwd2']
        print(pwd2)

        if len(email) < 1:
            flash('Introduce un email y una contraseña')
            return render_template("signup.html", email=email)

        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT email from usuaris"
        print(sql)
        cursor.execute(sql)
        llistaemails = cursor.fetchall()
        print(llistaemails)
        con.commit()
        con.close()



        for repe in llistaemails:
            #print('hola')
            print(repe[0])
            print(email)
            if repe[0] == email:
                print('Aquest usuari ja existeix')
                flash('Este usuario ya existe')
                return render_template("signup.html")
                
        
        if pwd != pwd2:
            print('hola')
            flash('Las contraseñas no coinciden')
            return render_template("signup.html", email=email)
        
        else:

            validar=False #que se vayan cumpliendo los requisitos uno a uno.
            long=len(pwd)  #Calcula la longitud de la contraseña
            espacio=False #variable para identificar espacios
            mayuscula=False #variable para identificar letras mayúsculas
            minuscula=False #variable para identificar letras minúsculas
            numeros=False #variable para identificar números
            correcto=True #verifica que hayan mayuscula, minuscula y numeros

            for carac in pwd: #ciclo for que recorre caracter por caracter en la contraseña
                if carac.isspace() == True:
                    espacio=True

                if carac.isupper() == True: #saber si hay mayuscula
                    mayuscula = True #acumulador o contador de mayusculas
                    
                if carac.islower() == True: #saber si hay minusculas
                    minuscula = True #acumulador o contador de minusculas

                if carac.isdigit() == True: #saber si hay números
                    numeros = True #acumulador o contador de numeros
            
            if espacio == True: #hay espacios en blanco
                print('No pot tenir espais en blanc')
                flash('No puede tener espacios en blanco')
                return render_template("signup.html", email=email)
                        
            else:
                validar = True

            if long < 8 or long >16 and validar == True:
                print('La contrasenya ha de tenir entre 8 i 16 caràcters')
                validar = False #cambia a False si no se cumple el requisito móinimo de caracteres
                flash('La contraseña debe tener entre 8 y 16 caracteres')
                return render_template("signup.html", email=email)
                                
            if mayuscula == True and minuscula == True and numeros == True and validar == True:
                validar = True #Cumple el requisito de tener mayuscula, minuscula, numeros 
            else:
                correcto= False #uno o mas requisitos de mayuscula, minuscula, numeros y no alfanuméricos no se cumple
            
            if validar == True and correcto == False:
                print("La contraseña escollida no és segura: ha de tenir lletres minúsculas, majúsculas i números")
                flash("La contraseña escogida no es segura: debe tener letras minúsculas, mayúsculas y números")
                return render_template("signup.html", email=email)

            if validar == True and correcto == True:
                #introdueix a la base de dades email i pwd validats
                pwdhash = generate_password_hash(pwd)
                print(pwdhash)
                con = connectDatabase()
                cursor = con.cursor()
                sql = "INSERT INTO usuaris (email, pwd) VALUES ('{0}','{1}')".format(email, pwdhash)
                #sql = "CREATE TABLE novaprova (nova VARCHAR(200), prova VARCHAR(200))"
                print(sql)
                cursor.execute(sql)
                print(cursor)
                con.commit()
                con.close()


                #corrobora que email i pwd estan a la base de dades i crea una sessió
                print(pwdhash)
                print(pwd)
                con = connectDatabase()
                cursor = con.cursor()
                sql = "SELECT * FROM usuaris WHERE email = '{0}' and pwd = '{1}'".format(email,pwdhash)
                cursor.execute(sql)
                account=cursor.fetchone()
                print(account)
                con.close()
                # If account exists in accounts table in out database
                if account:
                    # Create session data, we can access this data in other routes
                    session['loggedin'] = True
                    session['id'] = account[0]
                    session['email'] = account[1]
                    # Redirect to home page
                    flash('¡Bienvenido!')
                    return render_template('inici.html')


    return render_template ("signup.html")

@app.route('/login', methods=['GET','POST'])   
def login():
    
    if request.method == 'POST':
        if 'email' in request.form and 'pwd' in request.form:
            print('hola')
            email = request.form['email']
            pwd = request.form['pwd']
            print(email)
            print(pwd)
            

            con = connectDatabase()
            cursor = con.cursor()
            sql = "SELECT * FROM usuaris WHERE email = '{0}'".format(email)
            #sql = "SELECT * FROM usuaris WHERE email = '{0}' and pwd = '{1}'".format(email,pwd)
            cursor.execute(sql)
            account=cursor.fetchone()
            con.close()
            print(account)
            print(pwd)
            if account:
                # If account exists in accounts table in out database
                check_pwd = check_password_hash(account[2],pwd)
                # if pwd hashed matches with pwd in form
                print('cuenta')

                if check_pwd == True:
                    print('Veritat')
                    # Create session data, we can access this data in other routes
                    session['loggedin'] = True
                    session['id'] = account[0]
                    session['email'] = account[1]
                    # Redirect to home page
                    '''flash('¡Bienvenido!')'''
                    return render_template('inici.html')
                flash('Email o contraseña incorrectas')
                return render_template('login.html')
                
            else:
                # Account doesnt exist or username/password incorrect
                flash('Email o contraseña incorrectas')
                return render_template('login.html')

        return render_template ("login.html")
    return render_template ("login.html")
        
@app.route('/profile', methods=['GET','POST'])
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:

        #mirem si hi ha una fila creada (per haver penjat foto abans que nom)
        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM infokid WHERE id_kid = '{0}' ".format(session['id']) 
        cursor.execute(sql)
        nomnen=cursor.fetchone()
        con.close()

        if request.method == 'POST':
            print('hola')
            kidname = request.form['kidname']
            #si s'envia el formulari del nom del nen, l'introduim a la base de dades, a una fila nova
            if not nomnen:
                con = connectDatabase()
                cursor = con.cursor()
                sql = "INSERT INTO infokid (kidname, id_kid) VALUES ('{0}','{1}')".format(kidname, session['id'])
                print(sql)
                cursor.execute(sql)
                con.commit()
                con.close()

             #si s'envia el formulari del nom del nen, l'introduim a la base de dades, a una fila ja existent
            else:
                con = connectDatabase()
                cursor = con.cursor()
                sql = "UPDATE infokid SET kidname = '{0}' WHERE kidname = '{1}'".format(kidname,nomnen[1])
                print(sql)
                cursor.execute(sql)
                con.commit()
                con.close()


        # We need all the account info for the user so we can display it on the profile page
        #primer aconseguim les dades del compte d'usuari (no les del nen)
        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM usuaris WHERE IDusuari = '{0}' ".format(session['id']) 
        cursor.execute(sql)
        account=cursor.fetchone()
        con.close()

        #després aconseguim les dades del nen
        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM infokid WHERE id_kid = '{0}' ".format(session['id']) 
        cursor.execute(sql)
        nomnen=cursor.fetchone()
        con.close()

        
        return render_template('profile.html', account=account, nomnen=nomnen)



    # if User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/profile/editname', methods=['GET','POST'])
def editname():
    # Check if user is loggedin
    if 'loggedin' in session:
        

        # We need all the account info for the user so we can display it on the profile page
        #primer aconseguim les dades del compte d'usuari (no les del nen)
        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM usuaris WHERE IDusuari = '{0}' ".format(session['id']) 
        cursor.execute(sql)
        account=cursor.fetchone()
        con.close()

        #després aconseguim les dades del nen
        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM infokid WHERE id_kid = '{0}' ".format(session['id']) 
        cursor.execute(sql)
        nomnen=cursor.fetchone()
        con.close()

        #actualitzem el nom del nen
        if request.method == 'POST':
            print('hola')
            #si s'envia el formulari del nom del nen, l'introduim a la base de dades
            kidname = request.form['kidname']
            con = connectDatabase()
            cursor = con.cursor()
            sql = "UPDATE infokid SET kidname = '{0}' WHERE kidname = '{1}'".format(kidname,nomnen[1])
            print(sql)
            cursor.execute(sql)
            con.commit()
            con.close()

            #tornem a carregar el 'nomnen' amb el nou nom del nen
            con = connectDatabase()
            cursor = con.cursor()
            sql = "SELECT * FROM infokid WHERE id_kid = '{0}' ".format(session['id']) 
            cursor.execute(sql)
            nomnen=cursor.fetchone()
            con.close()
            print(nomnen)
            return render_template('profile.html', account=account, nomnen=nomnen)
        
        #tornem a carregar el 'nomnen' amb el nou nom del nen
        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM infokid WHERE id_kid = '{0}' ".format(session['id']) 
        cursor.execute(sql)
        nomnen=cursor.fetchone()
        con.close()
        print(nomnen)
        

        return render_template('editname.html', account=account, nomnen=nomnen)

@app.route('/profile/photo', methods=['GET','POST'])
def uploadphoto():
    if request.method == 'POST':
        #si s'envia el formulari de la foto amb l'arxiu, l'introduim a la base de dades
        foto = request.files['foto']
        if foto and allowed_file_img(foto.filename):

            #read image
            '''location = "images"'''
            imgresize = Image.open(foto)
            print(imgresize.size)

            #image size
            '''size=(300,300)
            #resize image
            imgresize.thumbnail(size, Image.ANTIALIAS)

            #save resized image
            data = str(datetime.now())
            fotosegura= secure_filename(data + '_' + foto.filename)
            imgresize.save(os.path.join(UPLOAD_FOLDER_IMG,fotosegura))'''


            basewidth = 250
            img = Image.open(foto)
            wpercent = (basewidth/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img = img.resize((basewidth,hsize), Image.ANTIALIAS)
            data = str(datetime.now())
            fotosegura= secure_filename(data + '_' + foto.filename)
            img.save(os.path.join(UPLOAD_FOLDER_IMG,fotosegura))


            #després aconseguim les dades del nen
            con = connectDatabase()
            cursor = con.cursor()
            sql = "SELECT * FROM infokid WHERE id_kid = '{0}' ".format(session['id']) 
            cursor.execute(sql)
        
            nomnen=cursor.fetchone()
            con.close()

            #i actualitzem la foto a la base de dades
            if nomnen:
                con = connectDatabase()
                cursor = con.cursor()
                sql = "UPDATE infokid SET kidphoto = '{0}' WHERE kidphoto = '{1}'".format(fotosegura,nomnen[2])
                print(sql)
                cursor.execute(sql)
                con.commit()
                con.close()
                return redirect(url_for('profile'))
            
            else:
                con = connectDatabase()
                cursor = con.cursor()
                sql = "INSERT INTO infokid (kidphoto, id_kid) VALUES ('{0}','{1}')".format(fotosegura, session['id'])
                print(sql)
                cursor.execute(sql)
                con.commit()
                con.close()
                return redirect(url_for('profile'))
    
        flash('Formato no admitido. Debe ser jpg, png o tiff')
    return render_template('photo.html')

@app.route('/profile/deletephoto' , methods = ['GET','POST'])
def deletephoto():
    if 'loggedin' in session:

        #primer aconseguim les dades del nen
                    
        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM infokid WHERE id_kid = '{0}' ".format(session['id']) 
        cursor.execute(sql)
        nomnen=cursor.fetchone()
        con.close()

        con = connectDatabase()
        cursor = con.cursor()
        sql = "UPDATE infokid SET kidphoto = '{0}' WHERE kidphoto = '{1}'".format('', nomnen[2])
        print(sql)
        #sql = "INSERT INTO diccionari (quediu, quevoldir, arxiu) VALUES ('{0}','{1}','{2}')".format(quediu, quevoldir, arxiusegur)
        #sql = "CREATE TABLE novaprova (nova VARCHAR(200), prova VARCHAR(200))"
        cursor.execute(sql)
        con.commit()
        con.close()
    
        #esborrar l'arxiu de la carpeta 'images'
        # File location
        '''location = "images"'''
        # Path
        path = os.path.join(UPLOAD_FOLDER_IMG, nomnen[2])
        # Remove the file
        os.remove(path)
        
        print("%s s'ha esborrat" %nomnen[2])


        flash('Foto eliminada')
        
        return redirect(url_for('profile'))
        #return render_template('formulari.html', quediu=quediu, quevoldir=quevoldir, arxiu=editar3)
    
    return redirect(url_for ('login'))


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('email', None)
    session.pop('pwd', None)

    return redirect(url_for('login'))

@app.route('/canvipwd',methods=['GET','POST'])
def canvipwd():
    if 'loggedin' in session:
        if request.method == 'POST':
            
            pwdactual = request.form['pwdactual']
            noupwd = request.form['noupwd']
            noupwd2 = request.form['noupwd2']
            
            con = connectDatabase()
            cursor = con.cursor()
            sql = "SELECT * FROM usuaris WHERE IDusuari = '{0}'".format(session['id'])
            #sql = "SELECT * FROM usuaris WHERE email = '{0}' and pwd = '{1}'".format(email,pwd)
            cursor.execute(sql)
            account=cursor.fetchone()
            con.close()
            print(account)
            print(pwdactual)
            
            # If account exists in accounts table in out database
            check_pwd = check_password_hash(account[2],pwdactual)
            # if pwd hashed matches with pwd in form
            print(check_pwd)
            
            
            
            if check_pwd == True:
                if noupwd != noupwd2:
                    flash('Las contraseñas no coinciden')
                    return render_template("canvipwd.html")
                else:

                    validar=False #que se vayan cumpliendo los requisitos uno a uno.
                    long=len(noupwd)  #Calcula la longitud de la contraseña
                    espacio=False #variable para identificar espacios
                    mayuscula=False #variable para identificar letras mayúsculas
                    minuscula=False #variable para identificar letras minúsculas
                    numeros=False #variable para identificar números
                    correcto=True #verifica que hayan mayuscula, minuscula y numeros

                    for carac in noupwd: #ciclo for que recorre caracter por caracter en la contraseña
                        if carac.isspace() == True:
                            espacio=True

                        if carac.isupper() == True: #saber si hay mayuscula
                            mayuscula = True #acumulador o contador de mayusculas
                            
                        if carac.islower() == True: #saber si hay minusculas
                            minuscula = True #acumulador o contador de minusculas

                        if carac.isdigit() == True: #saber si hay números
                            numeros = True #acumulador o contador de numeros
                    
                    if espacio == True: #hay espacios en blanco
                        print('No pot tenir espais en blanc')
                        flash('No puede tener espacios en blanco')
                        return render_template("canvipwd.html")
                                
                    else:
                        validar = True

                    if long < 8 or long >16 and validar == True:
                        print('La contrasenya ha de tenir entre 8 i 16 caràcters')
                        validar = False #cambia a False si no se cumple el requisito móinimo de caracteres
                        flash('La contraseña debe tener entre 8 y 16 caracteres')
                        return render_template("canvipwd.html")
                                        
                    if mayuscula == True and minuscula == True and numeros == True and validar == True:
                        validar = True #Cumple el requisito de tener mayuscula, minuscula, numeros 
                    else:
                        correcto= False #uno o mas requisitos de mayuscula, minuscula, numeros y no alfanuméricos no se cumple
                    
                    if validar == True and correcto == False:
                        print("La contraseña escollida no és segura: ha de tenir lletres minúsculas, majúsculas i números")
                        flash("La contraseña escogida no es segura: debe tener letras minúsculas, mayúsculas y números")
                        return render_template("canvipwd.html")

                    if validar == True and correcto == True:

                        pwdhash=generate_password_hash(noupwd)
                        con = connectDatabase()
                        cursor = con.cursor()
                        #actualitza la taula usuaris: afegeix el nou pwd amb hash en comptes del passwprd amb hash anterior
                        sql = "UPDATE usuaris SET pwd ='{0}' WHERE pwd = '{1}'".format(pwdhash,account[2])
                        #sql = "SELECT * FROM usuaris WHERE email = '{0}' and pwd = '{1}'".format(email,pwd)
                        cursor.execute(sql)
                        con.commit()
                        con.close()
                        #exemple
                        #sql = "UPDATE diccionari SET quediu = '{0}', quevoldir = '{1}' WHERE ID = {2}".format(quediu, quevoldir, id)
                        print('contrasenya canviada')
                        flash('Contraseña cambiada')
                        return render_template('inici.html')
                        

                    flash('Las nuevas contraseñas no coinciden')
                    return render_template('canvipwd.html')

                
            flash('La contraseña actual no es correcta')
            return render_template('canvipwd.html')


        return render_template('canvipwd.html')
    return render_template('canvipwd.html')


'''def send_quickly(app, msg):
    with app.app_context():
        mail.send(msg)'''
 
def send_mail(account):
    token = get_token()
    print(token)
    print(account[1])

    msg = Message(subject="¡Ya habla! Restablecer contraseña",sender=app.config['MAIL_USERNAME'],recipients=[account[1]])
    msg.body=f'''Para cambiar tu contraseña, clica aquí:
    
    {url_for('reset_token', token=token, _external=True)}

    Si no has pedido cambiar la contraseña, ignora este mensaje'''

    '''send=Thread(target=send_quickly, args=(app, msg))
    send.start()'''

    mail.send(msg)
    print('mail enviat2')
    
    

def get_token(expires_sec=3600):
    serial=Serializer(app.config['SECRET_KEY'], expires_in = expires_sec)
    return serial.dumps({'user_id': account[0]}).decode('utf-8')
    
def verify_token(token):
    print('hola')
    serial = Serializer(app.config['SECRET_KEY'])
    try:
        user_id = serial.loads(token)['user_id']
    except:
        return None
    
    con = connectDatabase()
    cursor = con.cursor()
    sql = "SELECT * FROM usuaris WHERE IDusuari = '{0}'".format(user_id)
    cursor.execute(sql)
    account=cursor.fetchone()
    con.close()
    return account
      
@app.route('/pwdrecovery', methods=['GET','POST'])
def pwdrecovery():
    if request.method == 'POST':
        email = request.form['email']
        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM usuaris WHERE email = '{0}'".format(email)
        #sql = "SELECT * FROM usuaris WHERE email = '{0}' and pwd = '{1}'".format(email,pwd)
        cursor.execute(sql)
        global account
        account=cursor.fetchone()
        con.close()
        
        
        if account:
            get_token()
            send_mail(account)
            print('mail enviat')
            flash('Revisa la bandeja de entrada (o la carpeta de spam)')
        else:
            flash('Este email no está registrado')
    return render_template('pwdrecovery.html')

@app.route('/pwdrecovery/<token>', methods=['GET','POST'])
def reset_token(token):
    account = verify_token(token)
    if account is None:
        flash('Enlace inválido o caducado')
        return redirect(url_for('pwdrecovery'))

        
    if request.method == 'POST':
        
        noupwd = request.form['noupwd']
        noupwd2 = request.form['noupwd2']
        
        con = connectDatabase()
        cursor = con.cursor()
        sql = "SELECT * FROM usuaris WHERE IDusuari = '{0}'".format(account[0])
        #sql = "SELECT * FROM usuaris WHERE email = '{0}' and pwd = '{1}'".format(email,pwd)
        cursor.execute(sql)
        account=cursor.fetchone()
        con.close()
        print(account)
       
        if noupwd != noupwd2:
            flash('Las contraseñas no coinciden')
            return render_template("resetpwd.html")

        else:

            validar=False #que se vayan cumpliendo los requisitos uno a uno.
            long=len(noupwd)  #Calcula la longitud de la contraseña
            espacio=False #variable para identificar espacios
            mayuscula=False #variable para identificar letras mayúsculas
            minuscula=False #variable para identificar letras minúsculas
            numeros=False #variable para identificar números
            correcto=True #verifica que hayan mayuscula, minuscula y numeros

            for carac in noupwd: #ciclo for que recorre caracter por caracter en la contraseña
                if carac.isspace() == True:
                    espacio=True

                if carac.isupper() == True: #saber si hay mayuscula
                    mayuscula = True #acumulador o contador de mayusculas
                    
                if carac.islower() == True: #saber si hay minusculas
                    minuscula = True #acumulador o contador de minusculas

                if carac.isdigit() == True: #saber si hay números
                    numeros = True #acumulador o contador de numeros
            
            if espacio == True: #hay espacios en blanco
                print('No pot tenir espais en blanc')
                flash('No puede tener espacios en blanco')
                return render_template("resetpwd.html")
                        
            else:
                validar = True

            if long < 8 or long >16 and validar == True:
                print('La contrasenya ha de tenir entre 8 i 16 caràcters')
                validar = False #cambia a False si no se cumple el requisito móinimo de caracteres
                flash('La contraseña debe tener entre 8 y 16 caracteres')
                return render_template("resetpwd.html")
                                
            if mayuscula == True and minuscula == True and numeros == True and validar == True:
                validar = True #Cumple el requisito de tener mayuscula, minuscula, numeros 
            else:
                correcto= False #uno o mas requisitos de mayuscula, minuscula, numeros y no alfanuméricos no se cumple
            
            if validar == True and correcto == False:
                print("La contraseña escollida no és segura: ha de tenir lletres minúsculas, majúsculas i números")
                flash("La contraseña escogida no es segura: debe tener letras minúsculas, mayúsculas y números")
                return render_template("resetpwd.html")

            if validar == True and correcto == True:

                pwdhash=generate_password_hash(noupwd)
                con = connectDatabase()
                cursor = con.cursor()
                #actualitza la taula usuaris: afegeix el nou pwd amb hash en comptes del passwprd amb hash anterior
                sql = "UPDATE usuaris SET pwd ='{0}' WHERE pwd = '{1}'".format(pwdhash,account[2])
                #sql = "SELECT * FROM usuaris WHERE email = '{0}' and pwd = '{1}'".format(email,pwd)
                cursor.execute(sql)
                con.commit()
                con.close()
                #exemple
                #sql = "UPDATE diccionari SET quediu = '{0}', quevoldir = '{1}' WHERE ID = {2}".format(quediu, quevoldir, id)
                print('contrasenya canviada')
                flash('Contraseña cambiada')
                return redirect (url_for('login'))

        flash('Las nuevas contraseñas no coinciden')
        return render_template('resetpwd.html')

    return render_template('resetpwd.html')

