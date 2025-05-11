from flask import render_template, jsonify, request, redirect
from app import app
from app.mock_data import (
    dashboard_summary
)
from app.utils import load_users, send_phishing_campaign
import json

@app.route('/')
@app.route('/dashboard')
def dashboard():
    with open("app\\security.json", "r") as file:
        security_alerts = json.load(file)
    return render_template('dashboard.html', 
                         summary=dashboard_summary,
                         recent_alerts=security_alerts[:2])

@app.route('/performance')
def performance():
    return render_template('performance.html', employees=load_users())

@app.route('/collaboration')
def collaboration():
    with open('numpy_numpy_monthly_collaboration.json', 'r') as file:
        collaboration_data = json.load(file)
    return render_template('collaboration.html', 
                         collaboration_data=collaboration_data)

@app.route('/security')
def security():
    with open("app\\security.json", "r") as file:
        security_alerts = json.load(file)
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

@app.route('/update-security-score')
def update_security_score():
    """Update a user's security score and redirect to a specified link"""
    username = request.args.get('username')
    redirect_url = request.args.get('redirect_url', '/security')
    
    if not username:
        return jsonify({'error': 'Username parameter is required'}), 400
    
    # Load users
    users = load_users()
    user_found = False
    
    # Find and update the user's security score
    for user in users:
        if user['name'] == username:
            user['security_score'] = user['security_score'] / 2
            user_found = True
            break
    
    if not user_found:
        return jsonify({'error': 'User not found'}), 404
    
    with open('app/users.json', 'w') as file:
        json.dump(users, file, indent=4)
    
    # Redirect to the specified URL
    return redirect("https://www.youtube.com/watch?v=h0NG7DxV5iE&ab_channel=InternetThings")

