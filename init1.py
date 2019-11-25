#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import datetime

#Initialize the app from Flask
app = Flask(__name__)



# todo: make exceptions
# the login is very similar but we have to make some changes to adapt to our actual database








#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 8889,
                       user='root',
                       password='root',
                       db='Finstagram',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
    return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Person WHERE username = %s and password = %s'
    cursor.execute(query, (username, password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    bio = request.form['bio']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Person WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO Person VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, firstName, lastName, bio))
        conn.commit()
        cursor.close()
        return render_template('index.html')


@app.route('/home')  # the user's own posts
def home():
    user = session['username']
    cursor = conn.cursor();
    query = 'SELECT username FROM Person WHERE username = %s'
    cursor.execute(query, (user))
    data = cursor.fetchall()
    cursor.close()



    # to do: show pending in different color
    cursor = conn.cursor();
    query = 'SELECT username from Person WHERE username != %s AND username NOT IN(SELECT username_followed FROM Follow WHERE username_follower = %s and followstatus = 1)'
    cursor.execute(query, (user, user))
    usersToFollow = cursor.fetchall()
    print(usersToFollow)
    cursor.close()

    #fetch list of users that have not been followed yet


    return render_template('home.html', username=user, posts=data, usersToFollow = usersToFollow)

@app.route('/follow', methods=['GET', 'POST'])
def follow():
    username =  session['username']
    cursor = conn.cursor();
    followed = request.form['tofollow']
    query = 'INSERT Into Follow (username_followed, username_follower, followstatus) VALUES(%s, %s, 0)'
    cursor.execute(query, (followed, username))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))


@app.route('/createFriendGroup', methods = ['GET', 'POST'])
def createFriendGroup():
    user = session['username']
    # fetch people that the user follows and list them as options using a radio button
    cursor = conn.cursor()

    query = 'SELECT username_followed FROM Follow WHERE username_follower = %s and followstatus = 1'
    cursor.execute(query, (user))
    data = cursor.fetchall()
    cursor.close()
    return render_template('makeFriendGroup.html', username = user, friends = data)

@app.route('/submitFriendGroup', methods = ['GET', 'POST'])
def submitFriendGroup():
    user = session['username']
    cursor = conn.cursor()
    groupName = request.form['groupName']
    query = 'INSERT INTO FriendGroup (groupOwner, groupName, description) VALUES (%s, %s, NULL)'
    cursor.execute(query, (user, groupName))
    cursor.close()

    # to do: allow users to modify friendgroup by adding / deleting members

    cursor = conn.cursor()
    members = request.form['friend']
    query = 'INSERT into BelongTo (member_username, owner_username, groupName) VALUES(%s, %s, %s)'
    cursor.execute(query, (members, user, groupName))
    conn.commit()
    cursor.close()

    return redirect(url_for('home'))




        
@app.route('/post', methods=['GET', 'POST'])
def post():
    username = session['username']
    cursor = conn.cursor();
    caption = request.form['caption']
    filename = request.form['filename']

    # convert image to binary 
    binary = convertToBinaryData(filename)
    # get date of post
    postingDate = datetime.datetime.today()

    #change this by adding a radio button to the post
    allFollowers = request.form['allFollowers']

    if not allFollowers: # allow user to pick which group they want to share with
        query = 'SELECT groupName FROM BelongTo WHERE member_username = %s'
        cursor.execute(query, (user))
        groups = data.fetchall()
        cursor.close()
        return render_template('home.html', groups = groups)




    # insert into the table

    # todo: show images

    query = 'INSERT INTO Photo (postingDate, filepath, allFollowers, caption, photoPoster, binaryPhoto) VALUES(%s, %s, %s, %s, %s, NULL)'
    cursor.execute(query, (postingDate, filename, allFollowers, caption, username))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))
    
    
def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData



@app.route('/select_blogger')
def select_blogger():
    #check that user is logged in
    #username = session['username']
    #should throw exception if username not found
    
    cursor = conn.cursor();
    query = 'SELECT DISTINCT username FROM blog'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('select_blogger.html', user_list=data)

@app.route('/show_posts', methods=["GET", "POST"])
def show_posts():
    poster = request.args['poster']
    cursor = conn.cursor();
    query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    cursor.execute(query, poster)
    data = cursor.fetchall()
    cursor.close()
    return render_template('show_posts.html', poster_name=poster, posts=data)

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')
        
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
