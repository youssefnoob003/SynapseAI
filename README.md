# SynapseAI - Workforce Analytics Demo

A Flask-based demonstration project showcasing intelligent workforce analytics capabilities.

## Features

- **Performance Monitoring**: Track employee performance scores and task completion
- **Collaboration Mapping**: Visualize team interactions and collaboration patterns
- **Security Analysis**: Monitor and analyze security-related behaviors and incidents
- **Dashboard Overview**: Comprehensive view of key metrics and trends

## Technologies Used

- Flask
- Bootstrap 5
- Chart.js
- Python 3.x

## Project Structure

```
synapse-ai/
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── js/
│   │       └── charts.js
│   ├── templates/
│   │   ├── layout.html
│   │   ├── dashboard.html
│   │   ├── performance.html
│   │   ├── collaboration.html
│   │   └── security.html
│   ├── __init__.py
│   ├── routes.py
│   └── mock_data.py
├── requirements.txt
└── run.py
```

## Setup and Installation

1. Create a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Run the application:
   ```powershell
   python run.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

## Pages

1. **Dashboard**: Overview of key metrics, trends, and recent alerts
2. **Performance**: Detailed employee performance metrics and task tracking
3. **Collaboration**: Team interaction visualization and collaboration analysis
4. **Security**: Security incident monitoring and alert management

## Development

This is a demo project using mock data. All data is simulated and stored in `mock_data.py`. The application uses:

- Bootstrap for responsive UI components
- Chart.js for interactive data visualization
- Flask's Jinja2 templating for dynamic content
- Custom CSS for enhanced styling

## Note

This is a demonstration project and does not include:
- Database integration
- User authentication
- Real-time data processing
- Production-level security measures

