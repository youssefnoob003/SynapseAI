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
    {"id": 5, "name": "Alex Taylor", "role": "DevOps Engineer", "score": 87, 
     "tasks_completed": 19, "tasks_in_progress": 5},
    {"id": 6, "name": "Olivia Kim", "role": "Frontend Developer", "score": 91, 
     "tasks_completed": 22, "tasks_in_progress": 2},
    {"id": 7, "name": "David Park", "role": "Data Scientist", "score": 89, 
     "tasks_completed": 17, "tasks_in_progress": 3},
    {"id": 8, "name": "Maya Roberts", "role": "Backend Developer", "score": 86, 
     "tasks_completed": 20, "tasks_in_progress": 4},
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

