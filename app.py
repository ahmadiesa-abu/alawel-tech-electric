from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.sqlite3'  # Corrected configuration key and file name
app.config['SECRET_KEY'] = "random string"
db = SQLAlchemy(app)  # Corrected class name

class Customers(db.Model):  # Corrected class name and capitalization
    id = db.Column('customer_id', db.Integer, primary_key=True)  # Corrected column spelling and type
    name = db.Column(db.String(200))  # Corrected column type and spelling
    account_number = db.Column(db.Integer)  # Corrected column type and spelling

    def __init__(self, name, account_number):
        self.name = name
        self.account_number = account_number

@app.route('/')
def show_all():
    return render_template('show_all.html', customers=Customers.query.all())  # Corrected template rendering

@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        if not request.form['name'] or not request.form['account_number']:
            flash('Please enter all the fields', 'error')
        else:
            customer = Customers(
                request.form['name'],
                request.form['account_number'],
            )
            db.session.add(customer)
            db.session.commit()  # Fixed typo in commit
            flash('Record was successfully added')
            return redirect(url_for('show_all'))
    return render_template('new.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created within the application context
    app.run(debug=True)
