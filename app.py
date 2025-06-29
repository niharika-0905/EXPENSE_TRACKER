#app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import numpy as np

app = Flask(__name__)
CORS(app)  # To allow cross-origin requests from frontend

DB_NAME = 'expenses.db'

# Initialize DB with a table
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/expense_all', methods=['GET'])
def get_expenses():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, category, amount, description, date FROM expenses ORDER BY date DESC')
    rows = c.fetchall()
    conn.close()

    expenses = []
    for r in rows:
        expenses.append({
            'id': r[0],
            'category': r[1],
            'amount': r[2],
            'description': r[3],
            'date': r[4]
        })
    return jsonify(expenses)

@app.route('/add', methods=['POST'])
def add_expense():
    data = request.json
    category = data.get('category')
    amount = data.get('amount')
    description = data.get('description', '')
    date_str = datetime.now().strftime('%Y-%m-%d')  # Add current date

    if not category or not amount:
        return jsonify({'error': 'Category and amount are required.'}), 400

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO expenses (category, amount, description, date) VALUES (?, ?, ?, ?)',
              (category, amount, description, date_str))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Expense added successfully.'})

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_expense(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM expenses WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': f'Expense with id {id} deleted.'})

import ml_model  # assuming your function is inside ml_model.py

@app.route('/predict_next_month', methods=['GET'])
def predict_next_month():
    try:
        next_year, next_month, prediction = ml_model.predict_next_month_from_csv('exp.csv')

        # Convert numpy types to Python types (if needed)
        result = {
            'next_year': int(next_year) if next_year is not None else None,
            'next_month': int(next_month) if next_month is not None else None,
            'next_month_prediction': float(prediction)
        }

        return jsonify(result)

    except Exception as e:
        print("Backend error:", e)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
