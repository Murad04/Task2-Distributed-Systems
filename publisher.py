import csv
import os
import time
from google.cloud import pubsub_v1
import logging

project_id = "inft-6000" 
topic_suffix = "-Murad_Mazanli" 
log_file = "logs.csv"
logs_file = 'publisherlogs.log'

try:
    if os.path.exists(logs_file):
        os.remove(logs_file)
except Exception:
    pass 

logging.basicConfig(filename=logs_file, level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s',filemode='w')

# Topics to create/use
TOPICS = ["DEBUG", "INFO", "WARN", "ERROR", "ALERT"]

# Creating and returning a publisher client
def create_publisher() -> pubsub_v1.PublisherClient:
    client = pubsub_v1.PublisherClient()
    return client

# Function to get topic path
def get_topic_path(publisher, topic_name) -> str:
    full_topic_name = f"{topic_name}{topic_suffix}"
    topic_path = publisher.topic_path(project_id, full_topic_name)
    return topic_path

def main():
    publisher = create_publisher()
    logging.info(f"Publisher started for project {project_id} with suffix {topic_suffix}")
    try:
        while True:
            with open(log_file, 'r', newline='') as file:
                file.seek(0)

                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        topic_name = row.get('level')
                        message_text = row.get('message')
                    except Exception as ex:
                        logging.error(f"Error reading row: {ex}")
                        continue

                    if not topic_name or not message_text:
                        continue

                    if topic_name in TOPICS:
                        topic_path = get_topic_path(publisher, topic_name)
                        data = message_text.encode("utf-8")
                        try:
                            future = publisher.publish(topic_path, data)
                            logging.info(f"Published to {topic_name}: {message_text} (Message ID: {future.result()})")
                        except Exception as e:
                            logging.error(f"Failed to publish to {topic_name}: {e}")
                    else:
                        logging.warning(f"Unknown topic: {topic_name}")
                    time.sleep(2)
            logging.info("Reached end of log file. Restarting...")

    except KeyboardInterrupt:
        logging.info("Publisher stopped.")

if __name__ == "__main__":
    main()