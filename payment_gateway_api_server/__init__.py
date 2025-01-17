# libs
import datetime
import json
import requests
from flask import Flask, render_template, request
from werkzeug.datastructures import ImmutableOrderedMultiDict

# setup Flask App and configure with sitetree, defaults, and context_processor
app = Flask(__name__)
with app.open_resource('data/tree.json') as f:
    app.config['SITETREE'] = json.load(f)

with app.open_resource('data/api_defaults.json') as f:
    app.config['APIDEFAULTS'] = json.load(f)

@app.context_processor
def inject_datetime():
    return {'datetime': datetime.datetime.today()}

# build route decorators
@app.route('/paypal/ipn/',methods=['POST'])
def ipn():
    try:
        arg = ''
        request.parameter_storage_class = ImmutableOrderedMultiDict
        values = request.form
        for x, y in values.iteritems():
            arg += "&{x}={y}".format(x=x,y=y)

        validate_url = 'https://www.sandbox.paypal.com' \
                       '/cgi-bin/webscr?cmd=_notify-validate{arg}' \
                       .format(arg=arg)
        r = requests.get(validate_url)
        if r.text == 'VERIFIED':
            try:
                payer_email =  thwart(request.form.get('payer_email'))
                unix = int(time.time())
                payment_date = thwart(request.form.get('payment_date'))
                username = thwart(request.form.get('custom'))
                last_name = thwart(request.form.get('last_name'))
                payment_gross = thwart(request.form.get('payment_gross'))
                payment_fee = thwart(request.form.get('payment_fee'))
                payment_net = float(payment_gross) - float(payment_fee)
                payment_status = thwart(request.form.get('payment_status'))
                txn_id = thwart(request.form.get('txn_id'))
            except Exception as e:
                with open('/tmp/ipnout.txt','a') as f:
                    data = 'ERROR WITH IPN DATA\n'+str(values)+'\n'
                    f.write(data)

            with open('/tmp/ipnout.txt','a') as f:
                data = 'SUCCESS\n'+str(values)+'\n'
                f.write(data)

            c,conn = connection()
            c.execute("INSERT INTO ipn (unix, payment_date, username, last_name, payment_gross, payment_fee, payment_net, payment_status, txn_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (unix, payment_date, username, last_name, payment_gross, payment_fee, payment_net, payment_status, txn_id))
            conn.commit()
            c.close()
            conn.close()
            gc.collect()

        else:
             with open('/tmp/ipnout.txt','a') as f:
                data = 'FAILURE\n'+str(values)+'\n'
                f.write(data)

        return r.text
    except Exception as e:
        return str(e)

@app.route('/')
def root_index():
    try:
        return render_template("index.html")
    except Exception as e:
        return(str(e))

@app.route('/paypal/')
def paypal_index():
    try:
        #print(request.path)
        return render_template("paypal/index.html")
    except Exception as e:
        return(str(e))

@app.route('/paypal/subscribe/', methods=['GET', 'POST'])
def paypal_subscribe():
    return render_template("paypal/subscribe.html")

@app.route('/paypal/smart_button/', methods=['GET', 'POST'])
def paypal_smart_button():
    try:
        return render_template("paypal/smart_button.html")
    except Exception as e:
        return(str(e))

@app.route('/paypal/callback/smart_button', methods=['GET', 'POST', 'OPTIONS'])
def paypal_callback_smart_button():
    try:
        print(request.values)
        print(request.form)
        return('SUCCESS', 201)
    except Exception as e:
        return(str(e))
