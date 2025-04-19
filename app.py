from conn import connect
from flask import Flask, render_template, request, redirect, flash, g, jsonify,session, send_from_directory, json, make_response
import yaml
import datetime
import mysql.connector
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = connect() 
        cursor = conn.cursor()      
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user[0]
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():

    return render_template('index.html')


@app.route('/session2', methods=['get','post'])
def session2():
    cart = session.get("cart", [])
    cart.append({
        "item_code": 123,
        "description": 'item_name',
        "batch_number": 11111,
      
        "total": 22222
    })
    
    resp = make_response(redirect('/get-cookie/'))
    resp.set_cookie('somecookiename', json.dumps(cart))
    return resp 

@app.route('/get-cookie/')
def get_cookie():
    username = request.cookies.get('somecookiename')
    if username:
        data = json.loads(username)  # Convert JSON string back to dictionary
        return jsonify(data)
   
    
    return username
 

@app.route('/all_patient')
def all_patient():
    conn = connect()
    cur = conn.cursor(dictionary=True)
    sql = "SELECT * FROM patients"
    cur.execute(sql,)
    patient_record = cur.fetchall()
    cur.close()
    conn.close()



    return render_template('all_patient.html', patient_record = patient_record)

@app.route('/search_patient', methods=['GET','POST'])
def search_patient():
    if request.method == 'GET':
        patient_name = request.args.get('patient_name') or ''
        patient_mrn = request.args.get('patient_mrn') or ''
        patient_mobile = request.args.get('patient_mobile') or ''
        patient_cnic = request.args.get('patient_cnic') or ''

        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql = "SELECT * FROM patients WHERE first_name LIKE %s;"      
        cur.execute(sql,(patient_name,))
        patient_record = cur.fetchall()
        cur.close()
        conn.close()
        print(patient_record)
      

    
    return render_template('search_patient.html', patient_record = patient_record)

def MRN():
    """Retrieve today's latest serial number within a transaction."""
    conn = connect()
    cursor = conn.cursor()
    # today_code = '0402'
    # year = 2026
    
    today_code = datetime.datetime.now().strftime("%d%m")  # Format: DDMM
    year = datetime.datetime.now().year
    
    sql = "SELECT COUNT(*) FROM patients WHERE mrn LIKE  %s"
    cursor.execute(sql, (f"%{year}-{today_code}-%",))
    count = cursor.fetchone()[0]
 

    letter_index = count // 9999
    prefix_letter = chr(ord('A') + letter_index)
    serial = (count % 9999) + 1
    mrn = f"{prefix_letter}{year}-{today_code}-{serial:04d}"
    print(mrn)

    return mrn



@app.route('/add_patient',  methods=['GET','POST'])
def add_patient():
     if request.method == 'POST':
        patient_fname = request.form.get('patient_fname')
        patient_lname = request.form.get('patient_lname')
        patient_age = request.form.get('patient_age')
        patient_nic = request.form.get('patient_nic') or int()
        patient_mobile = request.form.get('patient_mobile')
        mrn = MRN()
        print(MRN)
        try:
            conn = connect()
            cur = conn.cursor()
            sql = "INSERT INTO patients (`MRN`, `first_name`, `last_name`, `age`, `cnic`, `Mobile`) VALUES (%s, %s, %s, %s, %s, %s);"
            cur.execute(sql, (mrn, patient_fname, patient_lname,patient_age,patient_nic,patient_mobile))
            conn.commit()
            return redirect('create_order?mrn='+mrn)
        except mysql.connector.Error as error:
            flash(error.args)
            print(error)  # If MRN is duplicated (shouldn't happen due to COUNT logic)
            # conn.rollback()
            return redirect('add_patient')        
          # Retry with new MRN   
     else:       
        return render_template('add_patient.html')
     

@app.route('/cart_item_search')
def cart_item_search():
    if request.method == 'GET':
        
        order_number = 2001
        mrn_number = request.args.get('mrn')
        # search_item = request.args.get('search-item')
        search_item = request.args.get('query')
        # search_item = 'panadol'
        print(search_item)
        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql = "select * from items where item_name like %s"
        cur.execute(sql, (f"%{search_item}%",))
        result = cur.fetchall()
        cur.close()
        conn.close()
        print(result)
        return jsonify(result)


# 🟣 **View Cart**
@app.route("/cart", methods=["GET","POST"])
def view_cart():
    if request.method == "GET":
        # res = request.json
        return jsonify(session.get("cart", []))
    else:
        res = request.json
        data = res.get("status") 
        print(f"test : {res}")
           
        return jsonify({"message": "Save", "cart": session.get("cart", [])})



# 🔵 **Add Item to Cart**
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    data = request.json
    item_code = data.get("item_code")
    item_name = data.get("item_name")
    batch_number = data.get("batch_no")
    expiry_date = data.get("expiry_date")
    price = data.get("price")
    
    cart = session.get("cart", [])
    print(f"this is cart item {cart}")

    # 🟠 **Check if item already exists in cart**
    for item in cart:
        if item["item_code"] == item_code and item["batch_number"] == batch_number:
            item["quantity"] += 1
            item["total"] = item["quantity"] * item["price"]
            session["cart"] = cart
            return jsonify({"message": "Item quantity updated", "cart": cart})

    # 🟡 **Add new item to cart**
    cart.append({
        "item_code": item_code,
        "description": item_name,
        "batch_number": batch_number,
        "expiry_date": expiry_date,
        "price": price,
        "quantity": 1,
        "total": price
    })
    
    session["cart"] = cart
    print(f"added to cart {cart}")
    return jsonify({"message": "Item added to cart", "cart": cart})



# 🟤 **Remove Item from Cart**
@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    data = request.json
    item_code = data.get("item_code")
    batch_number = data.get("batch_number")
    
    cart = session.get("cart", [])
    cart = [item for item in cart if not (item["item_code"] == item_code and item["batch_number"] == batch_number)]
    
    session["cart"] = cart
    return jsonify({"message": "Item removed from cart", "cart": cart})

# ⚫ **Clear Cart**
@app.route("/clear_cart", methods=["POST","GET"])
def clear_cart():
    # session.pop('cart', None)

    session["cart"] = []
    return jsonify({"message": "Cart cleared"})

def VisitNumber():
    """Retrieve today's latest serial number within a transaction."""
    conn = connect()
    cursor = conn.cursor()  
    today_code = datetime.datetime.now().strftime("%d%m")  # Format: DDMM
    year = datetime.datetime.now().year
    sql = "SELECT COUNT(*) FROM orders WHERE order_number LIKE  %s"
    cursor.execute(sql, (f'%{year}%',))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    letter_index = count // 9999
    # prefix_letter = chr(ord('A') + letter_index)
    serial = (count % 9999) + 1
    visitnumber = f"v{year}{serial:04d}"
    return visitnumber

def OrderNumber():
    # """Retrieve today's latest serial number within a transaction."""
    
    
    conn = connect()
    cursor = conn.cursor()  
    today_code = datetime.datetime.now().strftime("%d%m")  # Format: DDMM
    year = datetime.datetime.now().year
    sql = "SELECT COUNT(*) FROM orders WHERE order_number LIKE  %s"
    cursor.execute(sql, (f'%{year}%',))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    letter_index = count // 9999
    # prefix_letter = chr(ord('A') + letter_index)
    serial = (count % 9999) + 1
    o_number = f"o{year}{serial:04d}"

    print(o_number)
    return o_number
   



@app.route("/all_order")
def all_order():
    order_number = "o20250003"

    conn= connect()
    cur = conn.cursor(dictionary=True)
    sql = "SELECT orders.*,patient_visit.*,patients.* FROM orders \
    LEFT JOIN patient_visit ON patient_visit.visit_id = orders.visit_id \
    LEFT JOIN patients ON patients.patient_id = patient_visit.patient_id;"
    cur.execute(sql)
    result = cur.fetchall()
    

    return render_template("all_orders.html" , result = result)
    
@app.route('/create_order', methods=['GET','POST'] )
def create_order(): 
    
    if request.method == 'GET': 
        session["cart"] = []
        mrn = request.args.get('mrn') 
        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql = "select * from patients where MRN = %s"
        cur.execute(sql,(mrn,))
        result = cur.fetchall()     
        
        return render_template('create_order.html', patient_record=result)
    else:
        mrn = request.form.get('mrn') 
  
        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql = "select * from patients where MRN = %s"
        cur.execute(sql,(mrn,))
        result = cur.fetchall()
        print(result[0]['patient_id'])
        patient_id = result[0]['patient_id']


        # Visit Number generate 
        visitnumber = VisitNumber()        
        conn = connect()
        cur = conn.cursor()
        sql = "INSERT INTO patient_visit (visit_number, patient_id, STATUS ) VALUES \
              (%s, %s,'comfirmed');"      
        cur.execute(sql, (visitnumber, patient_id, ))
        conn.commit()
        conn.close()

                
        #Get Patient Detail
        order_number = OrderNumber()  
        print(order_number)           
        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql = "SELECT * from patient_visit \
                LEFT JOIN patients ON patients.patient_id = patient_visit.patient_id \
                WHERE patients.MRN = %s AND patient_visit.visit_number = %s"
        cur.execute(sql,(mrn,visitnumber))
        result2 = cur.fetchall()
        conn.close()
        cur.close()  
        visit_id =      result2[0]['visit_id']  
       
      
        #Create Order
        conn = connect()
        cur  = conn.cursor()
        sql = "INSERT INTO `orders` (`visit_id`, `order_number`, `order_status`) VALUES (%s, %s, %s);"
        cur.execute(sql,(visit_id,order_number,'pending'))
        conn.commit()
        order_id = cur.lastrowid
        cur.close()
        print(f"last order id: {order_id}")

        #Insert Order Detail along items into db
        item = session.get("cart", [])
        print(item)
        for items in item:
            print(f"order items: {items['description']}")
            item_code = items['item_code']
            item_name = items['description']
            quantity = items['quantity']
            price = items['price']
            conn = connect()
            cur  = conn.cursor()
            sql = "INSERT INTO order_detail (order_id, item_code, oitem_name, qty, selling_price) VALUES (%s, %s, %s, %s,%s);"
            cur.execute(sql,(order_id,item_code,item_name,quantity,price))
            conn.commit()
            cur.close()

            #detect Stock
            conn  = connect()
            cur = conn.cursor(dictionary=True)
            sql = "UPDATE items s \
                    JOIN order_detail oi ON s.item_code = oi.item_code \
                    JOIN orders o ON o.order_id = oi.order_id \
                    SET s.stock_quantity = s.stock_quantity - oi.qty \
                    WHERE o.order_number = %s;"
            cur.execute(sql,(order_number,))
            conn.commit()
            conn.close()
        
     
        # return jsonify(session.get("cart", []))
        # clear_cart = session["cart"] = []
        # return render_template('create_order.html', patient_record=result, visit_number = visitnumber)
        cart = session.get("cart", [])
        return redirect('/order_detail?mrn='+str(mrn)+"&order="+str(order_number))
    


        
  

    return render_template('create_order.html')





@app.route("/order_detail")
def order_detail():
    session["cart"] = []
    mrn = request.args.get('mrn')        
    OrderNumber = request.args.get('order')
    # search_item = request.args.get('search-item')
    conn = connect()
    cur = conn.cursor(dictionary=True)
    sql = "select * from patients where MRN = %s"
    cur.execute(sql,(mrn,))
    result = cur.fetchall()
    
   

    conn = connect()
    cur = conn.cursor(dictionary=True)
    sql = "SELECT * FROM order_detail \
            inner JOIN orders ON orders.order_id = order_detail.order_id \
            INNER JOIN patient_visit pv ON orders.visit_id = pv.visit_id \
            WHERE order_number = %s "
    cur.execute(sql,(OrderNumber,))
    order_detail = cur.fetchall()
    conn.close()
    visitnumber = order_detail[0]['visit_number'] 
    # print(order_detail)


    #calculation
    
    for o in order_detail:
        p = {o['selling_price']} + {o['selling_price']}
        print(f"total price {p}")

   

    
    cart = session.get("cart", [])
    print(f"this is cart item before {cart}")
    
    for item in order_detail:
 

        cart.append({
            "item_code": item['item_code'],
            "description": item['oitem_name'],
            # "batch_number": order_detail.batch_number,
            # "expiry_date": order_detail.expiry_date,
            "price": item['selling_price'],
            "quantity": item['qty'],
            "total": 1
        })
    session["cart"] = cart
    print(f"this is cart item after {cart}")
    # 🟠 **Check if item already exists in cart**
    # for item in order_detail:
    #     print(item)
    #     print(item.item_code)
    #     if item["item_code"]:
    #         session["cart"] = cart
    #         # 🟡 **Add new item to cart**
    #         cart.append({
    #             "item_code": item_code,
    #             "description": item_name,
    #             "batch_number": batch_number,
    #             "expiry_date": expiry_date,
    #             "price": price,
    #             "quantity": 1,
    #             "total": price
    #         })
    
            # session["cart"] = cart
    # return jsonify({"message": "Item quantity updated", "cart": cart})

    


    # return render_template('create_order.html', patient_record=result, visit_number = visitnumber)
    return render_template('/order_detail.html',patient_record=result, visit_number = visitnumber,OrderNumber=OrderNumber,order_detail=order_detail)


@app.route("/cancel_order", methods=['GET','POST'])
def cancel_order():
    cart = session.get("cart", [])
    order_id = request.args.get('OrderNumber')

    print(cart)
    print(order_id)

    conn = connect()
    cur = conn.cursor(dictionary=True)
    sql = "UPDATE orders SET order_status = 'cancel' \
        WHERE order_id = ( SELECT order_id \
            FROM (SELECT order_id FROM orders WHERE order_number = %s LIMIT 1) AS sub);"
    cur.execute(sql,(order_id,))
    conn.commit()
    cur.close()
    return redirect("order_detail?mrn=A2025-1804-0001&order="+order_id)
    
@app.route('/Searchitem', methods=['GET','POST'] )
def searchitem():    
    if request.method == 'GET':
        order_number = 2001
        mrn_number = request.args.get('mrn')
        search_item = request.args.get('search-item')
        print(search_item)
        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql = "select * from items where item_name like %s"
        cur.execute(sql, (f"%{search_item}%",))
        result = cur.fetchall()
        cur.close()
        conn.close()
        print(result)
        return result

    
@app.route('/pharmacy_stock')
def pharmacy_stock():
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM items")
    medicines = cursor.fetchall()
    return render_template('pharmacy_stock.html', medicines=medicines)


@app.route('/PO_request')
def PO_reqeust():
    medicines="s"
    return render_template('PO_create_reqeust.html', medicines=medicines)


@app.route('/add_medicine', methods=['POST'])
def add_medicine():
    name = request.form['name']
    stock = request.form['stock']
    price = request.form['price']
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO medicines (name, stock, price) VALUES (%s, %s, %s)", (name, stock, price))
    conn.commit()
    return redirect('/medicines')



if __name__ == '__main__':
    app.run(debug=True)
