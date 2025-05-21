from conn import connect
from flask import Flask, render_template, request, redirect, flash, g, jsonify,session, send_from_directory, json, make_response,send_file, url_for,send_file
import yaml
import datetime
import mysql.connector
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from weasyprint import HTML
import io
from datetime import datetime, date, time






app = Flask(__name__)
app.config['SECRET_KEY']=b'o8UKgXYZVKfTmU_1N0mcVqb6ZpM5qvUfleVzFJXQhv0='
from auth import *


from mysql.connector import Error
    
def check_user_permission(self, user_id, permission_name):
        """Check if a user has a specific permission"""
        query = """
        SELECT COUNT(*) FROM users u
        JOIN user_roles ur ON u.user_id = ur.user_id
        JOIN role_permissions rp ON ur.role_id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.permission_id
        WHERE u.user_id = %s AND p.permission_name = %s
        """
        conn = connect()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (user_id, permission_name))
            result = cursor.fetchone()
            return result[0] > 0
        except Error as e:
            print(f"Error checking user permission: {e}")
            return False
        finally:
            cursor.close()


@app.route('/test')
def test():

    return render_template('/test.html')

@app.route('/')
@login_req
def dashboard():

    conn = connect()
    cur = conn.cursor(dictionary=True, buffered=True)
    sql = """SELECT COUNT(*) AS total  from patients;"""
    cur.execute(sql)
    patients = cur.fetchall()
    cur.close()
    conn.close()

    conn = connect()
    cur = conn.cursor(dictionary=True, buffered=True)
    sql = """SELECT COUNT(*) AS total  from orders;"""
    cur.execute(sql)
    orders = cur.fetchall()
    cur.close()
    conn.close()

    conn = connect()
    cur = conn.cursor(dictionary=True, buffered=True)
    sql = """SELECT count(*) as total FROM sales 
            WHERE CAST(transaction_date AS date) = CURRENT_DATE() AND transection_type = 'sale';"""
    cur.execute(sql)
    total_sale = cur.fetchall()
    cur.close()
    conn.close()
    conn = connect()
    cur = conn.cursor(dictionary=True, buffered=True)
    sql = """SELECT count(*) as today_return FROM sales 
            WHERE CAST(transaction_date AS date) = CURRENT_DATE() AND transection_type = 'Return';"""
    cur.execute(sql)
    today_return = cur.fetchall()
    cur.close()
    conn.close()

    

   
    return render_template('index.html', patients=patients, orders=orders, total_sale=total_sale, today_return=today_return)


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
@login_req
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
@login_req
def search_patient():
    if request.method == 'GET':
        patient_name = request.args.get('patient_name') or ''
        patient_mrn = request.args.get('patient_mrn') or ''
        patient_mobile = request.args.get('patient_mobile') or ''
        patient_cnic = request.args.get('patient_cnic') or ''
        v_number = request.args.get('v_number') or None


        conditions = []
        params = []


        
        
       
        if v_number == None:

            if patient_name:
                conditions.append("(first_name LIKE %s OR last_name LIKE %s)")
                params.extend(['%' + patient_name + '%', '%' + patient_name + '%'])

            if patient_mrn:
                conditions.append("mrn LIKE %s")
                params.append('%' + patient_mrn + '%')

            if patient_mobile:
                conditions.append('Mobile LIKE %s')
                params.append('%' + patient_mobile + '%')

            if patient_cnic:
                conditions.append('cnic = %s')
                params.append(patient_cnic)

     
            
            conn = connect()
            cur = conn.cursor(dictionary=True)
            if conditions:
                sql = "SELECT * FROM patients WHERE " + ' AND '.join(conditions)  # Changed OR to AND
           
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
@login_req
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
@login_req
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

    price_per_peice = price / (result_qty[0]['pieces_per_pack'] * result_qty[0]['packs_per_unit'] )
    
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
    visitnumber = f"pv{year}{serial:04d}"
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



@app.route("/all_order")
@login_req
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
@login_req
def create_order(): 
    try:
    
        if request.method == 'GET': 
            session["cart"] = []
            mrn = request.args.get('mrn') 
            pv = request.args.get('pv') or None
            conn = connect()
            cur = conn.cursor(dictionary=True, buffered=True)
            sql = "select * from patients where MRN = %s;"
            cur.execute(sql,(mrn,))
            p_result = cur.fetchall()
            sql = "SELECT * FROM patient_visit WHERE visit_number = %s;"
            cur.execute(sql,(pv,))
            v_result = cur.fetchall()     
            
            return render_template('create_order.html', patient_record=p_result, visit_record = v_result)
        else:
            mrn = request.form.get('mrn')
            pv_number = request.form.get('visitnumber') or None
            conn = connect()
            cur = conn.cursor(dictionary=True)
            sql = "select * from patients where MRN = %s"
            cur.execute(sql,(mrn,))
            result = cur.fetchall()      
            patient_id = result[0]['patient_id']
            if pv_number == None:

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
                print(result2)
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


                
            else:
                    
                #Get Patient Detail
                order_number = OrderNumber()              
                conn = connect()
                cur = conn.cursor(dictionary=True)
                sql = "SELECT * from patient_visit \
                        LEFT JOIN patients ON patients.patient_id = patient_visit.patient_id \
                        WHERE patients.MRN = %s AND patient_visit.visit_number = %s"
                cur.execute(sql,(mrn,pv_number))
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

    except Exception as e:
        app.logger.error(f"Error in some_route: {str(e)}")
        # flash("An error occurred", "error")
        return redirect(url_for('search_patient'))

@app.route('/payment_calculaton', methods=['GET','POST'])
@login_req
def payment():
        mrn = request.args.get('mrn')
        order_number = request.args.get('order')

        #Insert Order Detail along items into db
        item = session.get("cart", [])
   
        for items in item:      
            item_code = items['item_code']
            item_name = items['description']
            quantity = items['quantity']
            price = items['price']
            print(f"item qty {quantity}")
            conn = connect()
            cur  = conn.cursor(dictionary=True)
            sql = "select * from stock where item_code = %s"
            cur.execute(sql,(item_code,))
            item_detail = cur.fetchall() 
            item_d = item_detail[0]['item_id'] 
            print(f"this is tiem {item_d}")        
            cur.close()

            #detect Stock
            conn  = connect()
            cur = conn.cursor(dictionary=True)
            sql = "UPDATE stock s \
                    JOIN order_detail oi ON s.item_code = oi.item_code \
                    JOIN orders o ON o.order_id = oi.order_id \
                    SET s.stock_quantity = s.stock_quantity - %s \
                    WHERE o.order_number = %s and oi.o_item_id = %s;"
            cur.execute(sql,(quantity , order_number,item_d,))
            conn.commit()
            conn.close()
            today = date.today()
            print(today)

            #transection Record
            conn = connect()
            cur = conn.cursor(dictionary=True)
            sql = "INSERT INTO stock_transactions(item_id,transaction_type,transaction_date,quantity,reference,mode) VALUES (%s,%s,%s,%s,%s,%s) "
                    
            cur.execute(sql,(int(item_d),'Stock Out',today,quantity,order_number,'Sale'))
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
@login_req
def order_detail():
    session["cart"] = []
    mrn = request.args.get('mrn')        
    OrderNumber = request.args.get('order') 

    conn = connect()
    cur = conn.cursor(dictionary=True)
    sql = "select * from patients where MRN = %s LIMIT 1"
    cur.execute(sql,(mrn,))
    result = cur.fetchall()
    conn.close()
    
    conn = connect()
    cur = conn.cursor(dictionary=True)
    sql = """SELECT * FROM orders o
                LEFT JOIN order_detail od ON od.order_id = o.order_id
                LEFT JOIN patient_visit pv ON pv.visit_id = o.visit_id
                WHERE o.order_number = %s;"""
    cur.execute(sql,(OrderNumber,))
    order_detail = cur.fetchall()
    conn.close()
    visitnumber = order_detail[0]['visit_number'] 
    # print(order_detail)

    conn = connect()
    cur = conn.cursor(dictionary=True, buffered=True)
    sql = """SELECT * FROM return_items ri 
            LEFT JOIN stock s ON s.item_id = ri.item_id
            WHERE ri.original_sale_item_id = %s;"""
    cur.execute(sql,(OrderNumber,))
    return_detail = cur.fetchall()
    cur.close()
    conn.close()

    conn = connect()
    cur = conn.cursor(dictionary=True, buffered=True)
    sql = """SELECT  COUNT(od.oitem_id) AS total_items FROM order_detail od
LEFT JOIN orders o ON o.order_id = od.order_id
WHERE o.order_number = %s;"""
    cur.execute(sql,(OrderNumber,))
    od_count = cur.fetchall()
    cur.close()
    conn.close()

    conn = connect()
    cur = conn.cursor(dictionary=True, buffered=True)
    sql = """SELECT COUNT(ri.return_item_id) AS returned_items FROM return_items ri
WHERE ri.original_sale_item_id = %s;"""
    cur.execute(sql,(OrderNumber,))
    ri_count = cur.fetchall()
    cur.close()
    conn.close()


    #calculation section
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


    return render_template('/order_detail.html',patient_record=result, visit_number = visitnumber,OrderNumber=OrderNumber,order_detail=order_detail, return_detail=return_detail, od_count= od_count, ri_count=ri_count,total=total, round_amount=round_amount,round_def=round_def,Slip_detail=Slip_detail,vSlip_detail=vSlip_detail)



@app.route("/return_order", methods=['GET','POST'])
@login_req
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
        stock_return_id = order_detail[0]['o_item_id'] 
        print(f"stock_order_id {stock_return_id}")

        #return Order

        rvouchernumber = RVouchernumber()
        print(rvouchernumber)
        order_id = order_detail[0]['order_id']
        stock_item_id2 = order_detail[0]['o_item_id']
        print(order_id)
        conn = connect()
        cur  = conn.cursor()
        sql = "INSERT INTO `returns` ( `return_number`,original_sale_id, reason_code,`status`) VALUES ( %s,%s, %s,%s);"
        cur.execute(sql,(rvouchernumber,order_id,'PATIENT RETURN' ,'COMPLETED'),)
        conn.commit()
        order_id = cur.lastrowid
        cur.close()


        print(f"before get stock id {return_item_id}")       
       
       #Return item table entry
        for item_id, qty, price_per_pice in zip(return_item_id, return_item, return_price):
            print(f"after zip item id {item_id}")

            conn = connect()
            cur  = conn.cursor(dictionary=True)
            sql = "SELECT * FROM order_detail \
                inner JOIN orders ON orders.order_id = order_detail.order_id \
                INNER JOIN patient_visit pv ON orders.visit_id = pv.visit_id \
                WHERE oitem_id = %s;"
            cur.execute(sql,(item_id,))
            stock_item_detail = cur.fetchall()
            cur.close()
            # process each item
            stock_item_id = stock_item_detail[0]['o_item_id']
            stock_item_name = stock_item_detail[0]['oitem_name']
            

            print(f"{OrderNumber} Returning first {qty} units of item ID {item_id} price per pice {price_per_pice} stock id {stock_item_id}")

            conn = connect()
            cur  = conn.cursor()
            sql = "INSERT INTO return_items (return_id, original_sale_item_id, item_id,ritem_name, quantity, original_price,refund_amount) VALUES (%s, %s, %s, %s,%s,%s,%s);"
            cur.execute(sql,(rvouchernumber,OrderNumber,stock_item_id,stock_item_name,qty,price_per_pice,price_per_pice))
            conn.commit()
            cur.close()

            print(f"qty {qty}")
            print(f"item id {stock_item_id}")

            ##Stock upate
            conn = connect()
            cur  = conn.cursor()
            sql = "UPDATE stock \
                    SET stock_quantity = stock_quantity + %s \
                    WHERE item_id = %s;"
            cur.execute(sql,(int(qty),int(stock_item_id),))
            conn.commit()
            cur.close()


             
            # Stock transaction Entry
            conn = connect()
            cur = conn.cursor(dictionary=True)
            sql2 = """SELECT * FROM return_items
                        JOIN returns ON returns.return_number = return_items.return_id
                        JOIN orders ON orders.order_id = returns.original_sale_id

                        WHERE returns.return_number = %s"""
            cur.execute(sql2,(rvouchernumber,))        
            sale_d = cur.fetchall()
            return_item_id2 = item_id
            print(f"this is return item id {stock_item_id}")
            conn.close()
            cur.close()
            #Round
            total = 0
            today = datetime.now()         

            print(f"before stock transection stock id:{qty} stock qty {qty} voucher {rvouchernumber}")
                
            conn = connect()
            cur = conn.cursor(dictionary=True)
            s_trans = "INSERT INTO `stock_transactions` (`item_id`, `transaction_type`, `transaction_date`, `quantity`,`reference`,`mode`) \
                    VALUES (%s, 'Return', %s, %s, %s, 'Patient Return');"
            cur.execute(s_trans,(stock_item_id,today,qty,rvouchernumber))
            conn.commit()
            conn.close()
            cur.close()

        print(f"before sale entry {sale_d}")
        for item in sale_d:
            print(item['original_price'])
            print(item['quantity'])
            total = float(item['original_price']) * int(item['quantity'])

    
            
            round_amount = round(total,1)
            round_def = round(round_amount -  total, 1)
            print(f"round amount {round_amount}")

                
            # Sale Record


            conn = connect()
            cur = conn.cursor(dictionary=True)
            sql = "INSERT INTO sales(invoice_number,transection_type,s_order_id,total_amount,amount_paid,payment_method,status) \
                VALUES (%s,%s,%s,%s,%s,%s,%s) "
                    
            cur.execute(sql,(rvouchernumber,'Return',int(order_id),round_amount,round_amount,'Cash','Complete',))
            conn.commit()
            conn.close()
            cur.close()
            print(f"sale entry pass {rvouchernumber} {order_id} {round_amount}")


        ##Update order Status

        conn = connect()
        cur  = conn.cursor()
        sql = "UPDATE `orders` SET `order_status`='Return' WHERE  `order_number` = %s"
        cur.execute(sql,(OrderNumber,))
        conn.commit()
        cur.close()

        return redirect('/order_detail?mrn='+str(mrn)+"&order="+str(OrderNumber))
    flash("no items selected")
    return redirect('/order_detail?mrn='+str(mrn)+"&order="+str(OrderNumber))

    
@app.route("/cancel_order", methods=['GET','POST'])
@login_req
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
@login_req
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
@login_req
def PO_reqeust():
    medicines="s"
    return render_template('PO_create_reqeust.html', medicines=medicines)



@app.route('/cash_invoice/<order_number>')
@login_req
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
@login_req
def return_invoice(rvouchernumber): 
    print(rvouchernumber)

    conn = connect()
    cursor = conn.cursor(dictionary=True,buffered=True)

  
    cursor.execute("""
                    SELECT * FROM return_items
                    JOIN returns ON returns.return_number = return_items.return_id
                    JOIN orders ON orders.order_id = returns.original_sale_id  
                    LEFT JOIN sales s ON s.s_order_id = returns.return_id 
                   LEFT JOIN patient_visit pv ON pv.visit_id = orders.visit_id   
						  LEFT JOIN patients p ON p.patient_id = pv.patient_id                   
                    WHERE returns.return_number = %s;""", (rvouchernumber,))
    return_v = cursor.fetchone()
    print(f"this is Return order detail {return_v}")

    # 🟠 **Fetch Order Items**
    item_id = return_v
    print(f"v {item_id}")
    # cursor.execute("SELECT * FROM return_items \
    #                 LEFT JOIN order_detail od ON od.o_item_id = return_items.item_id \
    #                 WHERE return_items.return_id = %s", (str(rvouchernumber),))
    cursor.execute("SELECT * FROM returns \
                    LEFT JOIN return_items ri ON returns.return_number = ri.return_id\
                    LEFT JOIN stock s ON s.item_id = ri.item_id\
                    WHERE returns.return_number = %s", (str(rvouchernumber),))
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
        print(item['item_name'])
        total += float(item['original_price']) * int(item['quantity'])

    print(f"this is total {total}")

    total2 = round(total,2)
    
    round_amount = round(total)
    print(round_amount)
    round_def = round(round_amount -  total2, 1)
    
    # return  render_template('/cash_invoice.html', data = items, order_detail=order, round_amount=round_amount , round_def=round_def)

    rendered = render_template('/return_invoice.html', data = items, order_detail=return_v, round_amount=round_amount , round_def=round_def,total=total2)
    html = HTML(string=rendered)  

    rendered_pdf = html.write_pdf()  
    return send_file(io.BytesIO(rendered_pdf), download_name='return_invoice.pdf')




@app.route('/create_item', methods=['GET','POST'])
@login_req
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

@app.route('/update_item', methods=['GET','POST'])
@login_req
def update_item():
    try:
        if request.method == 'GET':
            item_id = request.args.get('itemid')
            conn = connect()
            cur = conn.cursor(dictionary=True)
            sql = """SELECT * FROM items
                    WHERE items.b_item_id = %s"""
            cur.execute(sql,(item_id,))
            item_record = cur.fetchone()
            cur.close()
            conn.close()


            print(f"items detail {item_record}")

            return render_template('/update_item.html',item_record=item_record)
        else:
            item_id2 = request.form.get('item_id')
            item_code = request.form.get('item_code') 
            item_name = request.form.get('item_name')
            cat = request.form.get('cat')
            oum = request.form.get('oum')
            pieces = request.form.get('pieces-per-unit')
            pack = request.form.get('pack-per-unit')
            item_status = request.form.get('is_active') or 0
            print(f"item id from form {item_id2}")

            conn  = connect()
            cur = conn.cursor()
            sql = """UPDATE `items` SET 
            `b_Item_code`=%s, 
            `b_item_name`=%s, 
            `b_cat`=%s, 
            `uom`=%s, 
            `pieces_per_pack`=%s, 
            `packs_per_unit`=%s, 
            `is_active`=%s 
            
            WHERE  `b_item_id`=%s;
                                    """
            
            cur.execute(sql,(item_code,item_name,cat,oum,pieces,pack,item_status,item_id2,))
            conn.commit()
            cur.close()
            conn.close()
            flash('Item Updated', 'success')
            return redirect('create_item')
            return redirect('/update_item?itemid='+item_id2)
        
    except Exception as e:
        app.logger.error(f"Error in some_route: {str(e)}")
        if 'Cannot delete or update' in str(e):

            flash("Item Used in Orders", "You Can't Change Item Code or Name Which Items are Used in Orders")
            return redirect('/update_item?itemid='+item_id2)
        else:
            flash(str(e), "Alert")
            return redirect('/update_item?itemid='+item_id2)


@app.route('/search_item')
@login_req
def search_item():
    if request.method == 'GET':
        search_item = request.args.get('query')
        print(search_item)
        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql = "SELECT  items.*, stock.stock_quantity, stock.reorder_level FROM items\
                LEFT JOIN stock ON stock.b_item_id = items.b_item_id where b_item_name like %s AND  items.is_active = 1"
        cur.execute(sql, (f"%{search_item}%",))
        result = cur.fetchall()
        cur.close()
        conn.close()
        print(result)
        return jsonify(result)





@app.route('/pharmacy_stock', methods=['GET', 'POST'])
@login_req
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
            packsize = request.form.get('packsize').strip()
            # cat = request.form.get('cat', '').strip()
            quantity = request.form.get('quantity')
            purchase_price = request.form.get('purchase_price', '0')
            selling_price = request.form.get('selling_price', '0')
            # expiry_date = request.form.get('expiry_date')
            batch_no = request.form.get('batch_no', '').strip()
            reorder_level = request.form.get('reorder_level', '0')

            print(f"measurment {measurment}")
            print(f"pack size {packsize}")
            if measurment.isdigit() and packsize.isdigit():

                #unit
                if  int(measurment) != int(packsize):                
                        stock_insert = int(measurment) * int(quantity) * int(packsize)                
                        print(f"unit insert {stock_insert}")

                # pack
                if int(measurment) == int(packsize):
                    print("yes")
                    conn = connect()
                    cursor = conn.cursor(dictionary=True)
                    
                    # Get all medicines for display
                    
                    cursor.execute("SELECT * FROM items where b_item_id = %s;",(item_id,))
                    medicines = cursor.fetchall()
                
                    size = medicines[0]['pieces_per_pack']
                    print(f"peace per pack {size}")
                    print(f"insert quanty per pack {int(size) * int(quantity) }")
                    stock_insert =  int(size) * int(quantity)
                # unit
           
            
            else:
            # if measurment == 'Pieces':
                print(f"in pece func")
                
                stock_insert = int(quantity) 
                print(f" peice {stock_insert}")
               
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
                        selling_price = %s,
                        created_at = %s
                        
                    WHERE b_item_id = %s
                    """
                    today = datetime.now()
                    cursor.execute(update_sql, (
                        item_code, item_name, cat, stock_quantity,
                        reorder_level_int,  
                        purchase_price_float, selling_price_float,today,
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
                  

                    s_trans = "INSERT INTO `stock_transactions` (`item_id`, `transaction_type`, `transaction_date`, `quantity`,`mode`) \
                          VALUES (%s, 'Stock In', %s, %s,'Purchase');"
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
                  

                    s_trans = "INSERT INTO `stock_transactions` (`item_id`, `transaction_type`, `transaction_date`, `quantity`,`mode`) \
                          VALUES (%s, 'Stock In', %s, %s,'Purchase');"
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
        if 'cur' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
        return render_template('pharmacy_stock.html', medicines=medicines)




@app.route('/stock_return', methods=['POST','GET'])
def stock_return():
    # try:
        if request.method == 'GET':
            item_id = request.args.get('item_id')
            conn = connect()
            cur = conn.cursor(dictionary=True, buffered=True)
            sql = """select * from stock where item_id = %s"""
            cur.execute(sql, (item_id,))
            result = cur.fetchall()
            cur.close()
            conn.close()
            # print(locals())

            return render_template('/stock_return.html', result=result)
        else:
            item_id = request.form.get('item_id')
            r_qty = request.form.get('r_qty')
            current_stock = request.form.get('current_stock')
            r_type = request.form.get('r_type')
            r_reason = request.form.get('r_reason')

       
            if not all([item_id,r_qty,current_stock,r_type,r_reason]):
                  flash('All fields are required!', 'Alert')
                  return redirect(url_for('stock_return')+'?item_id=' + item_id)
            try:
                # Convert quantity to integer (with validation)
                r_qty = int(r_qty)
                if r_qty <= 0:
                    flash('Quantity must be positive!', 'error')
                    return redirect(url_for('stock_return')+'?item_id=' + item_id)
                else:
                    # Check Current stock at post request for safty
                    conn = connect()
                    cur = conn.cursor(dictionary=True)
                    sql = """select * from stock where item_id = %s"""
                    cur.execute(sql, (item_id,))
                    checked_current_stock = cur.fetchall()
                    cur.close()
                    conn.close()

                    checked_current_stock = int(checked_current_stock[0]['stock_quantity'])                    
                    today = datetime.now()

                    print(f"stock transaction  qty {r_qty}")
                    print(f"stock transaction type {r_type}")
                    print(f"stock transaction date {today}")

                    if r_type == 'Stock Out':                        
                        
                        less_stock = checked_current_stock - r_qty

                        print(f"Current Stock {current_stock}")
                        print(f"less stock {less_stock}")

                        conn = connect()
                        cur = conn.cursor()
                        sql = """UPDATE `stock` SET `stock_quantity`=%s WHERE  `item_id`=%s"""
                        cur.execute(sql,(less_stock,item_id,))
                        conn.commit()
                        cur.close()
                        conn.close()

                        ## Stock Less Transection 
                        
                        
                        conn = connect()
                        cur = conn.cursor()
                        sql = """INSERT INTO `stock_transactions` 
                                (`item_id`, `transaction_type`, `quantity`, `transaction_date`, `mode`,`remarks`) 
                                VALUES 
                                (%s, %s, %s, %s, %s,%s);"""
                        cur.execute(sql,(item_id,'Stock Out',r_qty,today,'Adjustment',r_reason,))
                        conn.commit()
                        cur.close()
                        conn.close()
                
                    
                        flash('Stock Less successfully!', 'success')
                        return redirect(url_for('stock_return')+'?item_id=' + item_id)
                    elif r_type == 'Stock In':
                        less_stock = checked_current_stock + r_qty
                        
                        print(f"Current Stock {current_stock}")
                        print(f"less stock {less_stock}")

                        conn = connect()
                        cur = conn.cursor()
                        sql = """UPDATE `stock` SET `stock_quantity`=%s WHERE  `item_id`=%s"""
                        cur.execute(sql,(less_stock,item_id,))
                        conn.commit()
                        cur.close()
                        conn.close()

                        ## Stock Less Transection 
                        
                        
                        conn = connect()
                        cur = conn.cursor()
                        sql = """INSERT INTO `stock_transactions` 
                                (`item_id`, `transaction_type`, `quantity`, `transaction_date`, `mode`,`remarks`) 
                                VALUES 
                                (%s, %s, %s, %s, %s,%s);"""
                        cur.execute(sql,(item_id,'Stock In',r_qty,today,'Adjustment',r_reason,))
                        conn.commit()
                        cur.close()
                        conn.close()

                        
                        
                        flash('Stock Added successfully!', 'success')
                        return redirect(url_for('stock_return')+'?item_id=' + item_id)

                    elif r_type == 'Expiry':
                        less_stock = checked_current_stock - r_qty
                        
                        print(f"Current Stock {current_stock}")
                        print(f"less stock {less_stock}")

                        conn = connect()
                        cur = conn.cursor()
                        sql = """UPDATE `stock` SET `stock_quantity`=%s WHERE  `item_id`=%s"""
                        cur.execute(sql,(less_stock,item_id,))
                        conn.commit()
                        cur.close()
                        conn.close()

                        ## Stock Less Transection 
                        
                        
                        conn = connect()
                        cur = conn.cursor()
                        sql = """INSERT INTO `stock_transactions` 
                                (`item_id`, `transaction_type`, `quantity`, `transaction_date`, `mode`,`remarks`) 
                                VALUES 
                                (%s, %s, %s, %s, %s,%s);"""
                        cur.execute(sql,(item_id,'Stock Out',r_qty,today,'Expiry',r_reason,))
                        conn.commit()
                        cur.close()
                        conn.close()

                        flash('Expiry Less from Stock successfully!', 'success')
                        return redirect(url_for('stock_return')+'?item_id=' + item_id)
                    
                    elif r_type == 'Damage':
                        less_stock = checked_current_stock - r_qty
                        
                        print(f"Current Stock {current_stock}")
                        print(f"less stock {less_stock}")

                        conn = connect()
                        cur = conn.cursor()
                        sql = """UPDATE `stock` SET `stock_quantity`=%s WHERE  `item_id`=%s"""
                        cur.execute(sql,(less_stock,item_id,))
                        conn.commit()
                        cur.close()
                        conn.close()

                        ## Stock Less Transection 
                        
                        
                        conn = connect()
                        cur = conn.cursor()
                        sql = """INSERT INTO `stock_transactions` 
                                (`item_id`, `transaction_type`, `quantity`, `transaction_date`, `mode`,`remarks`) 
                                VALUES 
                                (%s, %s, %s, %s, %s,%s);"""
                        cur.execute(sql,(item_id,'Stock Out',r_qty,today,'Damage',r_reason,))
                        conn.commit()
                        cur.close()
                        conn.close()

                 

                        flash('Damage Less from Stock successfully!', 'success')
                        return redirect(url_for('stock_return')+'?item_id=' + item_id)
                    else:
                        flash('No Operation Done', 'success')
                        return redirect(url_for('stock_return')+'?item_id=' + item_id)

            except ValueError:
                flash('Invalid quantity format!', 'error')
                return redirect(url_for('stock_return')+'?item_id=' + item_id)
    # except Exception as e:
    #     flash(f'System error: {str(e)}', 'error')
    #     return redirect(url_for('stock_return')+'?item_id=' + item_id)
    # finally:
    #     if 'cur' in locals():
    #         cur.close()
    #     if 'conn' in locals():
    #         conn.close()


@app.route('/stock_price_udpate', methods=['GET','POST'])
def stock_price_update():

    if request.method == 'POST':
        item_id = request.form.get('item_id')
        p_udpate_reate = request.form.get('p_udpate_reate')
        s_update_rate = request.form.get('s_update_rate')

        conn = connect()
        cur = conn.cursor()
        sql = """UPDATE stock SET purchase_price=%s, selling_price=%s WHERE  item_id=%s;"""
        cur.execute(sql,(p_udpate_reate,s_update_rate,item_id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('pharmacy_stock'))
    else:
        return redirect(url_for('stock_return'))



    
@app.route('/legder_report', methods=['GET', 'POST'])
@login_req
def legder_report():
    if request.method == 'GET':
        

        data = None
        return render_template('legder_report.html', data = data)
    else:


        start_date = request.form.get('s-date')
        s_date = start_date+' 00:00:00'
        print(s_date)
        end_date = request.form.get('e-date')
        # e_date = end_date+' '+datetime.now().strftime("%H:%M:%S")
        e_date = end_date+' '+'23:59:59'
        print(e_date)
        item_code = request.form.get('item_code') or None
        # item_code = None  # Or you can set like 'ITEM001'

        conn = connect()
        cur = conn.cursor(dictionary=True)

        # Base SQL
        sql = """            
                SELECT  i.b_item_id AS item_id, i.b_Item_code AS item_code, i.b_item_name AS item_name, i.b_cat AS category, i.uom,
                    
                    -- Opening balance (stock at beginning of period)
                    (SELECT COALESCE(SUM(CASE 
                        WHEN st.transaction_type = 'Stock In' THEN st.quantity 
                        WHEN st.transaction_type = 'Stock Out' THEN -st.quantity 
                        WHEN st.transaction_type = 'Return' THEN st.quantity
                        ELSE 0 
                    END), 0)
                    FROM stock_transactions st
                    WHERE st.item_id = s.item_id 
                    AND st.transaction_date < %s) AS opening_balance,
                    
                    -- Stock In during period
                    (SELECT COALESCE(SUM(st.quantity), 0)
                    FROM stock_transactions st
                    WHERE st.item_id = s.item_id 
                    AND st.transaction_type = 'Stock In'
                    AND st.transaction_date BETWEEN %s AND %s) AS stock_in,
                    
                    -- Stock Out during period (sales)
                    (SELECT COALESCE(SUM(st.quantity), 0)
                    FROM stock_transactions st
                    WHERE st.item_id = s.item_id 
                    AND st.transaction_type = 'Stock Out'
                    AND st.transaction_date BETWEEN %s AND %s) AS stock_out,
                    
                    -- Returns during period
                    (SELECT COALESCE(SUM(st.quantity), 0)
                    FROM stock_transactions st
                    WHERE st.item_id = s.item_id 
                    AND st.transaction_type = 'Return'
                    AND st.transaction_date BETWEEN %s AND %s) AS returns_in,
                    
                    -- Closing balance (opening + stock in - stock out + returns)
                    ((SELECT COALESCE(SUM(CASE 
                        WHEN st.transaction_type = 'Stock In' THEN st.quantity 
                        WHEN st.transaction_type = 'Stock Out' THEN -st.quantity 
                        WHEN st.transaction_type = 'Return' THEN st.quantity
                        ELSE 0 
                    END), 0)
                    FROM stock_transactions st
                    WHERE st.item_id = s.item_id 
                    AND st.transaction_date < %s)
                    +
                    (SELECT COALESCE(SUM(CASE 
                        WHEN st.transaction_type = 'Stock In' THEN st.quantity 
                        WHEN st.transaction_type = 'Stock Out' THEN -st.quantity 
                        WHEN st.transaction_type = 'Return' THEN st.quantity
                        ELSE 0 
                    END), 0)
                    FROM stock_transactions st
                    WHERE st.item_id = s.item_id 
                    AND st.transaction_date BETWEEN %s AND %s)) AS closing_balance
                    
                FROM items i
                JOIN stock s ON i.b_item_id = s.b_item_id
                WHERE i.is_active = 1
                 

        """

        params = [
            s_date, 
            s_date, e_date,
            s_date, e_date,
            s_date, e_date,           
            s_date, 
            s_date, e_date,           
           
        ]

        # 🔥 Add WHERE condition dynamically
        if item_code is not None:
            sql += " AND s.item_code = %s"
            params.append(item_code)

        # 🔥 Always add GROUP BY
        sql += """
        
            ORDER BY i.b_cat, i.b_item_name;  
        """

        # Execute
        cur.execute(sql, params)
        data = cur.fetchall()

        conn.close()
        cur.close()

        print(data)


        return render_template('legder_report.html', data = data)

@app.route('/sale_report', methods=['GET','POST'])
def sale_report():
    if request.method == 'GET':
        sale_data =None
        return render_template('/sale_report.html', sale_data = sale_data)
    else:

        s_date = request.form.get('s-date')
        e_date = request.form.get('e-date')

        start_date = str(s_date) +' 00:00:00'
        end_date = str(e_date) +' 23:59:59'

        print(f"s date {start_date}")
        print(f"s date {end_date}")
        conn = connect()
        cur = conn.cursor(dictionary=True, buffered=True)
        sql = """SELECT * ,
                        ROUND(od.qty * od.selling_price, 2) AS sale_total,
                        ROUND(ri.quantity * ri.original_price, 2) AS return_total
                        FROM sales
                left JOIN order_detail od  ON od.order_id = sales.s_order_id
                LEFT JOIN return_items ri ON ri.return_id = sales.invoice_number
                left JOIN orders o ON o.order_id = sales.s_order_id
                WHERE sales.transaction_date BETWEEN %s AND %s
                """
        cur.execute(sql,(start_date,end_date,))
        sale_data = cur.fetchall()
        cur.close()
        conn.close()

        conn = connect()
        cur = conn.cursor(dictionary=True, buffered=True)
        sql = """SELECT 
                    count(sales.total_amount) AS total_orders,
                    count(case when sales.transection_type = 'Sale' then sales.id  END) AS total_sale,

                    count(case when sales.transection_type = 'return' then sales.id  END) AS total_return,

                    SUM(case when sales.transection_type = 'sale' then sales.total_amount ELSE 0 END) AS sale_orders,
                    ROUND(SUM(case when sales.transection_type = 'return' then sales.total_amount ELSE 0 END),0) AS return_orders,

                    ROUND((
                    SUM(case when sales.transection_type = 'sale' then sales.total_amount ELSE 0 END) 
                    -
                    SUM(case when sales.transection_type = 'return' then sales.total_amount ELSE 0 END) 
                    ),0) AS Total_sale
                    FROM sales 
                WHERE sales.transaction_date BETWEEN %s AND %s
                """
        cur.execute(sql,(start_date,end_date,))
        sale_summary = cur.fetchall()
        cur.close()
        conn.close()




        return render_template('/sale_report.html', sale_data = sale_data, sale_summary=sale_summary)


@app.route('/stock_report')
def stock_report():

    if request.method=='GET':
        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql = """SELECT stock.item_id, stock.item_code, stock.item_name, stock.stock_quantity, i.pieces_per_pack, i.packs_per_unit from stock 
LEFT JOIN items i ON i.b_item_id = stock.b_item_id;
SELECT * FROM items;
"""
        cur.execute(sql)
        stock = cur.fetchall()
        cur.close()
        conn.close()


    return render_template('/stock_report.html', stock = stock)


@app.route('/stock_report_pdf')
@login_req
def stock_report_pdf(): 
        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql = """SELECT stock.item_id, stock.item_code, stock.item_name, stock.stock_quantity, i.pieces_per_pack, i.packs_per_unit ,
i.pieces_per_pack * i.packs_per_unit AS size,
ROUND(stock.stock_quantity /(i.pieces_per_pack * i.packs_per_unit),2) AS pack_left
from stock 
LEFT JOIN items i ON i.b_item_id = stock.b_item_id;
            """
        cur.execute(sql)
        stock = cur.fetchall()
        cur.close()
        conn.close()
        today = datetime.today()

    
    

        rendered = render_template('/stock_report_pdf.html',  stock = stock,today=today)
        html = HTML(string=rendered)  

        rendered_pdf = html.write_pdf()  
        return send_file(io.BytesIO(rendered_pdf), download_name='stock_report_pdf.pdf')


## Setup Section
#user Section

@app.route('/user_list')
def all_users():
    if request.method == 'GET':
        conn = connect()
        cur = conn.cursor(dictionary=True)
        sql = """SELECT 
    u.user_id,
    u.username, 
    u.email,  -- or other user details you need
    r.role_name,
    u.active,
    GROUP_CONCAT(p.permission_name) AS permissions  -- assuming permissions are in another table
FROM 
    users u
LEFT JOIN 
    user_roles ur ON u.user_id = ur.user_id
LEFT JOIN 
    roles r ON ur.role_id = r.role_id
LEFT JOIN 
    role_permissions rp ON r.role_id = rp.role_id
LEFT JOIN 
    permissions p ON rp.permission_id = p.permission_id
GROUP BY 
    u.user_id, u.username, u.email"""
        cur.execute(sql)
        result = cur.fetchall()
        cur.close()
        conn.close()


        return render_template('/user_list.html', data = result)
    

   

class UsernameValidation(object):
    def __init__(self, username = ''):
        self.username = username
    
    def __space(self):
        space = any(c.isspace() for c in self.username)
        return space       

    def validate(self):
        # lower = self.__lower()
        # upper = self.__upper()
        # digit = self.__digit()
        space = self.__space()
        length = len(self.username)
        # report =  lower and upper and digit and length >= 6
        if space == True:
            print("do not use space")
            return True  
        else:
            pass    

class PasswordValidation(object):
    def __init__(self, username = ''):
        self.username = username

    def __lower(self):
        lower = any(c.islower() for c in self.username)
        return lower

    def __upper(self):
        upper = any(c.isupper() for c in self.username)
        return upper

    def __digit(self):
        digit = any(c.isdigit() for c in  self.username)
        return digit
    
    def __space(self):
        space = any(c.isspace() for c in self.username)
        return space
       

    def validate(self):
        lower = self.__lower()
        upper = self.__upper()
        digit = self.__digit()
        space = self.__space()

        length = len(self.username)

        report =  lower and upper and digit and length >= 6
        if space == True:
            print("do not use space")
            return True
        
        elif report:
            print("Username passed all checks ")
            return True

        elif not lower:
            print("You didnt use Lower case letter")
            return False

        elif not upper:
            print("You didnt userUpper case letter")
            return False

        elif length <6:
            print("username should Atleast have 6 character")
            return False

        elif not digit:
            print("You didnt use Digit")
            return False  
        else:
            pass



@app.route('/create_user', methods=['POST', 'GET'])
def create_user():
    if request.method == 'GET':

 
        conn = connect()
        cur = conn.cursor(dictionary=True ,buffered=True)
        sql = "select * from roles;"
        cur.execute(sql)
        result = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('/create_user.html', result = result)
    
    else:
        username = request.form.get('username')
        email = request.form.get('email')
        user_passowrd = request.form.get('password')
        role = request.form.get('role') or None
        
        
        conn = connect()
        cur = conn.cursor(dictionary=True, buffered=True)
        sql = "SELECT * FROM users WHERE username = %s;"
        cur.execute(sql,(username,))
        username_exit = cur.rowcount
        
        
        cur.close()
        conn.close()
        print(username)

        conn = connect()
        cur = conn.cursor(dictionary=True, buffered=True)
        sql = "SELECT * FROM users WHERE email = %s;"
        cur.execute(sql,(email,))
        email_exit = cur.rowcount
        cur.close()
        conn.close()
        print(username)

        if email_exit > 0:
            flash("Email already Exist")
            return render_template('/create_user.html')
        
        if username_exit > 0:
            flash("User name already Exist")
            return render_template('/create_user.html')            
        
        username_check = UsernameValidation(username)
        password_check = PasswordValidation(user_passowrd)

        if password_check.validate():
                
                ph = argon2.PasswordHasher()
                hasshed = ph.hash(user_passowrd)
                
                conn = connect()
                cur = conn.cursor()
                sql = """INSERT INTO `users` (`username`, `password`, `email`) 
                        VALUES (%s, %s, %s);"""
                cur.execute(sql,(username,hasshed,email))
                conn.commit()
                cur.close()
                user_id_get = cur.lastrowid
                cur.close()
                conn.close()
                print(user_id_get)
                
                

                

                
                return redirect('update_user?user_id='+str(user_id_get))
                

        else:
            flash("Please Follow the password Rule")
            return render_template('/create_user.html')

    


@app.route('/update_user',methods=['GET', 'POST'])
def update_user():
            try:
                if request.method =='GET':
                    
                    user_id = request.args.get('user_id')
                    conn = connect()
                    cur = conn.cursor(dictionary=True ,buffered=True)
                    sql = """SELECT * FROM users u                           
                            WHERE u.user_id = %s; """
                    cur.execute(sql, (user_id,))
                    result = cur.fetchall()
                    cur.close()
                    conn.close()

                    conn = connect()
                    cur = conn.cursor(dictionary=True ,buffered=True)
                    sql = """SELECT * FROM users u 
                            JOIN user_roles ur ON ur.user_id = u.user_id                          
                            WHERE u.user_id = %s; """
                    cur.execute(sql, (user_id,))
                    user_role = cur.fetchall()
                    cur.close()
                    conn.close()

                    conn = connect()
                    cur = conn.cursor(dictionary=True, buffered=True)
                    sql2 = "select * from roles;"
                    cur.execute(sql2)
                    roles = cur.fetchall()
                    cur.close()
                    conn.close()               
                    

                    return render_template('/update_user.html',result = result, roles= roles, user_role=user_role)
                else:

                    from itertools import zip_longest
                    user_id = request.form.get('user_id')
                    user_password    = request.form.get('password')
                    role    = request.form.getlist('role') or None
                    active_status    = request.form.get('active','0') 
                    

                    

                     


                    if user_password and not role:
                        
                         
                        
                  
                            password_check = PasswordValidation(user_password)
                            
                            if password_check.validate():                       
                                ph = argon2.PasswordHasher()
                                hasshed = ph.hash(user_password) 
                                
                                    
                            
                                conn = connect()
                                cur = conn.cursor(dictionary=True, buffered=True)
                                sql = "UPDATE `users` SET `password`=%s WHERE  `user_id`=%s;"
                                cur.execute(sql,(hasshed,user_id))
                                conn.commit()
                                cur.close()
                                conn.close()
                                result = cur.rowcount
                                flash(f"Password updated ")
                                return redirect("update_user?user_id="+user_id) 
                            else:
                                flash("Please Follow the Password Rules")
                                return redirect("update_user?user_id="+user_id)
                            
                    else:
                            conn = connect()
                            cur = conn.cursor()
                            sql = """UPDATE `users` SET `active`=%s WHERE  `user_id`=%s;"""
                            cur.execute(sql,(active_status,user_id,))
                            conn.commit()
                            cur.close()
                            conn.close()
                        
                            
                            print(f"user id {user_id}")
                            print(f"role id {role}")
                            conn = connect()
                            cur = conn.cursor()   
                            sql3 = """DELETE FROM `user_roles` WHERE  `user_id`=%s;"""   
                            cur.execute(sql3,(user_id,)) 
                            conn.commit()
                            cur.close()
                            conn.close()
                            user_id_int = int(user_id)
                            # if role_id != None:
                            user_id_val = user_id  # assuming this is a single value
                            for role_id in role:  # assuming roles is a list of role IDs
                                val = (user_id_val, role_id)

                                conn = connect()
                                cur = conn.cursor()
                                sql2 = "INSERT INTO user_roles (user_id, role_id) VALUES  (%s, %s) ON DUPLICATE KEY UPDATE user_id = VALUES(user_id),  role_id = VALUES(role_id)"                
                                cur.execute(sql2, val,)
                                conn.commit()
                                cur.close()
                                conn.close()  
                            flash('Permission Updated') 
                            return redirect("update_user?user_id="+user_id)  
            finally:
                cur.close()
                conn.close() 



               
                

                

if __name__ == '__main__':
    app.run(debug=False)
