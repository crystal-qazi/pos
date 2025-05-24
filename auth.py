from app import *
from functools import wraps
import jwt
import argon2








url = ""
def user_perm():
    if 'x-access-token' in request.cookies:
                token = request.cookies['x-access-token']
                token_decode = jwt.decode(token, key=app.config['SECRET_KEY'], algorithms="HS256")
                usr_id = token_decode['id']
                conn3 = connect()
                cur = conn3.cursor(dictionary=True, buffered=True)
                sql = """SELECT u.user_id, ur.role_id, rp.permission_id,rp.route FROM user_roles ur
                            RIGHT JOIN users u ON u.user_id = ur.user_id
                            RIGHT JOIN role_permissions rp ON rp.role_id = ur.role_id
                            WHERE u.user_id = %s"""              
                cur.execute(sql,(usr_id,))
                user_perm = cur.fetchall()
                return user_perm
    
def user_perm_front():
    if 'x-access-token' in request.cookies:
                token = request.cookies['x-access-token']
                token_decode = jwt.decode(token, key=app.config['SECRET_KEY'], algorithms="HS256")
                usr_id = token_decode['id']

                conn3 = connect()
                cur = conn3.cursor(dictionary=True, buffered=True)
                sql = "SELECT user_permissions.up_id, user_permissions.role_id, user_permissions.p_id, user_permissions.p_url FROM user_role \
                        Right JOIN users ON users.id = user_role.user_id \
                        Right JOIN user_permissions ON user_permissions.role_id = user_role.role_id \
                        WHERE users.id = %s"
                sql2 = "SELECT * FROM user_role \
                LEFT JOIN front_permissions ON front_permissions.role_id = user_role.role_id\
                WHERE user_role.user_id= %s"
                cur.execute(sql2,(usr_id,))
                user_perm = cur.fetchall()
                return user_perm
    
    

def role_list2(url):
    conn = connect()
    cur = conn.cursor(dictionary=True, buffered=True)
    sql = "SELECT * FROM routes LEFT JOIN role ON routes.role_id = role.r_id WHERE routes.route = %s "
    cur.execute(sql,(url,))
    role_data = cur.fetchall()    
    conn.close()
    
    rows = []
    for row in role_data:
        rows.append(row['role_name'])
    return rows


### login section
def login_req(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            if 'x-access-token' in request.cookies:
                token = request.cookies['x-access-token']
                data = jwt.decode(token, key=app.config['SECRET_KEY'], algorithms="HS256")    

                return func(*args, **kwargs) 
            # else:
            #      flash("else Statment")       
        except jwt.exceptions.DecodeError as err:
             flash("Please login again", 'Alert')
        return redirect(url_for('login', next=request.url))
    return decorated_function            


@app.route("/login", methods = ['POST', 'GET'])
def login():
    url2 = request.args.get('next')
    if not 'x-access-token' in request.cookies:        
        if request.method == 'POST':            
            url = request.endpoint
            username =  request.form['username']
            user_name_2 = username.lower()
            password = request.form['password'] 
            next_url = request.form.get("next")   
            conn = connect()
            cur = conn.cursor(dictionary=True, buffered=True)
            sql = 'SELECT * FROM users where username  LIKE %s AND active = 1 LIMIT 1'
            cur.execute(sql, (username,))
            result = cur.fetchall()
            for resutn in result: 
                if user_name_2 == resutn['username']:    
                            try:  
                                data_pass = resutn['password']
                                print(f"Database {data_pass}")
                                ph = argon2.PasswordHasher()
                                pass_verify = ph.verify(data_pass, password)
                                print(pass_verify)
                            
                                if pass_verify:  
                                    encoded_data = jwt.encode(payload={"id": resutn['user_id'],
                                                    "name": resutn['username'],
                                                    "login" : "logged"},
                                                        key=app.config['SECRET_KEY'],
                                                        algorithm="HS256",
                                                        headers={"kid": "test"})
                                    response = make_response(encoded_data)
                                    if next_url:                                        
                                        response = redirect(next_url)
                                        response.set_cookie('x-access-token', encoded_data)                                        
                                    else:
                                        response = redirect(url_for("dashboard"))
                                        response.set_cookie('x-access-token', encoded_data)                       
                                    return response   
                                else:                                                   
                                    return render_template("signin.html" )
                            except argon2.exceptions.VerifyMismatchError as err:
                                    flash('Login Alert','User or Password incorrect')                  
                                    return render_template("signin.html" )
                            except jwt.exceptions.DecodeError as errjwt:
                                    flash(errjwt)
                                    return render_template("signin.html" )
                else:
                    flash("else")                    
                    return render_template("signin.html" )
            flash("No Such User")
            return render_template("signin.html" )
        return render_template("signin.html")
    else:               
        
        resp = make_response(render_template("signin.html"))
        resp.set_cookie('x-access-token', expires=0)
        return resp


def role_req(url,perm):
    def role_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'x-access-token' in request.cookies:
                token = request.cookies['x-access-token']
                data = jwt.decode(token, key=app.config['SECRET_KEY'], algorithms="HS256")
                user_id = session.get('id')
                conn = connect()
                cur = conn.cursor()
                sql = """SELECT r.role_name FROM users 
                        LEFT JOIN user_roles ur ON ur.user_id = users.user_id
                        LEFT JOIN roles r ON r.role_id = ur.role_id 
                        where users.user_id = %s"""
                cur.execute(sql,(data['id'],))
                user_role2 = cur.fetchall()
                conn.close()
                print(f"user role {user_role2}")
                           
                
                print(f"url {url}")
                print(f"p_id {perm}")

                conn2 = connect()
                cur = conn2.cursor()
                sql = """SELECT roles.role_name from role_permissions  rp
                            left join roles ON roles.role_id = rp.role_id
                           WHERE rp.route = %s AND rp.permission_id= %s"""
                cur.execute(sql,[url, perm])
                allowed = cur.fetchall()
                conn2.close()
                print(f"allowed role {allowed}")
                x = None
                for x in allowed:
                    x = user_role2
                    print(f"allowed role {x} {user_role2}")
                    # flash("You are  Auth veiw This page Content", "Alert")
                    
                # if x in user_role2 or 'superadmin':
                #     print("yes")                 
                    return func(*args, **kwargs)
                else:
                            flash("You are not Auth veiw This page Content", "Alert")
                            return render_template("/error.html")
            return f"out"
        return wrapper
    return role_decorator
        

@app.route('/logout')
def logout_func():
    next_url = request.form.get("next") 
    test = session.get('next_url')
    if next_url:
                session.clear()                
                s = request.cookies['x-access-token']
                resp = make_response()
                resp = redirect(next_url)
                resp.set_cookie('x-access-token', expires=0)
                return resp
                
    else:
        session.pop('login', False)
        resp = make_response()
        resp = redirect('/')
        resp.set_cookie('x-access-token', expires=0)
        return resp