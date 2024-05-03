from imagekitio import ImageKit
from PIL import Image
import cv2
import base64
import io
import urllib
import requests
import numpy as np
from app.utility.logger import logger

class UPLOADFILE:
    
    def __init__(self, baseconfig) -> None:
        self.baseconfig = baseconfig
        try:
            self.imagekit = ImageKit(
                public_key=self.baseconfig.get('Imagekit', 'public_key'),
                private_key=self.baseconfig.get('Imagekit', 'private_key'),
                url_endpoint=self.baseconfig.get('Imagekit', 'url_endpoint')
            )
        except:
            logger.error("failed to connect to imagekit")
            
        self.transformation = {
            'height': self.baseconfig.getint('Imagekit', 'height'),
            'width': self.baseconfig.getint('Imagekit', 'width'),
            'crop': self.baseconfig.get('Imagekit', 'crop'),
        }

    def _uploadfile(self, img, file_name=None) -> bool:
        try:
            content_file = io.BytesIO()
            img.save(content_file, format='PNG')
            content_file.seek(0)
            base64_encoded = base64.b64encode(content_file.read()).decode('utf-8')
            
            image_upload_url = self.imagekit.upload_file(file=base64_encoded,
                    file_name=file_name)
            #print("image_upload_url:", image_upload_url)
            return image_upload_url
        except Exception as e:
            logger.exception(e)
    
    def url_to_image(self, url) -> Image.Image:
        try:
            resp = requests.get(url)
            img = Image.open(io.BytesIO(resp.content))
            #img = img.convert('RGB')
            return img
        except Exception as e:
            logger.exception(e)
