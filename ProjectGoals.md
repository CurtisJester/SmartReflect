# Smartphone Use Analysis

This project will provide a SQL database with the smartphone use data that powers a frontend viewer. 
The goal is to allow the user to explore the data interactively, provide a few filters, and offer
the user an export ability for their filtered results.

## Implementation Overview

The frontend will be a simple web application that uses TypeScript and React to provide a user-friendly interface for exploring the data.
The backend will be a python application that uses FastAPI to provide a REST API for the frontend to consume.
The database will run on SQLite and will be populated with the smartphone use data. 
The database will be populated using a python script that reads the smartphone use data and inserts it into the database.
The frontend will be able to query the backend for data and display it, and export the data in a CSV file.

### Dataset Information

The dataset contains the following columns and column data types:
 - transaction_id: str
 - user_id: str
 - age: int
 - gender: str
 - daily_screen_time_hours: float
 - social_media_hours: float
 - gaming_hours: float
 - work_study_hours: float
 - sleep_hours: float
 - notifications_per_day: int
 - app_opens_per_day: int
 - weekend_screen_time: float
 - stress_level: str
 - academic_work_impact: str
 - addiction_level: str
 - addicted_label: int

#### Potential Applications of This Data

This data could be used to:
 - Identify patterns in smartphone use and their impact on academic performance and work productivity
 - Develop interventions to reduce smartphone use and improve productivity
 - Explore potential relationships between smartphone use and stress levels
 - Explore potential connection between smartphone use and sleep quantity