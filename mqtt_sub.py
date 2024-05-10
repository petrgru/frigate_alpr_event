from paho.mqtt import client as mqtt_client
import requests
from PIL import Image
import io, os
import json
import logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger('pika').setLevel(logging.WARNING)
logger = logging.getLogger()
codeproject_host = "http://xxx:8888"
url_cam = "????"
mqtt_broker = 'x.x.x.x'
port = 1883
topic_sub = "   "
client_id = 'xzcfghjt123'
mqtt_password=''
mqtt_user=''
crop_image=[0,0,0,0]

print(codeproject_host)
def load_config():
    if os.path.exists('.config'):
        logger.info ('Importing environment from .config...')
        for line in open('.config'):
            var = line.strip().split('=', 1)
            if len(var) == 2:
                os.environ[var[0]] = var[1]

load_config()
topic_sub = os.environ['mqtt_topic']
mqtt_password = os.environ['mqtt_password']
mqtt_user = os.environ['mqtt_user']
port = int(os.environ['mqtt_port'])
client_id = os.environ['mqtt_client_id']
mqtt_broker = os.environ['mqtt_broker']
url_cam = os.environ['url_cam']
codeproject_host=os.environ['codeproject_host']
crop_image=os.environ['crop_image']

def picture_dowload(url, filename="receive.jpg"):
    try:
        r = requests.get(url, stream=True)
        if r.ok:
            logger.info("image download")
    except requests.exceptions.RequestException as e:
        logger.info('Problem download snapshot ' + str(e))    
    dt = Image.open(r.raw)
    dt.save("full.png")
    crop_str=crop_image.split()
    crop=[]
    for i in crop_str:
        crop.append(int(i))
    dt = dt.crop(crop)
    bio = io.BytesIO()
    dt.save(bio, format="PNG",quality=100)
    bio.seek(0)
    dt.save("crop.png")
    response = requests.post(
        f'{codeproject_host}/v1/image/alpr',
        files={'image': ('file.PNG', bio, 'image/png')})
    logger.info(response.json())

#    print(response.json())
    return response.json()

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info("Successfully connected to MQTT broker")
        else:
            logger.info("Failed to connect, return code %d", rc)
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
    client.on_connect = on_connect
    client.connect(mqtt_broker, port)
    return client
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        logger.info('image received')
        picture_dowload(url_cam)
    client.subscribe(topic_sub)
    client.on_message = on_message
def main():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()
    
if __name__ == '__main__':   
    main()

