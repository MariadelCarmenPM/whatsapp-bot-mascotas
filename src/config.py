import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    
    HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"
    TIMEOUT = int(os.getenv("TIMEOUT", 60000))
   
    USER_DATA_DIR = os.path.join(os.getcwd(), "userData")