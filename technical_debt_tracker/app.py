from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date, datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
@app.route('/')
def index():
    conn = get_db_connection()
    debts = conn.execute('SELECT * FROM technical_debt').fetchall()
    conn.close()

    today = date.today()
    processed = []

    for d in debts:
        deadline = datetime.strptime(d['deadline'], "%Y-%m-%d").date()
        days_left = (deadline - today).days

        alert = "none"
        if d['status'] != "Resolved":
            if days_left < 0:
                alert = "overdue"
            elif days_left <= 3:
                alert = "warning"

        processed.append({
            "id": d["id"],
            "title": d["title"],
            "severity": d["severity"],
            "status": d["status"],
            "deadline": d["deadline"],
            "alert": alert
        })

    # ---- DASHBOARD COUNTS ----
    total_count = len(processed)
    open_count = 0
    resolved_count = 0
    overdue_count = 0

    for d in processed:
        if d["status"] == "Resolved":
            resolved_count += 1
        else:
            open_count += 1
            if d["alert"] == "overdue":
                overdue_count += 1

    return render_template(
        'index.html',
        debts=processed,
        total_count=total_count,
        open_count=open_count,
        resolved_count=resolved_count,
        overdue_count=overdue_count
    )



@app.route('/add', methods=['GET', 'POST'])
def add_debt():
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO technical_debt (title, description, severity, status, deadline) VALUES (?, ?, ?, ?, ?)',
            (
                request.form['title'],
                request.form['description'],
                request.form['severity'],
                'Open',
                request.form['deadline']
            )
        )
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('add_debt.html')

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

@app.route('/delete/<int:id>')
def delete_debt(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM technical_debt WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
