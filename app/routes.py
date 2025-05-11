from flask import render_template, jsonify, request
from app import app
from app.mock_data import (
    employees, collaboration_data, security_alerts,
    dashboard_summary
)
from app.utils import load_users, send_phishing_campaign

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

@app.route('/get-users')
def get_users():
    """API endpoint to get users for the phishing test"""
    users = load_users()
    return jsonify(users)

@app.route('/run-phishing-test', methods=['POST'])
def run_phishing_test():
    """API endpoint to run phishing tests"""
    data = request.json
    selected_indices = data.get('selected_users', [])
    
    # Send phishing emails
    results = send_phishing_campaign(selected_indices)
    
    # Return results
    return jsonify({
        'success': True,
        'sent_count': len(results),
        'results': results
    })

