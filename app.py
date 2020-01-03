from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from flask_mysqldb import MySQL
from wtforms import BooleanField,Form, StringField, TextAreaField, PasswordField, validators, IntegerField, SelectField
from flask_oauthlib.client import OAuth
app = Flask(__name__)
app.secret_key = ''
app.config['SESSION_TYPE'] = 'filesystem'
# Config MySQL
app.config['MYSQL_HOST'] = ""
app.config['MYSQL_USER'] = ""
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
oauth = OAuth(app)
# init MYSQL
mysql = MySQL(app)

#reglage oauth
viarezo = oauth.remote_app(
    'viarezo',
    consumer_key='',
    consumer_secret='',
    request_token_params={'scope': 'default'},
    base_url='https://auth.viarezo.fr/',
    access_token_method='POST',
    access_token_url='https://auth.viarezo.fr/oauth/token',
    authorize_url='https://auth.viarezo.fr/oauth/authorize'
)

#login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user') is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login')
def login():
    return viarezo.authorize(callback=url_for('authorized', _external=True, _scheme='https',), state="nostate")

@app.route('/login/authorized')
def authorized():
    resp = viarezo.authorized_response()
    if resp is None or resp.get('access_token') is None:
        flash('Erreur de connexion', 'error')
        return redirect(url_for('index'))
    session['viarezo_token'] = (resp['access_token'], '')
    me = viarezo.get('/api/user/show/me')
    session['user'] = me.data['firstName'] + " " + me.data['lastName']
    return redirect(url_for('index'))


@viarezo.tokengetter
def get_viarezo_oauth_token():
    return session.get('viarezo_token')

#Form pour les crepes
class ItemForm(Form):
    nutella = IntegerField('Nombre de crêpes Nutella',default=0)
    #chocolat = SelectField(u'Nombre de crepe chocolat', choices=[('1'), ('2'), ('3')])
    citronsucre = IntegerField('Nombre de crêpes Citron-Sucre',default=0)
    speculos = IntegerField('Nombre de crêpes de speculos',default=0)
    sucre = IntegerField('Nombre de crêpes sucre',default=0)
    confiture = IntegerField('Nombre de crêpes confiture',default=0)
    instructions = StringField('Instructions',default="aucune")
    lieu = StringField('Lieu de livraison')
    completed=BooleanField('Done')
    deliver=BooleanField('Done')
# Index pour version maintenance (pas de livraison de crepe)

# @app.route('/', methods=['GET','POST'])
# def index():
#     return render_template('pause.html')


# Index pour la version ON (livraison de crepes possible)
@app.route('/', methods=['GET','POST'])
@login_required
def index():
    cur = mysql.connection.cursor()
  
    cur.execute("CREATE TABLE IF NOT EXISTS todolist (id INT(11) AUTO_INCREMENT PRIMARY KEY, nom VARCHAR(200),nutella INT(11), citronsucre INT(11), speculos INT(11),sucre INT(11),confiture INT(11),instructions VARCHAR(200), lieu VARCHAR(200), create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,completed BOOL, deliver BOOL);")
    mysql.connection.commit()
    cur.close()
    form = ItemForm(request.form)
    if request.method == 'POST' and form.validate():
        nutella = form.nutella.data
        citronsucre = form.citronsucre.data
        speculos = form.speculos.data
        sucre = form.sucre.data
        confiture = form.confiture.data
        lieu = form.lieu.data
        instructions=form.instructions.data
        nom=session['user']
        
       
        if nutella >100 or citronsucre >100 or speculos>100 or sucre>100 or confiture >100:
            # flash('100 max', 'warning')
            return render_template('trop.html')
        if nutella ==0 and citronsucre == 0 and speculos == 0 and sucre == 0 and confiture ==0 and instructions =='':
            return redirect(url_for('index'))

        
       
         # Create Cursor
        cur = mysql.connection.cursor()
         # Execute
        cur.execute("INSERT INTO todolist(nom,nutella, citronsucre, speculos, sucre, confiture, instructions,lieu, completed,deliver) VALUES(%s, %s, %s,%s, %s,%s,%s,%s,FALSE,FALSE)",(nom,nutella, citronsucre, speculos, sucre, confiture, instructions,lieu))
        

         # Commit to DB
        mysql.connection.commit()

         #Close connection
        cur.close()
         #flash('En cours', 'success')
        return render_template('commande.html')

    return render_template('index.html', form=form)



#page de livraison, privée

@app.route('/livraisons')
@login_required
def livraisons():
    if session['user'] == "Arnaud Petit" or session['user']=="Brieuc Devevey" or session['user']=="Yvan Duhen" or session['user']=="Simon Tronchi" or session['user']=="Clara Rieffel" or session["user"]=="Alban Falck" or session["user"]=="Mehdi Bennis" or session["user"]=="Medhi Hmene" or session["user"]=="Edouard Chauliac" or session["user"]=="Thomas Moreau" or session["user"]=="Youssef Chadali" or session["user"]=="Antoine Payan" or session["user"]=="Valentin Odde" or session["user"]=="Matthieu Annequin" or session["user"]=="Rémi Quentin" or session["user"]=="Robin Delebassée" or session["user"]=="Jean-Baptiste Peter" or session["user"]=="Noah Vincens" or session["user"]=="Romain Fournier" or session["user"]=="Thomas Méot" or session["user"]=="Hicham Bouanani" or session["user"]=="Amine Larhchim" or session["user"]=="Emma Lovisa" or session["user"]=="Florence Remy" or session["user"]=="Majda Brahimi" or session["user"]=="Romain Picard" or session["user"]=="Alban Falck" or session["user"]=="Alban Falck" or session["user"]=="Alban Falck" or session["user"]=="Alban Falck" or session["user"]=="Alban Falck" or session["user"]=="Alban Falck" or session["user"]=="Alban Falck" or session["user"]=="Alban Falck" or session["user"]=="Alban Falck":
        cur=mysql.connection.cursor()
     #recuperer le contenu
        result=cur.execute("SELECT * FROM todolist WHERE deliver = False OR completed = False ORDER BY create_date ASC")
        items=cur.fetchall()
        cur.close()
        if result > 0:
            return render_template('livraisons.html',items=items)
        else:
            msg='Aucune commande'
            return render_template('livraisons.html',msg=msg)
        return render_template('livraisons.html', todo_list=todo_list)
    else:
        return redirect(url_for('index'))

@app.route('/switch_item/<string:id>', methods=['POST'])
def switch_item(id):
    cur = mysql.connection.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS todolist (id INT(11) AUTO_INCREMENT PRIMARY KEY, chocolat INT(11), caramel INT(11), lieu VARCHAR(200), create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,completed BOOL,deliver BOOL);")    
    mysql.connection.commit()
    cur.close()
    cur=mysql.connection.cursor()
    print("SELECT * FROM todolist WHERE id = {}".format(id))
    result=cur.execute("SELECT * FROM todolist WHERE id = {}".format(id))
    item=cur.fetchone()
    print(item)
    
    if(not(item['completed'])):
        cur.execute('UPDATE todolist SET completed=True WHERE id={}'.format(id))
        
    else:
        cur.execute('UPDATE todolist SET completed=False WHERE id={}'.format(id))
        
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('livraisons'))

@app.route('/switch_itemlvr/<string:id>', methods=['POST'])
def switch_itemlvr(id):
    cur = mysql.connection.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS todolist (id INT(11) AUTO_INCREMENT PRIMARY KEY, chocolat INT(11), caramel INT(11), lieu VARCHAR(200), create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,completed BOOL,deliver BOOL);")    
    mysql.connection.commit()
    cur.close()
    cur=mysql.connection.cursor()
    print("SELECT * FROM todolist WHERE id = {}".format(id))
    result=cur.execute("SELECT * FROM todolist WHERE id = {}".format(id))
    item=cur.fetchone()
    print(item)
    
    if(not(item['deliver'])):
        
        cur.execute('UPDATE todolist SET deliver=True WHERE id={}'.format(id))
        
    else:
        
        cur.execute('UPDATE todolist SET deliver=False WHERE id={}'.format(id))
        
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('livraisons'))

@app.route('/delete_item/<string:id>', methods=['POST'])
def delete_item(id):
    cur = mysql.connection.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS todolist (id INT(11) AUTO_INCREMENT PRIMARY KEY, chocolat INT(11), caramel INT(11), lieu VARCHAR(200), create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,completed BOOL,deliver BOOL);")   
    mysql.connection.commit()
    cur.close()
    cur=mysql.connection.cursor()
    cur.execute('DELETE FROM todolist WHERE id={}'.format(id))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('livraisons'))


if __name__ == '__main__':
    app.run(debug=True)
