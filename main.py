
import json
import time
import configparser
from kafka import KafkaConsumer
from inference import VTO_Inference_v3
from app.utility.logger import logger
from app.utility.helper import UPLOADFILE
from app.controller.manager_kafka import Manager_kafka
from PIL import Image
import glob, os
import requests
from io import BytesIO
import urllib.request
import io


config = configparser.ConfigParser()
config.read("config.ini")

input_component = "INPUT_VTO_V3"
component = "RESULT_VTO_V3"
component_errors = "RESULT_VTO_V3_ERROR"
ootd_model_type = "dc"
gpu_id = "cuda"

app_kafka = Manager_kafka(config)
app_uloadfile = UPLOADFILE(config)
idm_inference = VTO_Inference_v3(model_type=ootd_model_type, gpu_id=gpu_id)


def _main(config) -> None:
    try:
        idm_inference.__init__();
        consumer = KafkaConsumer(input_component, bootstrap_servers=[config.get('SERVER-KAFKA-CONSUMER', 'bootstrap_server')],
                                 value_deserializer=lambda x: x.decode('utf-8'))

        while True:
            try:
                for message in consumer:
                    info_mess = message.value
                    info_mess = json.loads(info_mess)

                    img = info_mess['info']['url-human']
                    img = img.encode('ascii', 'ignore')
                    print("img url ");
                    print(img);
                    #img2 = Image.open(img)                        
                    # img = app_uloadfile.url_to_image(img)
                    # human_url_res = requests.get(img)
                    # human_img3 = Image.open(BytesIO(human_url_res.content)).crop((1,20,50,80))
                    with urllib.request.urlopen(img) as url1:
                        f1 = io.BytesIO(url1.read())
                    human_img4 = Image.open(f1)
                    
                    cloth = info_mess['info']['url-clothes']
                    cloth = cloth.encode('ascii', 'ignore')
                    print("cloth url ");
                    print(cloth);
                    #cloth2 = Image.open(requests.get(cloth, stream=True).raw)                     
                    # img = app_uloadfile.url_to_image(cloth)
                    # cloth_url_res = requests.get(cloth)
                    # cloth_img3 = Image.open(BytesIO(cloth_url_res.content)).crop((1,20,50,80))
                    with urllib.request.urlopen(cloth) as url2:
                        f2 = io.BytesIO(url2.read())
                    cloth_img4 = Image.open(f2)
                    clothes_type = "upper_body"

                    time_start = time.time()

                    # results = idm_inference._infer_virtualtryon_v3(
                    #     img, cloth, clothes_type, n_samples=2)
                    
                    # print("========================================");
                    # print("type(human_img4)");
                    # print(type(human_img4));
                    
                    # print("type(cloth_img4)");
                    # print(type(cloth_img4));
                    # print("========================================");
                    
                    print("idm_inference run with params:")
                    [image_out,masked_img] = idm_inference._infer_virtualtryon_v3(
                        human_img4, cloth_img4, clothes_type, n_samples=2)
                    time_end = time.time()
                    
                    
                    # print("========================================");
                    # print("type(image_out)");
                    # print(type(image_out));
                    # print(image_out); 
                                
                    
                    # print("type(masked_img)");
                    # print(type(masked_img));
                    # print(masked_img);                      
                    # print("========================================");
                    
                    print(
                        "\nUse: {} - Time for generate processing: {}".format(gpu_id, time_end - time_start))
                    results= None;
                    if image_out is not None:
                        urls = []
                        # for idx in range(len(results)):
                        #     url = app_uloadfile._uploadfile(
                        #         results[idx], file_name=str(time.time())).url
                        #     urls.append(url)
                        url = app_uloadfile._uploadfile(image_out, file_name=str(time.time())).url
                        print("==================app_uloadfile======================");
                        print(url);
                        urls.append(url)
                        mess = {
                            "status": True,
                            "info": {
                                "component": component,
                                "id": info_mess['info']['id'],
                                "group-topic": "VTO_V3",
                                "url-image": urls,
                            },
                            "origin": info_mess,
                            "gpu_id": gpu_id,
                            "timestamp": (time_end - time_start)
                        }
                        app_kafka._producer_push(component, mess)
                    else:
                        mess = {
                            "status": False,
                            "info": {
                                "component": component_errors,
                                "id": info_mess['info']['id'],
                                "group-topic": "VTO_V3",
                                "url-image": None,
                            },
                            "origin": info_mess,
                            "gpu_id": gpu_id,
                            "timestamp": (time_end - time_start)
                        }
                        app_kafka._producer_push(component_errors, mess)
            except Exception as e:
                logger.exception(e)
    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    logger.info("STARTING APP")
    _main(config)
