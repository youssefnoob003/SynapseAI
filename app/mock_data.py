from datetime import datetime, timedelta

# Performance Data
employees = [
    {"id": 1, "name": "John Smith", "role": "Software Engineer", "score": 85, 
     "tasks_completed": 24, "tasks_in_progress": 3},
    {"id": 2, "name": "Emma Wilson", "role": "Data Analyst", "score": 92, 
     "tasks_completed": 18, "tasks_in_progress": 2},
    {"id": 3, "name": "Michael Chen", "role": "Product Manager", "score": 88, 
     "tasks_completed": 15, "tasks_in_progress": 4},
    {"id": 4, "name": "Sarah Davis", "role": "UX Designer", "score": 90, 
     "tasks_completed": 21, "tasks_in_progress": 2},
]

# Collaboration Data by Month
collaboration_data = {
    "2024-01": [
        {"from": "John Smith", "to": "Emma Wilson", "count": 15},
        {"from": "Emma Wilson", "to": "Michael Chen", "count": 12},
        {"from": "Michael Chen", "to": "Sarah Davis", "count": 8},
        {"from": "Sarah Davis", "to": "John Smith", "count": 10},
        {"from": "John Smith", "to": "Michael Chen", "count": 7},
        {"from": "Emma Wilson", "to": "Sarah Davis", "count": 9}
    ],
    "2024-02": [
        {"from": "John Smith", "to": "Emma Wilson", "count": 18},
        {"from": "Emma Wilson", "to": "Michael Chen", "count": 15},
        {"from": "Michael Chen", "to": "Sarah Davis", "count": 11},
        {"from": "Sarah Davis", "to": "John Smith", "count": 13},
        {"from": "John Smith", "to": "Michael Chen", "count": 9},
        {"from": "Emma Wilson", "to": "Sarah Davis", "count": 12}
    ],
    "2024-03": [
        {"from": "John Smith", "to": "Emma Wilson", "count": 20},
        {"from": "Emma Wilson", "to": "Michael Chen", "count": 16},
        {"from": "Michael Chen", "to": "Sarah Davis", "count": 14},
        {"from": "Sarah Davis", "to": "John Smith", "count": 15},
        {"from": "John Smith", "to": "Michael Chen", "count": 11},
        {"from": "Emma Wilson", "to": "Sarah Davis", "count": 13}
    ]
}

# Security Alerts
security_alerts = [
    {
        "type": "Off-hours Access",
        "user": "John Smith",
        "timestamp": (datetime.now() - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M"),
        "severity": "medium",
        "details": "System access detected at 11:45 PM"
    },
    {
        "type": "Multiple Login Attempts",
        "user": "Emma Wilson",
        "timestamp": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
        "severity": "high",
        "details": "5 failed login attempts detected"
    },
    {
        "type": "Unusual File Access",
        "user": "Michael Chen",
        "timestamp": (datetime.now() - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M"),
        "severity": "low",
        "details": "Accessed restricted project files"
    }
]

# Dashboard Summary
dashboard_summary = {
    "average_performance": 89,
    "total_tasks_completed": 78,
    "active_projects": 12,
    "collaboration_score": 8.5,
    "security_alerts_today": 3,
    "team_productivity_trend": [75, 82, 88, 85, 89, 92, 89],  # Last 7 days
    "department_scores": {
        "Engineering": 87,
        "Design": 90,
        "Product": 88,
        "Analytics": 92
    }
}

