import json
import time
import re
import os
import argparse
from google.cloud import pubsub_v1

project_id = "inft-6000"                                                                        
topic_suffix = "-Murad_Mazanli"                                                                 
rules_file = "rules.json"                                                                       

# I choose to encapsulate subscriber functionality within a class
class Subscriber:
    """
    Docstring for Subscriber:
    Subscriber class to manage:
        - Pub/Sub subscriptions based on dynamic rules.
        - Loading rules from a JSON file.
        - Processing messages based on rules.
    """
    def __init__(self, subscriber_id) -> None:
        self.subscriber_id = subscriber_id
        self.project_id = project_id
        self.subscriber_client = pubsub_v1.SubscriberClient()
        self.active_subscriptions = {}                                                          # Storing active subscriptions
        self.rules = []                                                                         # Used for holding the rules for the subscriber
        self.last_modification_time = 0                                                         # Tracking last modification time of rules file

    # Method for getting the level from a rule
    def _rule_level(self, rule) -> str:
        return rule.get('level')
        
    # Method for getting topic path
    def get_topic_path(self, topic_name) -> str:
        full_topic_name = f"{topic_name}{topic_suffix}"                                         # Full topic name with suffix
        return self.subscriber_client.topic_path(self.project_id, full_topic_name)      

    # Method for getting subscription path
    def get_subscription_path(self, topic_name) -> str:
        subscription_name = f"{topic_name}{topic_suffix}-{self.subscriber_id}"                  # Full subscription name with suffix and subscriber ID
        return self.subscriber_client.subscription_path(self.project_id, subscription_name)

    def load_rules(self) -> None:
        # Checking the rules if modified since last load
        try:
            current_modification_time = os.path.getmtime(rules_file)
            if current_modification_time > self.last_modification_time:
                print(f"Loading rules from {rules_file}...")
                with open(rules_file, 'r') as file:
                    data = json.load(file)
                    if self.subscriber_id in data['subscribers']:                                # Check for subscriber 
                        self.rules = data['subscribers'][self.subscriber_id]
                        print(f"Loaded {len(self.rules)} rules for {self.subscriber_id}")
                        self.update_subscriptions()
                    else:
                        print(f"No rules found for subscriber {self.subscriber_id}")
                        self.rules = []
                self.last_modification_time = current_modification_time                          # Update last modification time
        except Exception as e:
            print(f"Error loading rules: {e}")

    def update_subscriptions(self) -> None:
        # Finding required topics based on rules
        required_topics = set()
        for rule in self.rules:
            level = self._rule_level(rule)
            if level:
                required_topics.add(level)
        
        # Remove subscriptions for topics no longer needed
        current_topics = set(self.active_subscriptions.keys())
        topics_to_remove = current_topics - required_topics 
        for topic in topics_to_remove:
            print(f"Unsubscribing from {topic}...")
            self.active_subscriptions[topic].cancel()
            del self.active_subscriptions[topic]
            
        # Add new subscriptions
        topics_to_add = required_topics - current_topics
        for topic in topics_to_add:
            self.start_subscription(topic)

    def start_subscription(self, topic_name: str) -> None:
        topic_path = self.get_topic_path(topic_name)
        subscription_path = self.get_subscription_path(topic_name)
        
        # Create subscription if it doesn't exist
        try:
            self.subscriber_client.create_subscription(
                name=subscription_path, 
                topic=topic_path
            )
            print(f"Created subscription {subscription_path}")
        except Exception:
            pass
            
        print(f"Subscribing to {topic_name}...")
        
        # Callback function to process messages
        def callback(message):
            self.process_message(topic_name, message)
            
        future = self.subscriber_client.subscribe(subscription_path, callback=callback)
        self.active_subscriptions[topic_name] = future

    def process_message(self, topic: str, message) -> None:
        text = message.data.decode("utf-8")
        matched = False
        
        # Check against all rules for this topic
        for rule in self.rules:
            rule_level = self._rule_level(rule)
            if rule_level == topic:
                if re.search(rule['pattern'], text):
                    print(f"[{self.subscriber_id}] MATCH on {topic}: {text} (Pattern: {rule['pattern']})")
                    matched = True
                    break 
        message.ack()

    def run(self) -> None:
        print(f"Subscriber {self.subscriber_id} started.")
        try:
            while True:
                self.load_rules()
                time.sleep(10) 
        except KeyboardInterrupt:
            print("Subscriber stopping...")
            for future in self.active_subscriptions.values():
                future.cancel()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("subscriber_id", help="ID of the subscriber")
    args = parser.parse_args()

    # Checking subscriber ID argument
    if args.subscriber_id not in ["sub-1", "sub-2", "sub-3", "sub-4"]:
        print("Invalid subscriber ID. Use one of: sub-1, sub-2, sub-3, sub-4")
        exit(1)
    
    subscriber = Subscriber(args.subscriber_id)
    subscriber.run()