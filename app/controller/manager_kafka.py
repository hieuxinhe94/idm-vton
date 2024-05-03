from ..utility.logger import logger
from kafka import KafkaProducer, KafkaConsumer
import json

class Manager_kafka():
    
    def __init__(self, config) -> None:
       self.config = config
            
    def _producer_push(self, conponent, msg) -> bool:
        logger.debug("Push msg:{} to Conponent:{}".format(msg, conponent))
        try:
            print("--------------------- self.config.get('SERVER-KAFKA-PRODUCER', 'bootstrap_server'): ", self.config.get('SERVER-KAFKA-PRODUCER', 'bootstrap_server'))
            producer = KafkaProducer(bootstrap_servers=[self.config.get('SERVER-KAFKA-PRODUCER', 'bootstrap_server')],
                                value_serializer=lambda v: json.dumps(v).encode('utf-8'))
            
            print("producer:", producer)
            producer.send(conponent, msg)
            producer.flush()
        except Exception as e:
            logger.exception(e)
            
    def _consumer_get(self, conponent) -> bool:
        logger.debug("Get msg from component:{}".format(conponent))
        try:
            consumer = KafkaConsumer(conponent, bootstrap_servers=[self.config.get('SERVER-KAFKA-CONSUMER', 'bootstrap_server')],
                        value_deserializer=lambda x: x.decode('utf-8'))

            while True:
                logger.warn("WARN: Read msg from conponent:{}".format(conponent))
                for msg in consumer:
                    print("mess:", msg.value)
                    logger.debug("INFO: msg.value")
                    return msg
        except Exception as e:
            logger.exception(e)