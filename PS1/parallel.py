from PIL import Image
from PIL.ExifTags import TAGS
import requests as req


print(req.get("https://pbs.twimg.com/profile_banners/1721298719071502336/1757497530/1500x500").json())