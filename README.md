# Homework 2: Content-Based Subscriptions with Google Cloud Pub/Sub

## Overview
In this project, I have implemented a distributed messaging system using Google Cloud Pub/Sub and it has content-based filtering where subscribers filter messages based on regex patterns defined in a file.

## Prerequisites
1.  **Google Cloud Project**
2.  **Service Account**
3.  **Python**
4.  **Dependencies**: Google Cloud Pub/Sub library:

## Usage

### 1. Setup Topics
Run the setup script to create the topics and four subscriptions per topic (`sub-1`..`sub-4`):
```bat
# Windows
.\script_manage.bat setup
```

**Terminal 1:**
```bat
python subscriber.py sub-1
```

**Terminal 2:**
```bat
python subscriber.py sub-2
```

**Terminal 3:**
```bat
python subscriber.py sub-3
```

**Terminal 4:**
```bat
python subscriber.py sub-4
```

### 2. Start Publisher
```bat
python publisher.py
```

### 3. Deleting subscriptions
```bat
.\script_manage.bat delete
```

### 4. Easy way to run all of the subscribers and publisher 
```bat
.\script_run.bat
```

## Files
*   `publisher.py`: Reads `logs.csv` and publishes messages. And stores logs in the `publisherlogs.log`.
*   `subscriber.py`: Subscribes to topics and filters messages based on `rules.json`.
*   `manage_topics.py`: Creates and deletes Pub/Sub topics and subscriptions.
*   `script_manage.bat`: Runs the manage_topics.py with a given argument setup|delete.
*   `logs.csv`: Input log messages.
*   `rules.json`: Configuration for subscriber regex rules.
*   `script_run.bat`: Starts publisher and four subscribers in separate terminal. 

## Video Demonstration
[[Youtube Video](https://youtu.be/_IuTdSiBBnI)]