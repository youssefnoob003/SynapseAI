from flask import render_template
from app import app
from app.mock_data import (
    employees, collaboration_data, security_alerts,
    dashboard_summary
)

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', 
                         summary=dashboard_summary,
                         recent_alerts=security_alerts[:2])

@app.route('/performance')
def performance():
    return render_template('performance.html', employees=employees)

@app.route('/collaboration')
def collaboration():
    return render_template('collaboration.html', 
                         collaboration_data=collaboration_data)

@app.route('/security')
def security():
    return render_template('security.html', alerts=security_alerts)

