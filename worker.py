from src.infrastructure.messaging.kafka_consumer import TransformerConsumer

if __name__ == "__main__":
    worker = TransformerConsumer()
    worker.run()