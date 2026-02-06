from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date, datetime

app = Flask(__name__)

# ---------------- DATABASE CONNECTION ----------------
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- HOME PAGE ----------------
@app.route('/')
def index():
    conn = get_db_connection()
    debts = conn.execute('SELECT * FROM technical_debt').fetchall()
    conn.close()

    today = date.today()
    processed_debts = []

    for debt in debts:
        deadline_date = datetime.strptime(debt['deadline'], "%Y-%m-%d").date()
        days_left = (deadline_date - today).days

        alert = "none"
        if debt['status'] != "Resolved":
            if days_left < 0:
                alert = "overdue"
            elif days_left <= 3:
                alert = "warning"

        processed_debts.append({
            "id": debt["id"],
            "title": debt["title"],
            "description": debt["description"],
            "severity": debt["severity"],
            "status": debt["status"],
            "deadline": debt["deadline"],
            "alert": alert
        })

    return render_template('index.html', debts=processed_debts)

# ---------------- ADD DEBT ----------------
@app.route('/add', methods=['GET', 'POST'])
def add_debt():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        severity = request.form['severity']
        deadline = request.form['deadline']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO technical_debt (title, description, severity, status, deadline) VALUES (?, ?, ?, ?, ?)',
            (title, description, severity, 'Open', deadline)
        )
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add_debt.html')

# ---------------- UPDATE STATUS ----------------
@app.route('/resolve/<int:id>')
def resolve_debt(id):
    conn = get_db_connection()
    conn.execute(
        'UPDATE technical_debt SET status = ? WHERE id = ?',
        ('Resolved', id)
    )
    conn.commit()
    conn.close()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
# ---------------- DELETE DEBT ----------------
@app.route('/delete/<int:id>')
def delete_debt(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM technical_debt WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return redirect('/')
