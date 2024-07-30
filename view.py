from flask import Flask, request, jsonify, session, redirect, url_for, send_file
from marshmallow import ValidationError
from werkzeug.utils import secure_filename
from io import StringIO
import csv
import os
from datetime import datetime
from bson.objectid import ObjectId
from model import Budget
from model import DailyExpense
from database import mongo
from flask import Blueprint, request, jsonify

# app = Flask(__name__)

view = Blueprint('view', __name__)

@view.route('/')
def home():
    return 'Welcome to the homepage!'


@view.route('/budgets', methods=['POST'])
def set_budget():
    data = request.json
    try:
        Budget.set_budget(data['user_id'], data['amount'], data.get('period', 'monthly'))
        return jsonify({'message': 'Budget set successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

        
@view.route('/budgets/<user_id>', methods=['GET'])
def get_budgets(user_id):
    budgets = Budget.get_budgets(user_id)
    budget_list = list(budgets)
    for budget in budget_list:
        budget['_id'] = str(budget['_id'])
        budget['user_id'] = str(budget['user_id'])
    return jsonify(budget_list), 200

@view.route('/budget/alert/<user_id>', methods=['GET'])
def get_budget_alert(user_id):
    try:
        alert = Budget.check_budget_alert(user_id)
        if alert:
            return jsonify({'alert': alert}), 200
        else:
            return jsonify({'message': 'No budget alert at this time'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500




# @view.route('/categories', methods=['POST'])
# def add_category():
#     data = request.json
#     try:
#         category_id = Category.add_category(data['name'], data['user_id'])
#         return jsonify({'message': 'Category added successfully', 'category_id': str(category_id)}), 201
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400
        
# @view.route('/categories/user/<user_id>', methods=['GET'])
# def get_categories_by_user(user_id):
#     categories = Category.get_categories_by_user(user_id)
#     category_list = list(categories)
#     for category in category_list:
#         category['_id'] = str(category['_id'])
#     return jsonify(category_list), 200

@view.route('/daily_expenses', methods=['POST'])
def add_daily_expense():
    data = request.get_json()
    try:
        daily_expense_id = DailyExpense.add_daily_expense(data)
        return jsonify({'message': 'Daily expense added successfully', 'expense_id': str(daily_expense_id)}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
        
@view.route('/daily_expenses/user/<user_id>', methods=['GET'])
def get_daily_expenses_by_user(user_id):
    expenses = DailyExpense.get_daily_expenses_by_user(user_id)
    expense_list = list(expenses)
    for expense in expense_list:
        expense['_id'] = str(expense['_id'])
    return jsonify(expense_list), 200

from io import BytesIO

@view.route('/export/<username>', methods=['GET'])
def export_expenses(username):
    try:
        # Fetch expenses based on username
        expenses = DailyExpense.get_daily_expenses_by_username(username)
        
        # Create an in-memory text file object
        output = StringIO()
        writer = csv.writer(output)
        
        # Write CSV headers
        writer.writerow(['Date', 'Description', 'Amount'])
        for expense in expenses:
            # Check if date is a string and convert to datetime
            if isinstance(expense['date'], str):
                try:
                    date_obj = datetime.strptime(expense['date'], '%Y-%m-%d')
                except ValueError:
                    date_obj = 'Invalid Date'
            else:
                date_obj = expense['date']
                
            # Write expense data to CSV
            writer.writerow([
                date_obj.strftime('%Y-%m-%d') if isinstance(date_obj, datetime) else date_obj,
                expense['description'],
                expense['amount']
            ])
        
        # Get the value of the StringIO object
        output.seek(0)
        csv_data = output.getvalue()
        
        # Convert the string data to bytes
        csv_bytes = csv_data.encode('utf-8')
        
        # Create a BytesIO object
        bytes_io = BytesIO(csv_bytes)
        
        # Send the file as a response
        return send_file(
            bytes_io,
            mimetype='text/csv',
            as_attachment=True,
            download_name='expenses.csv'
        )
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500




@view.route('/import/<user_id>', methods=['POST'])
def import_expenses(user_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.csv'):
        csv_file = StringIO(file.read().decode('utf-8'))
        reader = csv.DictReader(csv_file)
        for row in reader:
            
            DailyExpense.add_daily_expense({
                'description': row['Description'],
                'amount': float(row['Amount']),
                'user_id': ObjectId(user_id),
                'date': datetime.strptime(row['Date'], '%Y-%m-%d').date()
            })
        return jsonify({'message': 'Expenses imported successfully'}), 200
    return jsonify({'error': 'Invalid file format'}), 400


from model import Receipt


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@view.route('/upload_receipt/<expense_id>', methods=['POST'])
def upload_receipt(expense_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_id = Receipt.add_receipt(expense_id, file)
        return jsonify({'message': 'Receipt uploaded successfully', 'file_id': str(file_id)}), 200
    return jsonify({'error': 'Invalid file format'}), 400

@view.route('/get_receipt/<expense_id>')
def get_receipt(expense_id):
    receipt = Receipt.get_receipt(expense_id)
    if receipt:
        return send_file(receipt, attachment_filename=receipt.filename)
    return jsonify({'error': 'Receipt not found'}), 404

from model import RecurringExpense

@view.route('/recurring_expenses', methods=['POST'])
def add_recurring_expense():
    data = request.json
    try:
        recurring_expense_id = RecurringExpense.add_recurring_expense(data)
        return jsonify({'message': 'Recurring expense added successfully', 'expense_id': str(recurring_expense_id)}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
        
@view.route('/recurring_expenses/<user_id>', methods=['GET'])
def get_recurring_expenses(user_id):
    expenses = RecurringExpense.get_recurring_expenses(user_id)
    expense_list = list(expenses)
    for expense in expense_list:
        expense['_id'] = str(expense['_id'])
        expense['user_id'] = str(expense['user_id'])
    return jsonify(expense_list), 200

# You'll need to set up a scheduled task to run this function daily
def daily_recurring_expense_check():
    RecurringExpense.process_recurring_expenses()

from model import Report

@view.route('/reports/summary/<user_id>', methods=['GET'])
def get_expense_summary(user_id):
    start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
    summary = Report.get_expense_summary(user_id, start_date, end_date)
    return jsonify(list(summary)), 200

@view.route('/reports/trend/<user_id>', methods=['GET'])
def get_spending_trend(user_id):
    start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
    trend = Report.get_spending_trend(user_id, start_date, end_date)
    return jsonify(list(trend)), 200


from model import SharedExpense
from utils import allowed_file
from schemas import sharedSchema

@view.route('/shared_expenses', methods=['POST'])
def add_shared_expense():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Invalid or missing JSON data.'}), 400
        
        # Use the data directly without validation
        user_id = data.get('user_id')
        participants = data.get('participants', [])
        split_type = data.get('split_type', 'equal').lower()
        total_amount = float(data.get('amount', 0))
        
        # Convert ObjectIds
        try:
            user_id = ObjectId(user_id)
            participants = [ObjectId(p) for p in participants]

        except Exception as e:
            return jsonify({'error': f"Invalid ObjectId format: {e}"}), 400
        
        # Insert shared expense
        data['user_id'] = user_id
        data['participants'] = participants
        shared_expense_id = SharedExpense.add_shared_expense(data)
        
        # Handle split calculations
        if split_type == 'equal':
            if not participants:
                return jsonify({'error': 'No participants provided for equal split.'}), 400
            individual_share = total_amount / len(participants)
            shares = {str(participant): individual_share for participant in participants}
        elif split_type == 'percentage':
            participant_shares = data.get('participant_shares', [])
            if not participant_shares:
                return jsonify({'error': 'No participant shares provided for percentage split.'}), 400
            shares = {}
            for participant in participant_shares:
                participant_id = participant.get('user_id')
                percentage = float(participant.get('percentage', 0)) / 100
                shares[participant_id] = total_amount * percentage
        elif split_type == 'fixed':
            fixed_shares = data.get('participant_shares', [])
            if not fixed_shares:
                return jsonify({'error': 'No fixed shares provided for fixed split.'}), 400
            shares = {}
            for share in fixed_shares:
                participant_id = share.get('user_id')
                shares[participant_id] = float(share.get('amount', 0))
        else:
            return jsonify({'error': 'Invalid split type.'}), 400
        
        # Add daily expenses for each participant
        for participant_id, share in shares.items():
            daily_expense_data = {
                'description': data['description'],
                'amount': share,
                'user_id': participant_id,
                'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
            }
            DailyExpense.add_daily_expense(daily_expense_data)
        
        return jsonify({
            'message': 'Shared expense added successfully and recorded as daily expenses',
            'expense_id': str(shared_expense_id)
        }), 201

    except Exception as e:
        # app.logger.error(f'Unexpected error in add_shared_expense: {str(e)}')
        return jsonify({'error': 'An unexpected error occurred'}), 500



@view.route('/shared_expenses/user/<user_id>', methods=['GET'])
def get_shared_expenses_by_user(user_id):
    expenses = SharedExpense.get_shared_expenses_by_user(user_id)
    expense_list = list(expenses)
    for expense in expense_list:
        expense['_id'] = str(expense['_id'])
    return jsonify(expense_list), 200

@view.route('/shared_expenses/user/<user_id>/date/<date>', methods=['GET'])
def get_shared_expenses_by_date(user_id, date):
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    expenses = SharedExpense.get_shared_expenses_by_date(user_id, date_obj)
    expense_list = list(expenses)
    for expense in expense_list:
        expense['_id'] = str(expense['_id'])
    return jsonify(expense_list), 200

from model import User

import logging




@view.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        # Check if required fields are present
        if 'username' not in data or 'email' not in data or 'password' not in data:
            raise ValueError("Missing required fields: 'username', 'email', and 'password'")

        # Add user and get the user ID
        user_id = User.add_user(data['username'], data['email'], data['password'])

        # Return success message with user ID
        return jsonify({'message': 'User registered successfully', 'user_id': str(user_id)}), 201

    except ValueError as e:
        logging.error(f"ValueError: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500
        
@view.route('/login', methods=['POST'])
def login():
    data = request.json
    if User.check_password(data['username'], data['password']):
        session['username'] = data['username']
        return jsonify({'message': 'Logged in successfully'}), 200
    return jsonify({'message': 'Invalid username or password'}), 401

@view.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))