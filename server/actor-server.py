from flask import Flask, Response, jsonify, request
from actorinfo import ActorsInfoPicker, Actor, MovieCredit
# from werkzeug import secure_filename
from werkzeug.utils import secure_filename

from ai_info_parser import make_dict
from db_connection import DBConnector
import json
import facerec
import sys
from flaskext.mysql import MySQL
import bcrypt
import os

prec=facerec.reclass()
app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = sys.argv[1]
app.config['MYSQL_DATABASE_PASSWORD'] = sys.argv[2]
app.config['MYSQL_DATABASE_DB'] = 'giganticgraniteDB'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

@app.route('/actors/image', methods=['POST'])
def getActors():
    img = request.files['image']
    
    #prec.prd(img) returns array of vectors which contain:
    #at first position "right" actor was found or "wrong" actor wasn't
    #found at current position
    #at second place is a mega position number of actor (or best guess in case of "wrong")
    #next four are position of face four int top left right bottom 
    #at this moment there can be problems with using this function
    found_actors=prec.prd(img)
    
    # 		TODO
    # find actor's name for specific id
    # create JSON with array of id, name, position
    #
    # test connection
    # dicted_actors = dict(status='ok')

    dicted_actors = make_dict(found_actors)
    # dicted_actors.append(dict(name='Alan Rickman', imdb='nm0000614'))
    data = json.dumps(dicted_actors)

    return Response(data, mimetype="application/json")


@app.route('/actors/suggestion', methods=['POST'])
def getComplaint():
    #   TODO
    # parse json to get arguments
    # get id from db
    # run method in ai to check suggestion
    #result=prec.sug(img,(top,left,right,bottom),position_id)
    img = request.files['image']
    complaint = request.form.get('complaint')
    img.save(secure_filename(img.filename))
    print(complaint)
    return Response("OK", mimetype="text/xml")


# JSON with details contains
# 	array of Actor:
#		name: string
#		biography: string
#		birthday: string
#		deathday: string or null
#		gender: string
#		imdb_profile: string
#		images: array of string
#		movie_credits: array of MovieCredit
#			title: string
#			genres: array of string
#			vote_average: number
#			poster: string
#	
@app.route('/actordetails/<actor_id>', methods=['GET'])
def getDetails(actor_id):
    picker = ActorsInfoPicker()
    connector = DBConnector()
    actors = []

    tmdb_id = connector.find_actor(actor_id)['tmdb_id']
    pick = picker.download_actor_info(tmdb_id, actor_id)
    if pick is not False:
        actors.append(pick)
    # actors.append(picker.download_actor_info(tmdb_id, 'nm0000093'))
    # actors.append(picker.download_actor_info('4566', 'nm0000614'))

    # Preparing JSON with actor details to return
    dicted_actors = []
    for actor in actors:
        dicted_credits = []
        for movie_credit in actor.movie_credits:
            dicted_credits.append(dict(
                title=movie_credit.title,
                genres=movie_credit.genres,
                vote_average=movie_credit.vote_average,
                poster=movie_credit.poster
            ))

        temp = dict(
            name=actor.name,
            biography=actor.biography,
            birthday=actor.birthday,
            deathday=actor.deathday,
            gender=actor.gender,
            imdb_profile=actor.imdb_profile,
            images=actor.images,
            movie_credits=dicted_credits
        )
        dicted_actors.append(temp)
    data = json.dumps(dicted_actors)

    return Response(data, mimetype="application/json")

#####################################################
#   Login
#####################################################

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    conn = mysql.connect()
    cursor = conn.cursor()

    query = ('SELECT * from user where username=%s')
    cursor.execute(query, (username))
    data = cursor.fetchone()
    if data:
        return jsonify({'data':'username is unavailable'})

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    
    query = ('INSERT INTO user (username, password) VALUES (%s, %s)')
        
    cursor.execute(query, (username, hashed_password))
    conn.commit()


    return jsonify({'data':'ok'})


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = mysql.connect()
    cursor = conn.cursor()

    query = ('SELECT * from user where username=%s')
    cursor.execute(query, (username))
    data = cursor.fetchone()

    if data:
        hash_password = data[2]

        if bcrypt.hashpw(password.encode('utf-8'), hash_password.encode('utf-8')) == hash_password.encode('utf-8'):
            return jsonify({'data':data[0]})
        else:
            return jsonify({'data':'Wrong password'})
    else:
        return jsonify({'data':'Wrong username'})

if __name__ == '__main__':
    app.run(debug = False, host = '156.17.227.136', port = 5000)
    #app.run(debug = False, host = '79.110.197.182', port = 5000)
