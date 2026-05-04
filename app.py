from flask import Flask, render_template, request, make_response
import sqlite3
from reportlab.pdfgen import canvas
from io import BytesIO

app = Flask(__name__)

# Home page
@app.route('/')
def home():
    return render_template('index.html')


# Signup
@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    password = request.form['password']

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))

    conn.commit()
    conn.close()

    return "Signup Success ✅"


# Login
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cur.fetchone()

    conn.close()

    if user:
        return render_template("dashboard.html")
    else:
        return "Invalid Credentials ❌"


# Save Dashboard Health Data
@app.route('/submit_health', methods=['POST'])
def submit_health():
    age = int(request.form['age'])
    weight = float(request.form['weight'])
    height = float(request.form['height'])
    bp = int(request.form['bp'])
    sugar = int(request.form['sugar'])
    smoking = request.form['smoking']
    family_history = request.form['family_history']
    extra_problems = request.form['extra_problems']

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO health_data
        (age, weight, height, bp, sugar, smoking, family_history, extra_problems)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (age, weight, height, bp, sugar, smoking, family_history, extra_problems))

    conn.commit()
    conn.close()

    # Stroke Risk Prediction Logic
    risk_score = 0

    if age > 60:
        risk_score += 2
    elif age > 40:
        risk_score += 1

    if bp > 140:
        risk_score += 2

    if sugar > 180:
        risk_score += 2

    if smoking.lower() == "yes":
        risk_score += 1

    if family_history.lower() == "yes":
        risk_score += 1

    if extra_problems.strip() != "":
        risk_score += 1

    if risk_score >= 6:
        risk = "High Risk 🔴"
    elif risk_score >= 3:
        risk = "Moderate Risk 🟠"
    else:
        risk = "Low Risk 🟢"

    # BMI Calculation
    height_m = height / 100
    bmi = round(weight / (height_m * height_m), 2)

    ideal_weight = round(22 * (height_m * height_m), 2)

    if bmi < 18.5:
        bmi_status = "Underweight"
    elif bmi < 25:
        bmi_status = "Normal"
    elif bmi < 30:
        bmi_status = "Overweight"
    else:
        bmi_status = "Obese"

    return render_template(
        "prediction.html",
        result=risk,
        bmi=bmi,
        bmi_status=bmi_status,
        ideal_weight=ideal_weight,
        age=age
    )


# ✅ FIXED REPORTS
@app.route('/reports')
def reports():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM health_data")
    data = cur.fetchall()

    conn.close()

    latest = data[-1] if data else [0,0,0,0,0,"","",""]

    # ✅ Correct mapping (FIXED)
    age = latest[0]
    weight = latest[1]
    height = latest[2]
    bp = latest[3]
    sugar = latest[4]
    smoking = latest[5]
    family_history = latest[6]
    extra_problems = latest[7]

    ideal_weight = 60
    ideal_bp = 120
    ideal_sugar = 140

    return render_template(
        "reports.html",
        records=data,
        age=age,
        weight=weight,
        height=height,
        bp=bp,
        sugar=sugar,
        smoking=smoking,
        family_history=family_history,
        extra_problems=extra_problems,
        ideal_weight=ideal_weight,
        ideal_bp=ideal_bp,
        ideal_sugar=ideal_sugar
    )


# PDF
@app.route('/download_pdf')
def download_pdf():
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(180, 800, "Stroke Health Report")

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM health_data ORDER BY rowid DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()

    if row:
        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, 750, f"Age: {row[0]}")
        pdf.drawString(100, 730, f"Weight: {row[1]}")
        pdf.drawString(100, 710, f"Height: {row[2]}")
        pdf.drawString(100, 690, f"BP: {row[3]}")
        pdf.drawString(100, 670, f"Sugar: {row[4]}")
        pdf.drawString(100, 650, f"Smoking: {row[5]}")
        pdf.drawString(100, 630, f"Family History: {row[6]}")
        pdf.drawString(100, 610, f"Extra Problems: {row[7]}")

    pdf.save()

    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=health_report.pdf'
    return response


# Prevention
@app.route('/prevention')
def prevention():
    return render_template("prevention.html")


if __name__ == "__main__":
    app.run(debug=True)
