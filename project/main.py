from flask import flash,Flask,render_template, redirect, url_for, request

import buildsql
import buildfirebase
import c_search
import r_search
import pymysql
def add_to_db(table, data):
    conn =  pymysql.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = 'Dsci-551',charset = 'utf8',db = 'project')
    cursor = conn.cursor(cursor = pymysql.cursors.DictCursor)
    
    insert_mysql ='insert into '+str(table)+' values('
    for s in data:
        insert_mysql += '"'+str(s)+'"'+','
    insert_mysql = insert_mysql[:-1]+')'
    print(insert_mysql)
    cursor.execute(insert_mysql)
    conn.commit()

    cursor.close()
    conn.close()

conn =  pymysql.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = 'Dsci-551',charset = 'utf8',db = 'project')
cursor = conn.cursor(cursor = pymysql.cursors.DictCursor)

select_mysql ='select * from account' 
cursor.execute(select_mysql)
data_list = cursor.fetchall()
tmp = {}
for data in data_list:
    tmp[data['email_address']] = (data['password'], data['user_name'])
acount_dic = tmp

cursor.close()
conn.close()

conn =  pymysql.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = 'Dsci-551',charset = 'utf8',db = 'project')
cursor = conn.cursor(cursor = pymysql.cursors.DictCursor)

select_mysql ='select * from house' 
cursor.execute(select_mysql)
house_list = cursor.fetchall()

cursor.close()
conn.close()

cri = buildfirebase.cat('/user/vincent/Crime.csv')
restaurant = buildfirebase.cat('/user/vincent/Restaurant.csv')


def filter(col, hold, data):
    if col == 'price':
        return [d for d in data if hold[0] <= float(d['mostRecentPriceAmount']) <= hold[1]]
    elif col == 'nbed':
        return [d for d in data if float(d['numBedroom']) >= hold]
    elif col == 'nbath':
        return [d for d in data if float(d['numBathroom']) >= hold]
    else:
        return [d for d in data if float(d['yearBuilt']) >= hold]


app = Flask(__name__ )

@app.route('/', methods = ['GET', 'POST'])
def home():
    msg = ''
    if request.method == 'POST':
        print(request.form)
        if len(request.form) == 2:
            p = request.form.get('password')
            e = request.form.get('email')
            if e not in acount_dic:
                msg = 'invalid email'
            elif p != acount_dic[e][0]:
                msg = 'invalid password'
            else:
                msg = 'Success Login'
                return redirect(url_for('monitor'))
            return render_template('sign_in.html', msg=msg)
        else:
            u = request.form.get('user_name')
            p = request.form.get('password')
            e = request.form.get('email')
            if not e:
                msg = 'Email Can not be empty'
            else:
                msg = 'Success Sign Up'
                add_to_db('account', [u, e, p]) 
        #return redirect(url_for('login'))
    return render_template('sign_up.html', msg=msg)

import pandas as pd

@app.route('/display', methods = ['GET', 'POST'])
def monitor():
    cr = pd.DataFrame.copy(cri, deep=True)
    re = pd.DataFrame.copy(restaurant, deep=True)
    if request.method == 'POST':
        data = []

        data[:] = house_list[:]
        if request.form.get('MiP'):
            data = filter('price', [float(request.form.get('MiP')), float('inf')],data)
        if request.form.get('MaP'):
            data = filter('price',[float('-inf'), float(request.form.get('MaP'))], data)
        if request.form.get('Bath'):
            cr = c_search.find_crime_by_keyword(str(request.form.get('Bath')))
        if request.form.get('Bed'):
            re = r_search.find_restaurant_by_type(str(request.form.get('Bed')))
        if len(cr.columns) != 0: 
            cr.columns = ['area', 'desc', 'date', 'id', 'LAT', 'location', 'LON', 'timeocc']
        cr = cr.to_dict('records')
        re = re.to_dict('records')
        return render_template('display.html', house_list=data, crime = cr, restaurant=re)
    if len(cr.columns) != 0:
        cr.columns = ['area', 'desc', 'date', 'id', 'LAT', 'location', 'LON', 'timeocc']
    cr = cr.to_dict('records')
    re = re.to_dict('records')
  
    return render_template('display.html', house_list=house_list, crime=cr, restaurant=re)

@app.route('/analysis')
def analysis():
    return render_template('Analysis.html')

@app.route('/manage', methods = ['GET', 'POST'])
def manage():
    if request.method=='POST':
        output = ''
        if not request.form.get('db') or not request.form.get('operation'):
            return render_template('Manage.html')
        
        if request.form.get('db') == '1':
            if request.form.get('operation') == '1':
                output = buildsql.ls(request.form.get('inp'))
            elif request.form.get('operation') == '2':
                output = buildsql.mkdir(request.form.get('inp'))

            elif request.form.get('operation') == '3':
                output = buildsql.cat(request.form.get('inp'))
            elif request.form.get('operation') == '4':
                output = buildsql.rm(request.form.get('inp'))
            elif request.form.get('operation') == '5':
                inp = request.form.get('inp').split(',')
                output = buildsql.put(inp[0],inp[1],int(inp[2]))
            elif request.form.get('operation') == '6':
                output = buildsql.getPartitionLocations(request.form.get('inp'))
            elif request.form.get('operation') == '7':
                inp = request.form.get('inp').split(',')
                output = buildsql.readPartition(inp[0],int(inp[1]))
        else:
            if request.form.get('operation') == '1':
                output = buildfirebase.ls(request.form.get('inp'))
            elif request.form.get('operation') == '2':
                output = buildfirebase.mkdir(request.form.get('inp'))

            elif request.form.get('operation') == '3':
                output = buildfirebase.cat(request.form.get('inp'))
            elif request.form.get('operation') == '4':
                output = buildfirebase.rm(request.form.get('inp'))
            elif request.form.get('operation') == '5':
                inp = request.form.get('inp').split(',')
                output = buildfirebase.put(inp[0], inp[1], int(inp[2]))
            elif request.form.get('operation') == '6':
                output = buildfirebase.getPartitionLocations(request.form.get('inp'))
            elif request.form.get('operation') == '7':
                inp = request.form.get('inp').split(',')
                output = buildfirebase.readPartition(inp[0], int(inp[1]))
 
        if isinstance(output, list):
            output = '                     '.join(output)
        if isinstance(output, str):
            nn ='1'
        else:
            nn ='2'
        if nn == '2':
            output = output.to_dict('records')
            output = [' '.join([str(s) for s in list(i.values())]) for i in output]
        return render_template('Manage.html', outp = output, nn = nn)
        print(request.form.get('db'), request.form.get('operation'), request.form.get('inp'))
    return render_template('Manage.html', outp = '123', nn ='3')

if __name__ == '__main__':

    app.run(host = '0.0.0.0', port = 5000)

