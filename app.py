from conn import connect
from flask import Flask, render_template, request, redirect, flash, g, jsonify,session, send_from_directory, json, make_response,send_file, url_for,send_file
import yaml
import datetime
import mysql.connector
import requests
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from weasyprint import HTML
import io
from datetime import datetime, date, time


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
        v_number = request.args.get('v_number') or None


        conditions = []
        params = []


        
        
        print(patient_mobile)
        if v_number == None:

            if patient_name:
                conditions.append("(first_name LIKE %s OR last_name LIKE %s)")
                params.extend(['%' + patient_name + '%', '%' + patient_name + '%'])

            if patient_mrn:
                conditions.append("mrn = %s")
                params.append(patient_mrn)

            if patient_mobile:
                conditions.append("Mobile LIKE %s")
                params.append('%' + patient_mobile + '%')

            if patient_cnic:
                conditions.append("cnic = %s")
                params.append(patient_cnic)

     
            
            conn = connect()
            cur = conn.cursor(dictionary=True)
            if conditions:
                sql = "SELECT * FROM patients where" + ' or' .join(conditions)
            else:
                sql = "SELECT * FROM patients " 
            print(conditions)    
            cur.execute(sql,(params))
            patient_record = cur.fetchall()
            cur.close()
            conn.close()
            return render_template('search_patient.html', patient_record = patient_record)
        else:
            
            conn = connect()
            cur = conn.cursor(dictionary=True)
            sql = """SELECT * FROM patient_visit
                    LEFT JOIN patients ON patients.patient_id = patient_visit.patient_id
                    WHERE patient_visit.visit_number = %s """   
            cur.execute(sql,(v_number,))
            patient_visit = cur.fetchall()
            cur.close()
            conn.close()
            return render_template('search_patient.html', patient_visit = patient_visit)
      

    
    return render_template('search_patient.html', patient_record = patient_record)

def MRN():
    """Retrieve today's latest serial number within a transaction."""
    conn = connect()
    cursor = conn.cursor()
    # today_code = '0402'
    # year = 2026
    
    today_code = datetime.now().strftime("%d%m")  # Format: DDMM
    year = datetime.now().strftime("%y")
    
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
            if 'cnic' in str(error):
                    flash("Please check NIC Feild Enter withou dash")
            else:
                flash(error.args)
            # print(error)  # If MRN is duplicated (shouldn't happen due to COUNT logic)
            # conn.rollback()
            
            return redirect('add_patient')        
          # Retry with new MRN   
     else:       
        return render_template('add_patient.html')
     

@app.route('/cart_item_search')
def cart_item_search():
    if request.method == 'GET':
        search_item = request.args.get('query')
        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql = """select * from stock
                JOIN items ON items.b_item_id = stock.b_item_id where item_name LIKE %s"""
        cur.execute(sql, (f"%{search_item}%",))
        result = cur.fetchall()
        cur.close()
        conn.close()
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
        # print(f"test : {res}")           
        return jsonify({"message": "Save", "cart": session.get("cart", [])})



# 🔵 **Add Item to Cart**
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    data = request.json
    print(f"back {data}")
    item_id = data.get("item_id")
    item_code = data.get("item_code")
    item_name = data.get("item_name")
    batch_number = data.get("batch_no")
    expiry_date = data.get("expiry_date")
    cart_qty = data.get("cart_qty")
    

    price = data.get("price")
    
    
    print(f"price {price}" )
    print(f"qty {cart_qty}")
    print( int(cart_qty) * price)
    
    cart = session.get("cart", []) 

    print(f"this is cart item {cart}")

    conn = connect()
    cur = conn.cursor(dictionary=True)
    sql = "SELECT * FROM stock\
         LEFT JOIN items ON items.b_item_id = stock.b_item_id WHERE stock.item_id = %s"
    print(f"item id {item_id}")
    cur.execute(sql,(item_id,))
    result_qty = cur.fetchall()
    print(f"result {result_qty[0]['pieces_per_pack']}")
    print(f"this is cartui {cart_qty}")

    price_per_peice = price / result_qty[0]['pieces_per_pack']
    
    print(f"price per piece {price_per_peice}")

    

    

    # 🟠 **Check if item already exists in cart**
    item_found = False
    for item in cart:
        if item["item_code"] == item_code and item["batch_number"] == batch_number:
            if result_qty[0]['stock_quantity'] >= item['quantity']+cart_qty:
                item["quantity"] += int(cart_qty)
                item["total"] = round(item["quantity"] * price_per_peice,2)
                session["cart"] = cart
                # return jsonify({"message": "Item added to cart", "cart": cart})
                return jsonify({"cart": cart})
            else:
                return jsonify({"message": "Stock Low", "cart": cart})
            # item_found = True
            # break

    if not item_found:
            

    # 🟡 **Add new item to cart**

        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql = "SELECT * FROM stock\
            LEFT JOIN items ON items.b_item_id = stock.b_item_id WHERE stock.item_id = %s"
        print(f"item id {item_id}")
        cur.execute(sql,(item_id,))
        result_qty = cur.fetchall()
        print(f"result {price_per_peice}")
        print(f"this is cartui {cart_qty}")

    

        if result_qty[0]['stock_quantity'] >= int(cart_qty):
            print(f"ok {cart}")

            cart.append({
                "item_id": item_id,
                "item_code": item_code,
                "description": item_name,
                "batch_number": batch_number,
                "expiry_date": expiry_date,
                "price": round(price_per_peice,2),
                # "quantity": 1,
                "quantity": cart_qty,
                # "total": price
                "total": round(price_per_peice * int(cart_qty),2)
            })
            
            session["cart"] = cart
            print(f"added to cart {cart}")
            # flash("cart updated")
            # return jsonify({"message": "Item added to cart", "cart": cart})
            return jsonify({ "cart": cart})
        else:      
            return jsonify({"message": "Stock Low", "cart": cart})



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
    today_code = datetime.now().strftime("%d%m")  # Format: DDMM
    year = datetime.now().year
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
    today_code = datetime.now().strftime("%d%m")  # Format: DDMM
    year = datetime.now().year
    sql = "SELECT COUNT(*) FROM orders WHERE order_number LIKE  %s"
    cursor.execute(sql, (f'%{year}%',))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    letter_index = count // 9999
    # prefix_letter = chr(ord('A') + letter_index)
    serial = (count % 9999) + 1
    o_number = f"o{year}{serial:04d}"
    return o_number

def Cashslipnumber():
    # """Retrieve today's latest serial number within a transaction."""    
    
    conn = connect()
    cursor = conn.cursor()  
    today_code = datetime.now().strftime("%d%m")  # Format: DDMM
    year = datetime.now().year
    sql = "SELECT COUNT(*) FROM sales WHERE invoice_number LIKE  %s"
    cursor.execute(sql, (f'%{year}%',))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    letter_index = count // 9999
    # prefix_letter = chr(ord('A') + letter_index)
    serial = (count % 9999) + 1
    o_number = f"c{year}{serial:04d}"
    return o_number

def RVouchernumber():
    # """Retrieve today's latest serial number within a transaction."""
    
    
    conn = connect()
    cursor = conn.cursor()  
    today_code = datetime.now().strftime("%d%m")  # Format: DDMM
    year = datetime.now().year
    sql = "SELECT COUNT(*) FROM returns WHERE return_number LIKE  %s"
    cursor.execute(sql, (f'%{year}%',))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    letter_index = count // 9999
    # prefix_letter = chr(ord('A') + letter_index)
    serial = (count % 9999) + 1
    o_number = f"v{year}{serial:04d}" 
    return o_number

@app.route('/r')
def r():
    rvouchernumber= RVouchernumber()
    return(rvouchernumber)
@app.route("/all_order")
def all_order():
 
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
        patient_id = result[0]['patient_id']

        # Visit Number generate 
        visitnumber = VisitNumber()        
        conn = connect()
        cur = conn.cursor()
        sql = "INSERT INTO patient_visit (visit_number, patient_id, STATUS ) VALUES \
              (%s, %s,'Confirmed');"      
        cur.execute(sql, (visitnumber, patient_id, ))
        conn.commit()
        conn.close()

                
        #Get Patient Detail
        order_number = OrderNumber()              
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
        today = datetime.now()
        print(today)
        conn = connect()
        cur  = conn.cursor()
        sql = "INSERT INTO `orders` (`visit_id`, `order_number`, `created_date`, `order_status`) VALUES (%s, %s, %s,%s);"
        cur.execute(sql,(visit_id,order_number,today,'Pending'))
        conn.commit()
        order_id = cur.lastrowid
        cur.close()
        # print(f"last order id: {order_id}")

        #Insert Order Detail along items into db
        item = session.get("cart", [])
        print(item)
        for items in item:
            print(f"order items: {items['description']}")

            item_id = items['item_id']
            item_code = items['item_code']
            item_name = items['description']
            quantity = items['quantity']
            price = items['price']
            print(f"item id {item_id}")
            conn = connect()
            cur  = conn.cursor()
            sql = "INSERT INTO order_detail (order_id, o_item_id, item_code, oitem_name, qty, selling_price,oi_status) VALUES (%s, %s, %s, %s, %s,%s,%s);"
            cur.execute(sql,(order_id,item_id,item_code,item_name, quantity,price,'Pending'))
            conn.commit()
            cur.close()
        
        cart = session.get("cart", [])
        return redirect('/order_detail?mrn='+str(mrn)+"&order="+str(order_number))    



@app.route('/payment_calculaton', methods=['GET','POST'])
def payment():
        mrn = request.args.get('mrn')
        order_number = request.args.get('order')

        # print(mrn)
        # print(order_number)
        #Insert Order Detail along items into db
        item = session.get("cart", [])
        # print(item)
        for items in item:
            # print(f"order items: {items['description']}")
            # item_id = items['item_id']
            item_code = items['item_code']
            item_name = items['description']
            quantity = items['quantity']
            price = items['price']
            # print(f"item price {price}")
            conn = connect()
            cur  = conn.cursor(dictionary=True)
            sql = "select * from stock where item_code = %s"
            cur.execute(sql,(item_code,))
            item_d = cur.fetchall()    
            # print(f"this is tiem {item_d[0]['item_id']}")        
            cur.close()

            #detect Stock
            conn  = connect()
            cur = conn.cursor(dictionary=True)
            sql = "UPDATE stock s \
                    JOIN order_detail oi ON s.item_code = oi.item_code \
                    JOIN orders o ON o.order_id = oi.order_id \
                    SET s.stock_quantity = s.stock_quantity - oi.qty \
                    WHERE o.order_number = %s;"
            cur.execute(sql,(order_number,))
            conn.commit()
            conn.close()
            today = date.today()
            print(today)

            #transection Record
            conn = connect()
            cur = conn.cursor(dictionary=True)
            sql = "INSERT INTO stock_transactions(item_id,transaction_type,transaction_date,quantity) VALUES (%s,%s,%s,%s) "
                    
            cur.execute(sql,(int(item_d[0]['item_id']),'Stock Out',today,quantity))
            conn.commit()
            conn.close()
            cur.close()

             #Order status
            conn = connect()
            cur = conn.cursor(dictionary=True)
            sql = "UPDATE orders SET order_status='Complete' WHERE  order_number=%s;"
                    
            cur.execute(sql,(order_number,))
            conn.commit()
            conn.close()
            cur.close()

        #Sale Entry
        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql2 = "SELECT * FROM order_detail \
                        inner JOIN orders ON orders.order_id = order_detail.order_id \
                        INNER JOIN patient_visit pv ON orders.visit_id = pv.visit_id \
                        WHERE order_number = %s"
        cur.execute(sql2,(order_number,))        
        sale_d = cur.fetchall()
        # print(f"this is order detail {sale_d}")
        conn.close()
        cur.close()
        #Round
        total = 0
        # print(total)
        for item in sale_d:
            print(item['selling_price'])
            print(item['qty'])
            total += float(item['selling_price']) * int(item['qty'])

        # print(f"this is total {total}")
        
        round_amount = round(total)
        round_def = round(round_amount -  total, 1)
        print(f"round amount {round_amount}")

        
        #transection Record

        cashslip_number = Cashslipnumber()
        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql = "INSERT INTO sales(invoice_number,transection_type,s_order_id,total_amount,amount_paid,payment_method,status) \
            VALUES (%s,%s,%s,%s,%s,%s,%s) "
                
        cur.execute(sql,(cashslip_number,'Sale',int(sale_d[0]['order_id']),round_amount,round_amount,'Cash','Complete',))
        conn.commit()
        conn.close()
        cur.close()

          

            




        return redirect('/order_detail?mrn='+str(mrn)+"&order="+str(order_number))


@app.route("/order_detail")
def order_detail():
    session["cart"] = []
    mrn = request.args.get('mrn')        
    OrderNumber = request.args.get('order') 
    # search_item = request.args.get('search-item')
    conn = connect()
    cur = conn.cursor(dictionary=True)
    sql = "select * from patients where MRN = %s LIMIT 1"
    cur.execute(sql,(mrn,))
    result = cur.fetchall()
    conn.close()
    
    conn = connect()
    cur = conn.cursor(dictionary=True)
    sql = "SELECT * FROM order_detail \
            LEFT  JOIN orders ON orders.order_id = order_detail.order_id \
            LEFT  JOIN patient_visit pv ON orders.visit_id = pv.visit_id \
            LEFT  JOIN return_items ri ON ri.item_id = order_detail.oitem_id \
            WHERE order_number = %s;"
    cur.execute(sql,(OrderNumber,))
    order_detail = cur.fetchall()
    conn.close()
    visitnumber = order_detail[0]['visit_number'] 
    # print(order_detail)


    #calculation
    total = 0
    # print(total)
    for item in order_detail:
        print(item['selling_price'])
        print(item['qty'])
        total += float(item['selling_price']) * int(item['qty'])

    # print(f"this is total {total}")

    #Round
    round_amount = round(total)
    round_def = round(round_amount -  total, 1)
   

    #Recipt
    conn = connect()
    cur = conn.cursor(dictionary=True)
    sql = "SELECT * FROM sales s\
        JOIN order_detail od ON od.order_id = s.s_order_id\
        JOIN orders o ON o.order_id = s.s_order_id\
            WHERE o.order_number = %s \
            GROUP BY s.invoice_number"
    cur.execute(sql,(OrderNumber,))
    Slip_detail = cur.fetchall()
    conn.close()
    # print(f"order_detail  {order_detail}")

   





    #vSlip
    #Recipt
    conn = connect()
    cur = conn.cursor(dictionary=True)
    sql = "SELECT * FROM returns \
    JOIN orders ON orders.order_id = returns.original_sale_id \
        WHERE orders.order_id = %s"
    cur.execute(sql,(order_detail[0]['order_id'],))
    vSlip_detail = cur.fetchall()
    conn.close()
   
    

    
    cart = session.get("cart", [])
    
    
    for item in order_detail:
 

        cart.append({
            "item_code": item['item_code'],
            "description": item['oitem_name'],
            # "batch_number": order_detail.batch_number,
            # "expiry_date": order_detail.expiry_date,
            "price": item['selling_price'],
            "quantity": item['qty'],
            "total": 1,
            "oder_detail_item_id":item['oitem_id']
        })
    session["cart"] = cart  


    return render_template('/order_detail.html',patient_record=result, visit_number = visitnumber,OrderNumber=OrderNumber,order_detail=order_detail, total=total, round_amount=round_amount,round_def=round_def,Slip_detail=Slip_detail,vSlip_detail=vSlip_detail)



@app.route("/return_order", methods=['GET','POST'])
def return_detail():
    session["cart"] = []
    mrn = request.args.get('mrn')        
    OrderNumber = request.args.get('OrderNumber') 
    return_item_id = request.form.getlist("order_detail_item_id")
    return_item = request.form.getlist("order_detail_item_qty")
    return_price = request.form.getlist("order_detail_item_price")


    print(f"mrn {mrn}")
    print(f"OrderNumber {OrderNumber}")
    print(f"return_item_id {return_item_id}")
    print(f"return_item_qty {return_item}")
    print(f"return_item_price {return_price}")
    
    if return_item :  
        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql = "select * from patients where MRN = %s"
        cur.execute(sql,(mrn,))
        result = cur.fetchall()
        conn.close()
    

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
        return_price2 = order_detail[0]['selling_price'] 
        print(order_detail)

        #return Order

        rvouchernumber = RVouchernumber()
        print(rvouchernumber)
        order_id = order_detail[0]['order_id']
        print(order_id)
        conn = connect()
        cur  = conn.cursor()
        sql = "INSERT INTO `returns` ( `return_number`,original_sale_id, reason_code,`status`) VALUES ( %s,%s, %s,%s);"
        cur.execute(sql,(rvouchernumber,order_id,'PATIENT RETURN' ,'PENDING'),)
        conn.commit()
        order_id = cur.lastrowid
        cur.close()
       
        print(f"before zip {return_item}")
        for item_id, qty, price_per_pice in zip(return_item_id, return_item, return_price):
        # process each item
            print(f"{OrderNumber} Returning first {qty} units of item ID {item_id} price per pice {price_per_pice}")

            conn = connect()
            cur  = conn.cursor()
            sql = "INSERT INTO return_items (return_id, original_sale_item_id, item_id, quantity, original_price) VALUES (%s, %s, %s, %s,%s);"
            cur.execute(sql,(rvouchernumber,OrderNumber,item_id,qty,price_per_pice))
            conn.commit()
            cur.close()

            print(f"qty {qty}")
            print(f"item id {order_detail[0]['o_item_id']}")
            conn = connect()
            cur  = conn.cursor()
            sql = "UPDATE stock \
                    SET stock_quantity = stock_quantity + %s \
                    WHERE item_id = %s;"
            cur.execute(sql,(int(qty),int(order_detail[0]['o_item_id']),))
            conn.commit()
            cur.close()


             
        # #Return Entry
        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql2 = """SELECT * FROM return_items
                    JOIN returns ON returns.return_number = return_items.return_id
                    JOIN orders ON orders.order_id = returns.original_sale_id

                    WHERE returns.return_number = %s"""
        cur.execute(sql2,(rvouchernumber,))        
        sale_d = cur.fetchall()
        # print(f"this is order detail {sale_d}")
        conn.close()
        cur.close()
        #Round
        total = 0
        # print(total)
        for item in sale_d:
            print(item['original_price'])
            print(item['quantity'])
            total += float(item['original_price']) * int(item['quantity'])

        # print(f"this is total {total}")
        
        round_amount = round(total)
        round_def = round(round_amount -  total, 1)
        print(f"round amount {round_amount}")

        
        #transection Record

        # cashslip_number = Cashslipnumber()
        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql = "INSERT INTO sales(invoice_number,transection_type,s_order_id,total_amount,amount_paid,payment_method,status) \
            VALUES (%s,%s,%s,%s,%s,%s,%s) "
                
        cur.execute(sql,(rvouchernumber,'Return',int(order_id),round_amount,round_amount,'Cash','Complete',))
        conn.commit()
        conn.close()
        cur.close()

    
    




   

    #Recipt
    # conn = connect()
    # cur = conn.cursor(dictionary=True)
    # sql = "SELECT * FROM returns \
    # JOIN orders ON orders.order_id = returns.original_sale_id \
    #     WHERE orders.order_id = %s"
    # cur.execute(sql,(OrderNumber,))
    # vSlip_detail = cur.fetchall()
    # conn.close()
    # print(f"order_detail  {order_detail}")
    

   
 
   
   
        return redirect('/order_detail?mrn='+str(mrn)+"&order="+str(OrderNumber))
    flash("no items selected")
    return redirect('/order_detail?mrn='+str(mrn)+"&order="+str(OrderNumber))

    
@app.route("/cancel_order", methods=['GET','POST'])
def cancel_order():
    cart = session.get("cart", [])
    order_id = request.args.get('OrderNumber')
    mrn = request.args.get('mrn')
    print(f"mrn {mrn}")
    

    conn = connect()
    cur = conn.cursor(dictionary=True)
    sql = """UPDATE orders SET order_status = 'Cancel'
            WHERE order_number = %s;
            """
    sql2 = """UPDATE order_detail SET oi_status = 'Cancel'
            WHERE order_id = (SELECT orders.order_id FROM orders WHERE order_number = %s);"""
    cur.execute(sql,(order_id,))
    cur.execute(sql2,(order_id,))
    conn.commit()
    cur.close()
    return redirect("order_detail?mrn="+mrn+"&order="+order_id)
    
@app.route('/Searchitem', methods=['GET','POST'] )
def searchitem():    
    if request.method == 'GET':
        order_number = 2001
        mrn_number = request.args.get('mrn')
        search_item = request.args.get('search-item')
        print(search_item)
        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql = "select * from stock where item_name like %s"
        cur.execute(sql, (f"%{search_item}%",))
        result = cur.fetchall()
        cur.close()
        conn.close()
        print(result)
        return result

    



@app.route('/PO_request')
def PO_reqeust():
    medicines="s"
    return render_template('PO_create_reqeust.html', medicines=medicines)





@app.route('/cash_invoice/<order_number>')
def cash_invoice(order_number): 

    conn = connect()
    cursor = conn.cursor(dictionary=True)

    # 🔵 **Fetch Order Details**
    cursor.execute("""
                    SELECT o.*, p.*, pv.*, s.* FROM orders o
                    LEFT JOIN patient_visit pv ON pv.visit_id = o.visit_id
                    LEFT JOIN sales s ON s.s_order_id = o.order_id
                    LEFT JOIN patients p ON p.patient_id = pv.patient_id
                    WHERE o.order_number =%s""", (order_number,))
    order = cursor.fetchone()
    print(f"this is order detail {order}")

    # 🟠 **Fetch Order Items**
    cursor.execute("SELECT * FROM order_detail WHERE order_id = %s", (order["order_id"],))
    items = cursor.fetchall()
    
    cursor.close()
    conn.close()
    print(f"items {items}")

     #Round
    total = 0
    print(total)
    for item in items:
        print(item['selling_price'])
        print(item['qty'])
        total += float(item['selling_price']) * int(item['qty'])

    print(f"this is total {total}")
    
    round_amount = round(total)
    round_def = round(round_amount -  total, 1)
    
    # return  render_template('/cash_invoice.html', data = items, order_detail=order, round_amount=round_amount , round_def=round_def)

    rendered = render_template('/cash_invoice.html', data = items, order_detail=order, round_amount=round_amount , round_def=round_def,total=total)
    html = HTML(string=rendered)  

    rendered_pdf = html.write_pdf()  
    return send_file(io.BytesIO(rendered_pdf), download_name='invoice.pdf')


@app.route('/return_invoice/<rvouchernumber>')
def return_invoice(rvouchernumber): 
    print(rvouchernumber)

    conn = connect()
    cursor = conn.cursor(dictionary=True,buffered=True)

    # 🔵 **Fetch Order Details**
    cursor.execute("""
                    SELECT * FROM return_items
                    JOIN returns ON returns.return_number = return_items.return_id
                    JOIN orders ON orders.order_id = returns.original_sale_id  
                    LEFT JOIN sales s ON s.s_order_id = returns.return_id                  
                    WHERE returns.return_number = %s;""", (rvouchernumber,))
    return_v = cursor.fetchone()
    print(f"this is Return order detail {return_v}")

    # 🟠 **Fetch Order Items**
    cursor.execute("SELECT * FROM return_items WHERE return_id = %s", (str(return_v['return_number']),))
    items = cursor.fetchall()
    
    cursor.close()
    conn.close()
    print(f"items {items}")

     #Round
    total = 0
    print(total)
    for item in items:
        print(item['original_price'])
        print(item['quantity'])
        total += float(item['original_price']) * int(item['quantity'])

    print(f"this is total {total}")
    
    round_amount = round(total)
    round_def = round(round_amount -  total, 1)
    
    # return  render_template('/cash_invoice.html', data = items, order_detail=order, round_amount=round_amount , round_def=round_def)

    rendered = render_template('/return_invoice.html', data = items, order_detail=return_v, round_amount=round_amount , round_def=round_def,total=total)
    html = HTML(string=rendered)  

    rendered_pdf = html.write_pdf()  
    return send_file(io.BytesIO(rendered_pdf), download_name='return_invoice.pdf')




# 🟢 **Generate PDF Invoice**
# @app.route("/invoice/<order_number>")
# def generate_invoice(order_number):
#     conn = connect()
#     cursor = conn.cursor(dictionary=True)

#     # 🔵 **Fetch Order Details**
#     cursor.execute("SELECT * FROM orders WHERE order_number = %s", (order_number,))
#     order = cursor.fetchone()
#     print(order)

#     # 🟠 **Fetch Order Items**
#     cursor.execute("SELECT * FROM order_detail WHERE order_id = %s", (order["order_id"],))
#     items = cursor.fetchall()
    
#     cursor.close()
#     conn.close()
#     print(f"items {items}")

#      #Round
#     total = 0
#     print(total)
#     for item in items:
#         print(item['selling_price'])
#         print(item['qty'])
#         total += float(item['selling_price']) * int(item['qty'])

#     print(f"this is total {total}")
    
#     round_amount = round(total)
#     round_def = round(round_amount -  total, 1)
   

#     # 🟡 **Create PDF Invoice**
#     pdf_path = f"invoices/{order_number}.pdf"
#     os.makedirs("invoices", exist_ok=True)
    
#     c = canvas.Canvas(pdf_path, pagesize=letter)
#     c.drawString(100, 750, f"Pharmacy Invoice - Order #{order_number}")
#     c.drawString(100, 730, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#     c.drawString(100, 710, f"Total: {round_amount} | Discount: {'0'} | Paid: {round_amount}")
    
#     y = 680
#     c.drawString(100, y, "----------------------------------------------")
#     c.drawString(100, y-20, "Item Code | Description | Qty | Price | Total")
#     c.drawString(100, y-40, "----------------------------------------------")
    
#     y -= 60
#     for item in items:
#         c.drawString(100, y, f"{item['item_code']}  | {item['oitem_name']}          | {item['qty']}         | {item['selling_price']}       | {item['selling_price']}")
#         y -= 20
    
#     c.save()
     
#     return send_file(pdf_path, as_attachment=True)



# 🟢 **Fetch Ledger Report**
@app.route("/ledger-report")
def ledger_report():
    start_date = request.args.get("start_date", (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d"))
    end_date = request.args.get("end_date", datetime.datetime.now().strftime("%Y-%m-%d"))
    transaction_type = request.args.get("transaction_type", "all")

    conn = connect()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM sales"
    params = [start_date, end_date]

    if transaction_type != "all":
        query += " AND transaction_type = %s"
        params.append(transaction_type)

    cursor.execute(query)
    ledger_data = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template("ledger_report.html", ledger_data=ledger_data, start_date=start_date, end_date=end_date, transaction_type=transaction_type)

@app.route('/create_item', methods=['GET','POST'])
def create_items():
    conn = connect()
    cur = conn.cursor(dictionary=True)
    sql = "select * from items;"
    cur.execute(sql)
    item_record = cur.fetchall()
    conn.close()
    cur.close()

    if request.method == 'POST':
        item_code = request.form.get('item_code') 
        item_name = request.form.get('item_name')
        cat = request.form.get('cat')
        oum = request.form.get('oum')
        pieces = request.form.get('pieces-per-unit')
        pack = request.form.get('pack-per-unit')
        
        # Check for duplicates in database
        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql = "SELECT b_item_code, b_item_name FROM items WHERE b_item_code = %s OR b_item_name = %s;"
        cur.execute(sql, (item_code, item_name))
        items_record = cur.fetchall()
        conn.close()
        
        # Initialize flags
        code_exists = False
        name_exists = False
        
        # Check each record for matches
        for record in items_record:
            if str(record['b_item_code']) == str(item_code):
                code_exists = True
            if str(record['b_item_name']) == str(item_name):
                name_exists = True
        
        # Now check both conditions
        if code_exists and name_exists:
            flash("Both item code and item name already exist!", "error")
        elif code_exists:
            flash("Item code already exists!", "error")
        elif name_exists:
            flash("Item name already exists!", "error")
        else:
            # No duplicates found, proceed with insert
            print("qry start")
            try:
                conn = connect()
                cur = conn.cursor()
                sql = """INSERT INTO items 
                        (b_Item_code, b_item_name, b_cat, uom, pieces_per_pack, packs_per_unit)
                        VALUES (%s, %s, %s, %s, %s, %s);"""
                cur.execute(sql, (item_code, item_name, cat, oum, pieces, pack))
                conn.commit()
                flash("Item added successfully!", "success")
            except Exception as e:
                conn.rollback()
                flash(f"Error adding item: {str(e)}", "error")
            finally:
                if conn:
                    conn.close()
                    return redirect("/create_item")


        
    return render_template('/create_item.html', item_record=item_record)

@app.route('/search_item')
def search_item():
    if request.method == 'GET':
        search_item = request.args.get('query')
        print(search_item)
        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql = "SELECT  items.*, stock.stock_quantity, stock.reorder_level FROM items\
                LEFT JOIN stock ON stock.b_item_id = items.b_item_id where b_item_name like %s"
        cur.execute(sql, (f"%{search_item}%",))
        result = cur.fetchall()
        cur.close()
        conn.close()
        print(result)
        return jsonify(result)


       
    


# @app.route('/pharmacy_stock', methods=['GET','POST'])
# def pharmacy_stock():
#     conn = connect()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM stock")
#     medicines = cursor.fetchall()
#     if request.method == 'POST':
#         item_id = request.form['item_id']
#         item_code = request.form['item_code']
#         item_name = request.form['item_name']
#         cat = request.form['cat']
#         quantity = request.form['quantity']
#         purchase_price = request.form['purchase_price']
#         selling_price = request.form['selling_price']
#         expiry_date = request.form['expiry_date'] or None
#         batch_no = request.form['batch_no']
#         reorder_level = request.form.get('reorder_level') or 0
        

#         print(quantity)
#         conn = connect()
#         cur = conn.cursor(dictionary=True)
#         sql = "select * from stock where b_item_id = %s"
#         cur.execute(sql, (item_id,))
#         q = cur.fetchall()
#         cur.close()
#         conn.close()
#         print(q)
        
#         if q != None:
#             stock_quantity = int(quantity) + int(q[0]['stock_quantity']) or 0
#             conn = connect()
#             cursor = conn.cursor()
#             cursor.execute("INSERT INTO stock (b_item_id,item_code, item_name, category, stock_quantity, reorder_level,batch_no,expiry_date,purchase_price,selling_price) \
#                         VALUES (%s,%s, %s, %s,%s, %s, %s,%s, %s, %s)", (item_id,item_code, item_name, cat,stock_quantity,reorder_level,batch_no,expiry_date,purchase_price,selling_price))
#             conn.commit()
#             conn.close()
#         else:
          
#             stock_quantity = int(quantity)
#             print(f"if stock was 0 {stock_quantity}")

#             conn = connect()
#             cursor = conn.cursor()
#             cursor.execute("INSERT INTO stock (b_item_id,item_code, item_name, category, stock_quantity, reorder_level,batch_no,expiry_date,purchase_price,selling_price) \
#                         VALUES (%s,%s, %s, %s,%s, %s, %s,%s, %s, %s)", (item_id,item_code, item_name, cat,stock_quantity,reorder_level,batch_no,expiry_date,purchase_price,selling_price))
#             conn.commit()
#             conn.close()
       
        


#         # conn = connect()
#         # cursor = conn.cursor()
#         # cursor.execute("INSERT INTO stock (b_item_id,item_code, item_name, category, stock_quantity, reorder_level,batch_no,expiry_date,purchase_price,selling_price) \
#         #             VALUES (%s,%s, %s, %s,%s, %s, %s,%s, %s, %s)", (item_id,item_code, item_name, cat,stock_quantity,reorder_level,batch_no,expiry_date,purchase_price,selling_price))
#         # conn.commit()
#         # conn.close()
        
#     return render_template('/pharmacy_stock.html', medicines =medicines)


@app.route('/pharmacy_stock', methods=['GET', 'POST'])
def pharmacy_stock():
    try:
        # Establish connection
        conn = connect()
        cursor = conn.cursor(dictionary=True)
        
        # Get all medicines for display
        cursor.execute("SELECT * FROM stock")
        medicines = cursor.fetchall()
        
        
        if request.method == 'POST':
            # Get form data with proper defaults and validation
            item_id = request.form.get('item_id')
            item_code = request.form.get('item_code', '').strip()
            item_name = request.form.get('item_name', '').strip()
            cat = request.form.get('cat', '').strip()
            measurment = request.form.get('measurment', '').strip()
            # cat = request.form.get('cat', '').strip()
            quantity = request.form.get('quantity', '0')
            purchase_price = request.form.get('purchase_price', '0')
            selling_price = request.form.get('selling_price', '0')
            # expiry_date = request.form.get('expiry_date')
            batch_no = request.form.get('batch_no', '').strip()
            reorder_level = request.form.get('reorder_level', '0')

            print(f"measurment {measurment}")
            # print(expiry_date)
            
            if measurment != 'Pieces':
                stock_insert = int(measurment) * int(quantity) 
            else:
                stock_insert = int(quantity) 
            print(f"stock insert {stock_insert}")
            # Validate required fields
            if not all([item_id, item_code, item_name, quantity]):
                flash('Missing required fields', 'error')
                return redirect(url_for('pharmacy_stock'))
            
            try:
                # Convert numeric values
                quantity_int = int(stock_insert)
                purchase_price_float = float(purchase_price)
                selling_price_float = float(selling_price)
                reorder_level_int = int(reorder_level)
                
                if quantity_int <= 0:
                    flash('Quantity must be positive', 'error')
                    return redirect(url_for('pharmacy_stock'))
                
                # Check if item exists
                cursor.execute("SELECT stock_quantity, item_id FROM stock WHERE b_item_id = %s", (item_id,))
                existing_stock = cursor.fetchone()
                # print(existing_stock)
                
                # Calculate new quantity
                if existing_stock:
                    stock_quantity = existing_stock['stock_quantity'] + quantity_int
                    print(f"if stock available {stock_quantity}")
                    # Update existing stock
                    update_sql = """
                    UPDATE stock SET 
                        item_code = %s,
                        item_name = %s,
                        category = %s,
                        stock_quantity = %s,
                        reorder_level = %s,
                       
                        
                        purchase_price = %s,
                        selling_price = %s
                        
                    WHERE b_item_id = %s
                    """
                    cursor.execute(update_sql, (
                        item_code, item_name, cat, stock_quantity,
                        reorder_level_int,  
                        purchase_price_float, selling_price_float,
                        item_id
                    ))
                    action = "updated"

                    #stock transaction in on existing items
                    t_id = existing_stock['item_id']
                    print(f"stock item id {t_id}")
                    
                    
                    #stock transaction in on new items
                    # t_id = cursor.lastrowid
                    # print(f"stock item id {t_id}")
                    # from datetime import date
                    today = datetime.now()
                    print(today)
                  

                    s_trans = "INSERT INTO `pharma`.`stock_transactions` (`item_id`, `transaction_type`, `transaction_date`, `quantity`) \
                          VALUES (%s, 'Stock In', %s, %s);"
                    cursor.execute(s_trans,(t_id,today,quantity_int,))

                    
                    
                
                else:
                    stock_quantity = quantity_int
                    # Insert new stock
                    insert_sql = """
                    INSERT INTO stock (
                        b_item_id, item_code, item_name, category,
                        stock_quantity, reorder_level, purchase_price, selling_price
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_sql, (
                        item_id, item_code, item_name, cat,
                        stock_quantity, reorder_level_int, purchase_price_float, selling_price_float
                    ))
                    action = "added"

                    #stock transaction in on new items
                    t_id = cursor.lastrowid
                    print(f"stock item id {t_id}")
                    # from datetime import date
                    today = datetime.now()
                    print(today)
                  

                    s_trans = "INSERT INTO `pharma`.`stock_transactions` (`item_id`, `transaction_type`, `transaction_date`, `quantity`) \
                          VALUES (%s, 'Stock In', %s, %s);"
                    cursor.execute(s_trans,(t_id,today,quantity_int,))
                
                conn.commit()
                flash(f'Stock {action} successfully! New quantity: {stock_quantity}', 'success')
                
                # Refresh medicines list after update
                cursor.execute("SELECT * FROM stock")
                medicines = cursor.fetchall()
                
            except ValueError:
                flash('Invalid numeric values in form', 'error')
                return redirect(url_for('pharmacy_stock'))
            except Exception as e:
                conn.rollback()
                flash(f'Database error: {str(e)}', 'error')
                # return redirect(url_for('pharmacy_stock'))
                
    except Exception as e:
        flash(f'System error: {str(e)}', 'error')
        return redirect(url_for('pharmacy_stock'))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    return render_template('pharmacy_stock.html', medicines=medicines)


@app.route('/legder_report', methods=['GET', 'POST'])
def legder_report():
    if request.method == 'GET':
        

        data = None
        return render_template('legder_report.html', data = data)
    else:

        # start_date = '2025-04-25'
        # end_date = '2025-04-26'

        start_date = request.form.get('s-date')
        end_date = request.form.get('e-date')
        item_code = request.form.get('item_code') or None
        # item_code = None  # Or you can set like 'ITEM001'

        conn = connect()
        cur = conn.cursor(dictionary=True)

        # Base SQL
        sql = """
            SELECT 
                items.b_Item_code, 
                items.b_item_name, 
                stock.item_code,
                stock.item_name,
                stock.reorder_level,

                (
                    SUM(CASE WHEN st.transaction_type = 'Stock In' AND st.transaction_date < %s THEN st.quantity ELSE 0 END)
                    -
                    SUM(CASE WHEN st.transaction_type = 'Stock Out' AND st.transaction_date < %s THEN st.quantity ELSE 0 END)
                ) AS op_balance,
                
                SUM(CASE WHEN st.transaction_type = 'Stock In' AND st.transaction_date BETWEEN %s AND %s THEN st.quantity ELSE 0 END) AS stock_in,
                
                SUM(CASE WHEN st.transaction_type = 'Stock Out' AND st.transaction_date BETWEEN %s AND %s THEN st.quantity ELSE 0 END) AS stock_out,

                (
                    (
                        SUM(CASE WHEN st.transaction_type = 'Stock In' AND st.transaction_date < %s THEN st.quantity ELSE 0 END)
                        -
                        SUM(CASE WHEN st.transaction_type = 'Stock Out' AND st.transaction_date < %s THEN st.quantity ELSE 0 END)
                    )
                    +
                    (
                        SUM(CASE WHEN st.transaction_type = 'Stock In' AND st.transaction_date BETWEEN %s AND %s THEN st.quantity ELSE 0 END)
                        -
                        SUM(CASE WHEN st.transaction_type = 'Stock Out' AND st.transaction_date BETWEEN %s AND %s THEN st.quantity ELSE 0 END)
                    )
                ) AS closing_balance

            FROM 
                items
            JOIN 
                stock ON stock.b_item_id = items.b_item_id
            JOIN 
                stock_transactions st ON st.item_id = stock.item_id
        """

        params = [
            start_date, start_date,
            start_date, end_date,
            start_date, end_date,
            start_date, start_date,
            start_date, end_date,
            start_date, end_date
        ]

        # 🔥 Add WHERE condition dynamically
        if item_code is not None:
            sql += " WHERE stock.item_code = %s"
            params.append(item_code)

        # 🔥 Always add GROUP BY
        sql += """
            GROUP BY 
                items.b_Item_code, 
                items.b_item_name, 
                stock.item_code,
                stock.item_name,
                stock.reorder_level
        """

        # Execute
        cur.execute(sql, params)
        data = cur.fetchall()

        conn.close()
        cur.close()

        print(data)






        return render_template('legder_report.html', data = data)







@app.route('/invoice')
def invoice(): 
    import io
    name = "qazi"  
    return  render_template('/invoice3.html', name = name)

    rendered = render_template('/invoice3.html', name = name)
    html = HTML(string=rendered)
    # rendered_pdf = html.write_pdf('./static/invoice.pdf')
    # return send_file('./static/invoice.pdf')

    rendered_pdf = html.write_pdf()
    #print(rendered)
    return send_file(io.BytesIO(rendered_pdf), download_name='invoice.pdf')

    


def hello_world():
    # --snip-- #
    rendered = render_template('invoice.html')
    html = HTML(string=rendered)
    rendered_pdf = html.write_pdf('./static/invoice.pdf')
    return send_file('./static/invoice.pdf')

if __name__ == '__main__':
    app.run(debug=True)
