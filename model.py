from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo
from bson.objectid import ObjectId
import datetime
from schemas.budgetSchema import BudgetSchema
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Budget:
    schema = BudgetSchema()

    @staticmethod
    def set_budget(user_id, amount, period='monthly'):
        data = {
            'user_id': user_id,
            'amount': amount,
            'period': period
        }
        errors = Budget.schema.validate(data)
        if errors:
            raise ValueError(str(errors))
        
        budget = {
            'user_id': ObjectId(user_id),
            'amount': amount,
            'period': period
        }
        return mongo.db.budgets.update_one(
            {'user_id': ObjectId(user_id)},
            {'$set': budget},
            upsert=True
        )

    @staticmethod
    def get_budgets(user_id):
        return mongo.db.budgets.find({'user_id': ObjectId(user_id)})

    @staticmethod
    def check_budget_alert(user_id):
        budget = mongo.db.budgets.find_one({'user_id': ObjectId(user_id)})
        if not budget:
            return None

        now = datetime.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        total_spent = mongo.db.daily_expenses.aggregate([
            {'$match': {
                'user_id': ObjectId(user_id),

                'date': {'$gte': start_of_month}
            }},
            {'$group': {
                '_id': None,
                'total': {'$sum': '$amount'}
            }}
        ]).next()['total']

        percentage_used = (total_spent / budget['amount']) * 100
        if percentage_used >= 80:
            return f"Alert: You've used {percentage_used:.2f}% of your budget for this category."
        return None


# from schemas.categorySchema import CategorySchema


# class Category:
#     schema = CategorySchema()

#     @staticmethod
#     def add_category(name, user_id):
#         data = {'name': name, 'user_id': user_id}
#         errors = Category.schema.validate(data)
#         if errors:
#             raise ValueError(str(errors))
        
#         category = {
#             'name': name,
#             'user_id': ObjectId(user_id)
#         }
#         return mongo.db.categories.insert_one(category).inserted_id

#     @staticmethod
#     def get_categories_by_user(user_id):
#         return mongo.db.categories.find({'user_id': ObjectId(user_id)})

from schemas.dailyExpenseSchema import DailyExpenseSchema

class DailyExpense:
    schema = DailyExpenseSchema()

    def __init__(self, description, amount, user_id, date=None):
        self.description = description
        self.amount = amount
        self.user_id = user_id
        self.date = date if date else datetime.now().date()

    @staticmethod
    def add_daily_expense(data):
        # errors = DailyExpense.schema.validate(data)
        # if errors:
        #     raise ValueError(str(errors))
        
        data['date'] = data.get('date', datetime.now().date())
        data['user_id'] = ObjectId(data['user_id'])
        data['category_id'] = data.get('category_id')
        return mongo.db.daily_expenses.insert_one(data).inserted_id
    
    @staticmethod
    def get_daily_expenses_by_username(username):
        user = mongo.db.users.find_one({'username': username})
        if not user:
            raise ValueError('User not found')
        user_id = user['_id']
        return mongo.db.daily_expenses.find({'user_id': user_id})

import gridfs

class Receipt:
    @staticmethod
    def add_receipt(expense_id, file):
        fs = gridfs.GridFS(mongo.db)
        file_id = fs.put(file, filename=file.filename)
        mongo.db.daily_expenses.update_one(
            {'_id': ObjectId(expense_id)},
            {'$set': {'receipt_id': file_id}}
        )
        return file_id

    @staticmethod
    def get_receipt(expense_id):
        expense = mongo.db.daily_expenses.find_one({'_id': ObjectId(expense_id)})
        if 'receipt_id' in expense:
            fs = gridfs.GridFS(mongo.db)
            return fs.get(expense['receipt_id'])
        return None

from schemas.recurringSchema import RecurringExpenseSchema


class RecurringExpense:
    schema = RecurringExpenseSchema()

    @staticmethod
    def add_recurring_expense(data):
        errors = RecurringExpense.schema.validate(data)
        if errors:
            raise ValueError(str(errors))
        
        data['user_id'] = ObjectId(data['user_id'])
        data['start_date'] = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        data['next_date'] = data['start_date']
        return mongo.db.recurring_expenses.insert_one(data).inserted_id

    @staticmethod
    def get_recurring_expenses(user_id):
        return mongo.db.recurring_expenses.find({'user_id': ObjectId(user_id)})

    @staticmethod
    def process_recurring_expenses():
        today = datetime.now().date()
        recurring_expenses = mongo.db.recurring_expenses.find({
            'next_date': {'$lte': today}
        })

        for expense in recurring_expenses:
            DailyExpense.add_daily_expense({
                'description': expense['description'],
                'amount': expense['amount'],
                'user_id': expense['user_id'],
                'date': today
            })

            if expense['frequency'] == 'daily':
                next_date = today + timedelta(days=1)
            elif expense['frequency'] == 'weekly':
                next_date = today + timedelta(weeks=1)
            elif expense['frequency'] == 'monthly':
                next_date = today + relativedelta(months=1)
            elif expense['frequency'] == 'yearly':
                next_date = today + relativedelta(years=1)

            mongo.db.recurring_expenses.update_one(
                {'_id': expense['_id']},
                {'$set': {'next_date': next_date}}
            )

class Report:
    @staticmethod
    def get_expense_summary(user_id, start_date, end_date):
        pipeline = [
            {'$match': {
                'user_id': ObjectId(user_id),
                'date': {'$gte': start_date, '$lte': end_date}
            }},
            {'$group': {
                'total': {'$sum': '$amount'}
            }}
        ]
        return mongo.db.daily_expenses.aggregate(pipeline)

    @staticmethod
    def get_spending_trend(user_id, start_date, end_date):
        pipeline = [
            {'$match': {
                'user_id': ObjectId(user_id),
                'date': {'$gte': start_date, '$lte': end_date}
            }},
            {'$group': {
                '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$date'}},
                'total': {'$sum': '$amount'}
            }},
            {'$sort': {'_id': 1}}
        ]
        return mongo.db.daily_expenses.aggregate(pipeline)

from schemas.sharedSchema import SharedExpenseSchema

class SharedExpense:
    schema = SharedExpenseSchema()

    def __init__(self, description, amount, split_type, user_id, participants, date=None, bill_photo=None):
        self.description = description
        self.amount = amount
        self.split_type = split_type
        self.user_id = user_id
        self.participants = participants
        self.date = date if date else datetime.now().date()
        self.bill_photo = bill_photo

    @staticmethod
    def add_shared_expense(data):
        # errors = SharedExpense.schema.validate(data)
        # if errors:
        #     raise ValueError(str(errors))
        
        data['date'] = data.get('date', datetime.now().date())
        data['user_id'] = ObjectId(data['user_id'])
        data['participants'] = [ObjectId(p) for p in data['participants']]
        return mongo.db.shared_expenses.insert_one(data).inserted_id

    @staticmethod
    def get_shared_expenses_by_user(user_id):
        return mongo.db.shared_expenses.find({"user_id": ObjectId(user_id)})

    @staticmethod
    def get_shared_expenses_by_date(user_id, date):
        return mongo.db.shared_expenses.find({"user_id": ObjectId(user_id), "date": date})

from schemas.userSchema import UserSchema

class User:
    schema = UserSchema()

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)

    @staticmethod
    def add_user(username, email, password):
        data = {'username': username, 'email': email, 'password': password}
        errors = User.schema.validate(data)
        if errors:
            raise ValueError(str(errors))
        
        user = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password)
        }
        return mongo.db.users.insert_one(user).inserted_id

    @staticmethod
    def get_user_by_username(username):
        return mongo.db.users.find_one({'username': username})

    @staticmethod
    def check_password(username, password):
        user = User.get_user_by_username(username)
        if user:
            return check_password_hash(user['password_hash'], password)
        return False