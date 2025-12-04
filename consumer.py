from confluent_kafka import Consumer
import json

# Créer le consumer
conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'social_media_group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
topic = 'social_media_stream'
consumer.subscribe([topic])

print("🎧 En écoute des messages...")
print("-" * 50)

try:
    while True:
        # Poll pour récupérer les messages (timeout en secondes)
        msg = consumer.poll(timeout=1.0)
        
        if msg is None:
            continue
        
        if msg.error():
            # Gestion des erreurs
            print(f"Erreur: {msg.error()}")
            continue
        
        # Décoder la valeur du message
        try:
            value = json.loads(msg.value().decode('utf-8'))
        except:
            value = msg.value().decode('utf-8')
        
        # Afficher les informations du message
        print(f" Topic: {msg.topic()}")
        print(f"   Partition: {msg.partition()}")
        print(f"   Offset: {msg.offset()}")
        print(f"   Key: {msg.key().decode('utf-8') if msg.key() else None}")
        print(f"   Timestamp: {msg.timestamp()}")
        print(f"   Value: {value}")
        print("-" * 50)
except KeyboardInterrupt:
    print("\n👋 Arrêt du consumer...")
finally:
    consumer.close()