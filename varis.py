source env/bin/activate
export FLASK_ENV=development

Server: sql11.freemysqlhosting.net
Name: sql11440739
Username: sql11440739
Password: Yv3qDs7JI4
Port number: 3306

''' if nomnen != "":
kidname = request.form['kidname'].capitalize()
con = connectDatabase()
cursor = con.cursor()
sql = "UPDATE infokid SET kidname = '{0}' WHERE kidname = '{1}'".format(kidname,nomnen[1])
print(sql)
cursor.execute(sql)
con.commit()
con.close()'''


from flask import Flask, render_template, request, redirect, url_for, flash
import random

<style>
    .footer {
    background-color: black;
    position: absolute;
    bottom: 0;
    width: 100%;
    height: 40px;
    color: white;
    }   
</style>


app = Flask(__name__)
app.secret_key = 'mysecretkey'



@app.route('/')
def formulari():
    return render_template ("formulari.html")


@app.route('/diccionari')
def consultar():
    llistabuida=[]
    diccionari = open('diccionari.txt', 'r+')
    lineas = diccionari.readlines()  # crea una llista del .txt  
    for cadalinea in lineas:  # itera per cada element de la llista
        lineamaca = cadalinea.replace('\n', '').split(';')  # a cada linea li treu la \n i divideix on hi ha ; creant noves llistes de cada element de la llista d'abans
        #print(lineamaca)
        llistabuida.append(lineamaca)
    #print(llistabuida)
    diccionari.close()

    return render_template("diccionari.html", definicions=llistabuida)


@app.route('/afegir',methods=['POST'])    
def afegir():
    if request.method == 'POST':
        quediu = request.form['quediu'].capitalize().strip()
        quevoldir = request.form['quevoldir'].capitalize().strip()
        quediu=quediu.replace(' ',('_'))
        quevoldir=quevoldir.replace(' ',('_'))
        diccionari= open('diccionari.txt', 'a')
        diccionari.write(quediu + ';' + quevoldir + '\n')
        diccionari.close()
        print(quediu)
        print(quevoldir)
        flash('Paraula afegida! '+ ' ' + quediu + ': '+ quevoldir)
        return redirect(url_for('formulari'))



@app.route('/eliminar/<string:id>')
def eliminar(id):
    #print(id)
    diccionari = open('diccionari.txt', 'r+')
    lineas = diccionari.readlines()  # crea una llista del .txt  
    print(lineas)
    #diccionari.seek(0)  # portem el punter al principi de tot
    diccionari.close() #tanquem diccionari en mode lectura


    diccionari = open('diccionari.txt', 'w') #obrim diccionari en mode sobreescritura, per sobreescriure el fitxer amb el valor eliminat
    for cadalinea in lineas: #transformem cada linea en un element de llista, amb 2 valors
        lineamaca = cadalinea.replace('\n', '').split(';') #treiem salt de linea i dividim el valor en 2 on està ';'
        #print(lineamaca[0], lineamaca[1])
        #print(lineamaca)
        if id in lineamaca: #on l'id sigui el que volem borrar, borra aquesta llista de 2 valors
            del lineamaca[:]
        
        rectificat={} #diccionari buit per volcar tot menys la definició eliminada
        #print(lineamaca)
        #print(lineamaca[0], lineamaca[1])
        for nou in lineamaca: #recorrem la llista i afegim cada item al nou diccionari
            #print(nou)
            rectificat[lineamaca[0]] = lineamaca[1] #a rectificat, el primer valor és la key i el segon, el value
        
        for quediu, quevoldir in rectificat.items():  # items devuelve una lista de tuplas, cada tupla se compone de dos elementos: el primero será la clave y el segundo, su valor.
            diccionari.write('%s;%s\n' % (quediu, quevoldir)) # escrivim al txt els nous valors
            
    #print(lineas)
    diccionari.close() #tanquem diccionari
    flash('Paraula esborrada!')
    return redirect(url_for('consultar'))


@app.route('/editar/<string:id>')
def editar(id):
    
    diccionari = open('diccionari.txt', 'r+')
    lineas = diccionari.readlines()  # crea una llista del .txt  
    #print(lineas)
    diccionari.close()

    diccionari = open('diccionari.txt', 'w')
    for cadalinea in lineas: #transformem cada linea en un element de llista, amb 2 valors
        lineamaca = cadalinea.replace('\n', '').split(';') #treiem salt de linea i dividim el valor en 2 on està ';'
        #print(lineamaca[0], lineamaca[1])
        #print(lineamaca)
        if id in lineamaca: #on l'id sigui el que volem borrar, borra aquesta llista de 2 valors
            global editar1
            global editar2
            editar1 = lineamaca[0]
            editar2 = lineamaca[1]
            del lineamaca[:]
            print(lineamaca)
        
        editat={} #diccionari buit per volcar tot menys la definició eliminada
        #print(lineamaca)
        #print(lineamaca[0], lineamaca[1])
        for nou in lineamaca: #recorrem la llista i afegim cada item al nou diccionari
            #print(nou)
            editat[lineamaca[0]] = lineamaca[1] #a rectificat, el primer valor és la key i el segon, el value
        #diccionari.seek(0)

        for quediu, quevoldir in editat.items():  # items devuelve una lista de tuplas, cada tupla se compone de dos elementos: el primero será la clave y el segundo, su valor.
            diccionari.write('%s;%s\n' % (quediu, quevoldir)) # escrivim al txt els nous valors
    

    print(editar1)
    print(editar2)
    #diccionari.seek(0)  # portem el punter al principi de tot
    diccionari.close() #tanquem diccionari en mode lectura
    
    return render_template('editar.html', quediu = editar1 , quevoldir = editar2)
    #return 'ok'

@app.route('/editar/<string:id>', methods=['POST'])
def actualitzar(id):
    if request.method == 'POST':
        quediu = request.form['quediu'].capitalize().strip()
        quevoldir = request.form['quevoldir'].capitalize().strip()
        quediu=quediu.replace(' ',('_'))
        quevoldir=quevoldir.replace(' ',('_'))
        diccionari= open('diccionari.txt', 'a')
        diccionari.write(quediu + ';' + quevoldir + '\n')
        diccionari.close()
        print(quediu)
        print(quevoldir)
        flash('Paraula afegida! '+ ' ' + quediu + ': '+ quevoldir)
        return redirect(url_for('consultar'))

@app.route('/joc')
def joc():
    diccionarideltxt = {}
    diccionari = open('diccionari.txt', 'r')
    lineas = diccionari.readlines()
    for cadalinea in lineas:
        llistadelineas = cadalinea.replace('\n', '').split(';')
        diccionarideltxt[llistadelineas[0]] = llistadelineas[1]
    diccionari.close()

    llistanomsbons = list(diccionarideltxt.keys())
    llistanomsmarti = list(diccionarideltxt.values())

    compteenrere = 5 
    
    llistaaleatoris = []
    #print(llistanomsbons)
    #print(llistanomsmarti)
    aleatori = random.choice(llistanomsmarti)
    
    print(aleatori)
    
    return render_template('joc.html', aleatori=aleatori, compteenrere=compteenrere)


@app.route('/joc2', methods=['POST'])
def joc2():
    if request.method == 'POST':
        quevoldir = request.form['quevoldir'].capitalize().strip()
        quevoldir=quevoldir.replace(' ',('_'))
    marcador = 0
    compteenrere = 5
    diccionarideltxt = {}
    diccionari = open('diccionari.txt', 'r')
    lineas = diccionari.readlines()
    for cadalinea in lineas:
        llistadelineas = cadalinea.replace('\n', '').split(';')
        diccionarideltxt[llistadelineas[0]] = llistadelineas[1]
    diccionari.close()

    llistanomsbons = list(diccionarideltxt.keys())
    llistanomsmarti = list(diccionarideltxt.values())


    if quevoldir in llistanomsbons:
        print('Correcte!')
        flash('Correcte!')
        #marcador = marcador + 1
    else:
        print('No és correcte!')
        flash('No és correcte!')
        #compteenrere = compteenrere - 1

    aleatori = random.choice(llistanomsmarti)
    compteenrere = compteenrere - 1
    print(compteenrere)
    diccionari.close()
    
    
    return render_template('joc3.html', aleatori=aleatori, compteenrere=compteenrere)


@app.route('/joc3', methods=['POST'])
def joc3():
    if request.method == 'POST':
        quevoldir = request.form['quevoldir'].capitalize().strip()
        quevoldir=quevoldir.replace(' ',('_'))
    marcador = 0
    compteenrere = 5
    diccionarideltxt = {}
    diccionari = open('diccionari.txt', 'r')
    lineas = diccionari.readlines()
    for cadalinea in lineas:
        llistadelineas = cadalinea.replace('\n', '').split(';')
        diccionarideltxt[llistadelineas[0]] = llistadelineas[1]
    diccionari.close()

    llistanomsbons = list(diccionarideltxt.keys())
    llistanomsmarti = list(diccionarideltxt.values())


    if quevoldir in llistanomsbons:
        print('Correcte!')
        flash('Correcte!')
        #marcador = marcador + 1
    else:
        print('No és correcte!')
        flash('No és correcte!')
        #compteenrere = compteenrere - 1

    aleatori = random.choice(llistanomsmarti)
    compteenrere = compteenrere - 2
    print(compteenrere)
    diccionari.close()
    
    return ('final')
    #return render_template('joc3.html', aleatori=aleatori, compteenrere=compteenrere)
