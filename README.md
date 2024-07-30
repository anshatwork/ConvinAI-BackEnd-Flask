#  Expense Tracker

## Overview
This Expense Tracker is a Flask-based web application that helps users manage their daily expenses, recurring expenses, shared expenses, and track their budgets. It provides features for recording various types of expenses, setting budgets, and receiving alerts when approaching budget limits.

## Features
- User registration and authentication
- Daily expense logging
- Recurring expense management
- Shared expense tracking
- Budget setting and tracking
- Budget alerts
- Expense export to CSV

## Installation

1. Clone the repository:
2. Set up a virtual environment:
3. Install dependencies:
4. Set up environment variables:
Create a `.env` file in the root directory and add:
MONGO_URI=your_mongodb_connection_string
SECRET_KEY=your_secret_key

## Running the Application

Start the Flask development server:
The application will be available at `http://localhost:5000`.

## API Endpoints

### User Management
- `POST /register`: Register a new user
- `POST /login`: User login

### Expense Management
- `POST /expenses`: Add a new expense
- `GET /expenses/<user_id>`: Get all expenses for a user
- `GET /export/<user_id>`: Export user expenses to CSV

### Recurring Expenses
- `POST /recurring-expenses`: Set up a recurring expense
- `GET /recurring-expenses/<user_id>`: Get all recurring expenses for a user
- `PUT /recurring-expenses/<expense_id>`: Update a recurring expense
- `DELETE /recurring-expenses/<expense_id>`: Delete a recurring expense

### Shared Expenses
- `POST /shared-expenses`: Add a new shared expense
- `GET /shared-expenses/<user_id>`: Get all shared expenses for a user
- `PUT /shared-expenses/<expense_id>`: Update a shared expense
- `DELETE /shared-expenses/<expense_id>`: Delete a shared expense

### Budget Management
- `POST /budgets`: Set a budget for a user
- `GET /budget/alert/<username>`: Check for budget alerts

## Testing

To run the tests:
1. Ensure the Flask application is running
2. Execute the test script: ( PS: Can elaborate further )

## Future Enhancements
- Implement expense categories
- Add data visualization for expense trends
- Create a user-friendly frontend interface
- Implement multi-currency support
- Integrate JWT for enhanced authentication

## Contributing
Contributions to improve the application are welcome. Please follow these steps:
1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes and commit (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request


## Contact
For any queries or support, please contact [ansh.work2002@gmail.com]. 
