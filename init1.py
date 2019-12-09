#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import datetime
import hashlib

SALT = 'cs3083'
#Initialize the app from Flask
app = Flask(__name__)



# todo: make exceptions
# todo: make the follow update whenever someone follows someone else -> both ways


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
    return render_template('login.html')


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
    password = request.form['password'] + SALT
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Person WHERE username = %s and password = %s'
    cursor.execute(query, (username, hashed_password))
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
    password = request.form['password'] + SALT
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    bio = request.form['bio']
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

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
        cursor.execute(ins, (username, hashed_password, firstName, lastName, bio))
        conn.commit()
        cursor.close()
        return render_template('login.html')


@app.route('/home')  # the user's own posts
def home():
    user = session['username']
    cursor = conn.cursor();
    query = 'SELECT username FROM Person WHERE username = %s'
    cursor.execute(query, (user))
    data = cursor.fetchall()
    cursor.close()



    # to do: show pending in different color
    #fetch list of users that have not been followed yet
    cursor = conn.cursor();
    query = 'SELECT username, bio from Person WHERE username != %s AND username NOT IN(SELECT username_followed FROM Follow WHERE username_follower = %s)'
    cursor.execute(query, (user, user))
    usersToFollow = cursor.fetchall()

    # #fetch groups the user belongs to 
    query2 = 'SELECT groupName FROM BelongTo WHERE member_username = %s OR owner_username = %s'
    cursor.execute(query2, (user, user))
    groups = cursor.fetchall()

    #  fetching posts requires to first turn the location of the file into a working blob


    # fetch posts visible to user
    # visiblePostsQuery = """
    #         SELECT photoID, photoPoster, postingDate, caption
    #         FROM Photo
    #         WHERE allFollowErs = True AND photoPoster IN 
    #         (SELECT username_followed
    #         FROM Follow 
    #         WHERE username_follower = %s AND followstatus = 1)  OR photoID IN (
    #             SELECT photoID
    #             FROM SharedWith
    #             WHERE (groupOwner, groupName) IN (
    #                 SELECT owner_username, groupName
    #                 FROM BelongTo
    #                 WHERE member_username = %s
    #             )
    #         )
    #         ORDER BY postingDate DESC

    #         """\

    #modify the following to show tagged people too
    visiblePostsQuery = """
            SELECT Po.photoID, Po.photoPoster, Po.postingDate, Po.caption, Pe.firstName, Pe.lastName
            FROM Photo Po JOIN Person Pe ON (Po.photoPoster = Pe.username)
            WHERE allFollowers = True AND photoPoster IN 
            (SELECT username_followed
            FROM Follow 
            WHERE username_follower = %s AND followstatus = 1)  OR photoID IN (
                SELECT photoID
                FROM SharedWith
                WHERE (groupOwner, groupName) IN (
                    SELECT owner_username, groupName
                    FROM BelongTo
                    WHERE member_username = %s
                )
            )
            ORDER BY postingDate DESC  

            """


    
    cursor.execute(visiblePostsQuery, (user, user))
    visiblePosts = cursor.fetchall()
    cursor.close()

    return render_template('home.html', username=user, posts=data, usersToFollow = usersToFollow, groups = groups, visiblePosts = visiblePosts)


@app.route('/getFriendRequests', methods =['GET', 'POST'])
def getFriendRequests():
    username = session['username']
    cursor = conn.cursor();
    query = 'SELECT username_follower FROM Follow WHERE username_followed= %s AND followStatus = 0'
    cursor.execute(query, (username))
    requests = cursor.fetchall()

    print("getting friend requests")
    return render_template('friendRequests.html', requests = requests)

@app.route('/acceptFriendRequests', methods = ['GET', 'POST'])
def acceptFriendRequests():
    username = session['username']
    accepted = request.form['acceptFollow']
    cursor = conn.cursor();
    query = 'UPDATE Follow SET followstatus = 1 WHERE username_followed = %s AND username_follower = %s'
    cursor.execute(query, (username, accepted))
    conn.commit()   
    cursor.close()
    return redirect(url_for('home'))

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

@app.route('/like', methods=['GET', 'POST'])
def like():
    # add a check to see if post has already been liked or not
    username = session['username']
    photoID = request.form['photoID']
    cursor = conn.cursor();
    query = 'INSERT INTO Likes(username, photoID, liketime, rating) VALUES(%s, %s, %s, NULL)'
    cursor.execute(query, (username, photoID, datetime.datetime.now()))
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
    members = request.form.getlist("toAdd")
    to_insert = []
    for member in members:
        to_insert.append((member, user, groupName))

    query = 'INSERT into BelongTo (member_username, owner_username, groupName) VALUES(%s, %s, %s)'
    cursor.executemany(query, to_insert)
    conn.commit()
    cursor.close()

    return redirect(url_for('home'))


        
@app.route('/post', methods=['GET', 'POST'])
# first fetch the groups, then on submit it will lead to another route that will redirect back to him
def post():
    user = session['username']
    cursor = conn.cursor();
    query = 'SELECT groupName FROM BelongTo WHERE member_username = %s OR owner_username = %s'
    cursor.execute(query, (user, user))
    groups = cursor.fetchall()
    cursor.close()
    print(groups)

    return render_template('post.html', username = user, groups = groups)


@app.route('/submitpost', methods = ['GET', 'POST'])
def submitPost():
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

    

    # insert into the table

    # todo: show images

    query = 'INSERT INTO Photo (postingDate, filepath, allFollowers, caption, photoPoster, binaryPhoto) VALUES(%s, %s, %s, %s, %s, %s)'
    cursor.execute(query, (postingDate, filename, allFollowers, caption, username, binary))
    id = cursor.lastrowid
    conn.commit()

    if allFollowers == "0":
        # fetch name of groupOwner using the name of the group and the member
        groups_to_share = request.form.getlist("toShare")
        for group in groups_to_share:
            fetch_group_owner = 'SELECT owner_username FROM BelongTo WHERE groupName = %s AND (member_username = %s OR owner_username = %s)'
            cursor.execute(fetch_group_owner, (group, username, username))
            group_owner = cursor.fetchone()
            print(group_owner, group)
            share_query = 'INSERT INTO SharedWith (groupOwner, groupName, photoID) VALUES (%s, %s, %s)'
        
            cursor.execute(share_query, (group_owner['owner_username'], group, id))
            conn.commit()
    cursor.close()


        



            

        # query = 'INSERT INTO SharedWith (groupOwner, groupName, photoID) '



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