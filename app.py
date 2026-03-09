from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.sqlite3'  # Corrected configuration key and file name
app.config['SECRET_KEY'] = "random string"
db = SQLAlchemy(app)  # Corrected class name
migrate = Migrate(app, db)

class Customers(db.Model):  # Corrected class name and capitalization
    __tablename__ = 'customers'
    id = db.Column('customer_id', db.Integer, primary_key=True)  # Corrected column spelling and type
    name = db.Column(db.String(200))  # Corrected column type and spelling
    account_number = db.Column(db.Integer)  # Corrected column type and spelling
    account_type = db.Column(db.String(50))
    topups = db.relationship('Topups', backref='customer', lazy=True)

    def __init__(self, name, account_number, account_type):
        self.name = name
        self.account_number = account_number
        self.account_type = account_type

class Topups(db.Model):
    __tablename__ = 'topups'
    id = db.Column('topup_id', db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)

    def __init__(self, amount, customer_id):
        self.amount = amount
        self.customer_id = customer_id

@app.route('/')
def show_all():
    customers = Customers.query.all()
    return render_template('show_all.html', customers=customers)

@app.route('/new_customer', methods=['GET', 'POST'])
def new_customer():
    if request.method == 'POST':
        if not request.form['name'] or not request.form['account_number'] or not request.form.get('account_type'):
            flash('Please enter all the fields', 'error')
        else:
            customer = Customers(
                request.form['name'],
                request.form['account_number'],
                request.form['account_type']
            )
            db.session.add(customer)
            db.session.commit()  # Fixed typo in commit
            flash('Record was successfully added')
            return redirect(url_for('show_all'))
    return render_template('new_customer.html')

@app.route('/edit_customer/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    customer = Customers.query.get_or_404(customer_id)
    if request.method == 'POST':
        if not request.form['name'] or not request.form['account_number'] or not request.form.get('account_type'):
            flash('Please enter all the fields', 'error')
        else:
            customer.name = request.form['name']
            customer.account_number = request.form['account_number']
            customer.account_type = request.form['account_type']
            db.session.commit()
            flash('Record was successfully updated')
            return redirect(url_for('show_all'))
    return render_template('edit_customer.html', customer=customer)

@app.route('/topups/<int:customer_id>')
def show_topups(customer_id):
    customer = Customers.query.get_or_404(customer_id)
    return render_template('show_topups.html', customer=customer, topups=customer.topups)

@app.route('/new_topup/<int:customer_id>', methods=['GET', 'POST'])
def new_topup(customer_id):
    customer = Customers.query.get_or_404(customer_id)
    if request.method == 'POST':
        if not request.form['amount']:
            flash('Please enter the amount', 'error')
        else:
            try:
                amount = float(request.form['amount'])
                topup = Topups(amount=amount, customer_id=customer.id)
                db.session.add(topup)
                db.session.commit()
                flash('Topup was successfully added')
                return redirect(url_for('show_topups', customer_id=customer.id))
            except ValueError:
                flash('Invalid amount entered', 'error')
    return render_template('new_topup.html', customer=customer)

@app.route('/edit_topup/<int:topup_id>', methods=['GET', 'POST'])
def edit_topup(topup_id):
    topup = Topups.query.get_or_404(topup_id)
    if request.method == 'POST':
        amount = request.form.get('amount')
        created_at_str = request.form.get('created_at')
        if not amount or not created_at_str:
            flash('Please enter all the fields', 'error')
        else:
            try:
                topup.amount = float(amount)
                topup.created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M')
                db.session.commit()
                flash('Topup successfully updated')
                return redirect(url_for('show_topups', customer_id=topup.customer_id))
            except ValueError:
                flash('Invalid amount or date format', 'error')
    
    return render_template('edit_topup.html', topup=topup)

@app.route('/all_topups')
def all_topups():
    # Query all topups joined with their respective customers, ordered by newest first
    topups = db.session.query(Topups, Customers).join(Customers).order_by(Topups.created_at.desc()).all()
    
    # Filter for today's topups
    today = datetime.now().date()
    today_topups = [t for t in topups if t[0].created_at.date() == today]

    return render_template('all_topups.html', topups=topups, today_topups=today_topups)

@app.route('/statistics')
def statistics():
    # Group by customer
    customer_query = db.session.query(
        Customers.name,
        func.count(Topups.id).label('total_count'),
        func.sum(Topups.amount).label('total_amount')
    ).join(Topups)
    customer_stats = customer_query.group_by(Customers.id).all()

    # Aggregate by Day
    daily_query = db.session.query(
        func.strftime('%Y-%m-%d', Topups.created_at).label('period'),
        func.count(Topups.id).label('total_count'),
        func.sum(Topups.amount).label('total_amount')
    ).join(Customers, Topups.customer_id == Customers.id)
    daily_stats = daily_query.group_by('period').order_by('period').all()
    
    # Aggregate by Month
    monthly_query = db.session.query(
        func.strftime('%Y-%m', Topups.created_at).label('period'),
        func.count(Topups.id).label('total_count'),
        func.sum(Topups.amount).label('total_amount')
    ).join(Customers, Topups.customer_id == Customers.id)
    monthly_stats = monthly_query.group_by('period').order_by('period').all()

    # Aggregate by Year
    yearly_query = db.session.query(
        func.strftime('%Y', Topups.created_at).label('period'),
        func.count(Topups.id).label('total_count'),
        func.sum(Topups.amount).label('total_amount')
    ).join(Customers, Topups.customer_id == Customers.id)
    yearly_stats = yearly_query.group_by('period').order_by('period').all()

    # Aggregate by Account Type & Date
    account_type_query = db.session.query(
        func.strftime('%Y-%m-%d', Topups.created_at).label('period'),
        Customers.account_type.label('type_name'),
        func.count(Topups.id).label('total_count'),
        func.sum(Topups.amount).label('total_amount')
    ).join(Customers, Topups.customer_id == Customers.id)
    account_type_stats = account_type_query.group_by('period', Customers.account_type).order_by(db.desc('period')).all()

    return render_template('statistics.html', 
                           customer_stats=customer_stats,
                           daily_stats=daily_stats,
                           monthly_stats=monthly_stats,
                           yearly_stats=yearly_stats,
                           account_type_stats=account_type_stats)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created within the application context
    app.run(debug=True, host='0.0.0.0',port=80)
