#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import datetime
import hashlib

SALT = 'cs3083'
#Initialize the app from Flask
app = Flask(__name__)


def is_list(value):
    return isinstance(value, list)

app.jinja_env.filters['islist'] = is_list


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
            SELECT DISTINCT Po.photoID, Po.photoPoster, Po.postingDate, Po.caption, Pe.firstName, Pe.lastName
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

    # include usernames of people who have liked the photo and the rating they gave it
    # we have the photo`id and we want to get the username and rating of the people who like it

    # we cant include likes and rating in the previous query because then it will only return posts with likes

    
    cursor.execute(visiblePostsQuery, (user, user))
    visiblePosts = cursor.fetchall()

    cursor.close()

    return render_template('home.html', username=user, posts=data, usersToFollow = usersToFollow, groups = groups, visiblePosts = visiblePosts)
@app.route('/findUser', methods = ['GET', 'POST'])
def findUser():
    username = session['username']
    cursor = conn.cursor()
    to_find = request.form['user_to_find']

    # we want to know if we have followed this person or not, or if our follow is pending

    if_follows = 'SELECT DISTINCT username, followStatus FROM Person P JOIN Follow ON (username = username_followed AND username_follower = %s) WHERE username  = %s'
    cursor.execute(if_follows, (username, to_find))
    ret_user = cursor.fetchone()
    if ret_user: 
        print(ret_user)
        return render_template('user.html', user = ret_user)
    else:
        find_user = 'SELECT username FROM Person WHERE username = %s'
        cursor.execute(find_user, to_find) 
        found_user = cursor.fetchone()
        if found_user:
            return render_template('user.html', user = found_user)
        else:
            error = "User not found"
            return redirect(url_for('home', search_error = error))
        

@app.route('/unfollow', methods =['GET', 'POST'])
def unfollow():
    username = session['username']
    to_unfollow = request.form['tounfollow']
    print('we will unfollow', to_unfollow)
    cursor = conn.cursor();
    query = 'DELETE FROM Follow WHERE username_followed = %s AND username_follower = %s'
    cursor.execute(query, (to_unfollow, username))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))



@app.route('/showLikes', methods = ['GET', 'POST'])
def showLikes():
    username = session['username']
    cursor = conn.cursor();
    photoID = request.form['seeLikes']
    get_likes = 'SELECT username, rating FROM Likes WHERE photoID = %s'
    cursor.execute(get_likes, photoID)
    likes = cursor.fetchall()
    cursor.close()

    return render_template('showLikes.html', likes = likes)


@app.route('/getFriendRequests', methods =['GET', 'POST'])
def getFriendRequests():
    username = session['username']
    cursor = conn.cursor();
    query = 'SELECT username_follower FROM Follow WHERE username_followed= %s AND followStatus = 0'
    cursor.execute(query, (username))
    requests = cursor.fetchall()
    cursor.close()

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

@app.route('/declineFriendRequests', methods = ['GET', 'POST'])
def declineFriendRequests():
    username = session['username']
    decline = request.form['declineFollow']
    cursor = conn.cursor();

    query = 'DELETE FROM Follow WHERE username_follower = %s AND username_followed = %s'
    cursor.execute(query, (decline, username))

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
    photoID = request.form['like']

    # check if like already exists
    cursor = conn.cursor();
    find_like = "SELECT * FROM Likes WHERE photoID = %s AND username = %s"
    cursor.execute(find_like, (photoID, username))
    rating = request.form['rating']
    like_exist = cursor.fetchone()
    if like_exist:
        #update rating
        update_rating = 'UPDATE Likes SET rating = %s WHERE username = %s AND photoId = %s'
        cursor.execute(update_rating, (rating,username,photoID))
    else:
        query = 'INSERT INTO Likes(username, photoID, liketime, rating) VALUES(%s, %s, %s, %s)'
        cursor.execute(query, (username, photoID, datetime.datetime.now(), rating))

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
    return render_template('makeFriendGroup.html', username = user, friends = data, error = request.args.get('error'))

@app.route('/submitFriendGroup', methods = ['GET', 'POST'])
def submitFriendGroup():
    user = session['username']
    cursor = conn.cursor()
    groupName = request.form['groupName']

    # check if group name with same owner already exists
    find_group = 'SELECT * FROM FriendGroup WHERE groupName = %s AND groupOwner = %s'
    cursor.execute(find_group, (groupName, user))
    existing_group = cursor.fetchone()
    if existing_group:
        error = "You have already created a group with this name. Please select another name"
        return redirect(url_for('createFriendGroup', error = error))
    else:
        description = request.form['description']
        query = 'INSERT INTO FriendGroup (groupOwner, groupName, description) VALUES (%s, %s, %s)'
        cursor.execute(query, (user, groupName, description))
        conn.commit()


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
    query = 'SELECT DISTINCT groupName, owner_username FROM BelongTo WHERE member_username = %s OR owner_username = %s'
    cursor.execute(query, (user, user))
    groups = cursor.fetchall()
    cursor.close()
    # print(groups)

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