import smtplib
from email.mime.text import MIMEText
import json
from gpt4all import GPT4All
import os

# Load the GPT4All model
model = None

def get_model():
    """Lazy loading of the GPT4All model"""
    global model
    if model is None:
        model = GPT4All("mistral-7b-openorca.Q4_0.gguf")
    return model

def load_users():
    """Load users from the JSON file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    users_path = os.path.join(current_dir, 'users.json')
    
    with open(users_path, 'r') as f:
        users = json.load(f)
    return users

def generate_phishing_email(user):
    """Generate a phishing email for a user using GPT4All"""
    # Prompt template for generating phishing emails
    prompt_template = """
    You are generating a phishing email for internal cybersecurity awareness training.
    
    Target details:
    - Name: {name}
    - Location: {location}
    - Company: {company}
    - Role/Bio: {bio}
    
    Write an email that appears to come from the company's IT department.
    - The tone should be professional, concise, and slightly urgent.
    - Include a scenario that makes sense based on the user's job and background (e.g., finance → payroll update, developer → GitHub breach, HR → document access).
    - Mention the user's location or department subtly if relevant.
    - Add a fake (but realistic-looking) link.
    - Do NOT include any disclaimers or explanations — only the phishing email body.
    
    Begin below:
    """
    
    # Generate personalized email content
    prompt = prompt_template.format(
        name=user['name'], 
        company=user['company'], 
        location=user['location'], 
        bio=user['bio']
    )
    
    model = get_model()
    with model.chat_session():
        body = model.generate(prompt, max_tokens=300)
    
    return body.strip()

def send_phishing_email(user):
    """Send a phishing email to a user"""
    # Email sender details
    sender = 'it-support@fakebank.com'
    
    # Generate personalized email content
    body = generate_phishing_email(user)
    
    # Email details
    recipient = user['email']
    subject = f'Immediate Action Required: {user["company"]} Account Verification'
    
    # Construct email
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    
    # Send email
    try:
        with smtplib.SMTP('localhost', 1025) as server:
            server.send_message(msg)
        
        result = {
            'success': True,
            'recipient_name': user['name'],
            'recipient': recipient,
            'sender': sender,
            'subject': subject,
            'body': body
        }
    except Exception as e:
        result = {
            'success': False,
            'recipient_name': user['name'],
            'recipient': recipient,
            'error': str(e)
        }
    
    return result

def send_phishing_campaign(selected_indices):
    """Send phishing emails to selected users"""
    users = load_users()
    results = []
    
    for idx in selected_indices:
        if idx < len(users):
            result = send_phishing_email(users[idx])
            results.append(result)
    
    return results

