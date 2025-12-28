import sys
import json
import os
from google.cloud import pubsub_v1
from google.api_core.exceptions import NotFound, AlreadyExists
import logging

log_filename = 'logs.log'

# Removing the log file in order to create a new one
try:
    if os.path.exists(log_filename):
        os.remove(log_filename)
except Exception:
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_filename,
    filemode='w',
    datefmt='%Y-%m-%d %H:%M:%S'
)

project_id = "inft-6000" 
topic_suffix = "-Murad_Mazanli"
rules_file = "rules.json"
topics = ["DEBUG", "INFO", "WARN", "ERROR", "ALERT"]

def getting_topic_paths(publisher, topic_name) -> str:
    logging.info(f"Getting topic path for topic: {topic_name}")
    full_topic_name = f"{topic_name}{topic_suffix}"
    return publisher.topic_path(project_id, full_topic_name)

def getting_subscription_paths(subscriber_client, topic_name, sub_id) -> str:
    logging.info(f"Getting subscription path for topic: {topic_name}, subscriber: {sub_id}")
    sub_name = f"{topic_name}{topic_suffix}-{sub_id}"
    return subscriber_client.subscription_path(project_id, sub_name)

def rule_json_loading() -> dict:
    logging.info(f"Loading rules from {rules_file}...")
    if not os.path.exists(rules_file):
        logging.warning(f"No rules {rules_file} found.")
        return {}
    with open(rules_file, 'r') as f:
        return json.load(f)

def setup() -> None:
    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()
    
    logging.info(f"Setting up topics for project {project_id}...")
    
    # Create Topics
    for topic in topics:
        topic_path = getting_topic_paths(publisher, topic)
        try:
            publisher.create_topic(name=topic_path)
            logging.info(f"Created topic: {topic_path}")
        except AlreadyExists:
            logging.info(f"Topic already exists: {topic_path}")
        except Exception as e:
            logging.error(f"Error creating topic {topic_path}: {e}")

    # Create subscriptions
    logging.info("Setting up 4 subscriptions per topic...")
    sub_ids = ["sub-1", "sub-2", "sub-3", "sub-4"]
    for topic in topics:
        topic_path = getting_topic_paths(publisher, topic)
        for sub_id in sub_ids:
            sub_path = getting_subscription_paths(subscriber, topic, sub_id)
            try:
                subscriber.create_subscription(name=sub_path, topic=topic_path)
                logging.info(f"Created subscription: {sub_path}")
            except AlreadyExists:
                logging.info(f"Subscription already exists: {sub_path}")
            except Exception as e:
                logging.error(f"Error creating subscription {sub_path}: {e}")
    print("Setup completed.")

def delete() -> None:
    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()

    project_path = f"projects/{project_id}"

    # Delete all subscriptions in the project that contains the suffix
    logging.info("Searching subscriptions for deletion...")
    try:
        for sub in subscriber.list_subscriptions(request={"project": project_path}):
            name = sub.name
            if topic_suffix in name:
                try:
                    subscriber.delete_subscription(subscription=name)
                    logging.info(f"Deleted subscription: {name}")
                except NotFound:
                    logging.info(f"Subscription not found: {name}")
                except Exception as e:
                    logging.error(f"Error deleting subscription {name}: {e}")
    except Exception as e:
        logging.error(f"Error listing subscriptions: {e}")

    # Delete all topics in the project that contain the top suffix
    logging.info("Searching topics for deletion...")
    try:
        for topic in publisher.list_topics(request={"project": project_path}):
            name = topic.name
            if topic_suffix in name:
                try:
                    publisher.delete_topic(topic=name)
                    logging.info(f"Deleted topic: {name}")
                except NotFound:
                    logging.info(f"Topic not found: {name}")
                except Exception as e:
                    logging.error(f"Error deleting topic {name}: {e}")
    except Exception as e:
        logging.error(f"Error listing topics: {e}")

    logging.info("Deletion completed.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Argument setup/delete missing")
        exit(1)
    action = sys.argv[1]
    if action == "setup":
        setup()
    elif action == "delete":
        delete()
    else:
        exit(1)