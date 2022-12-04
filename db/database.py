from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pyrebase

SQL_ALCHEMY_DATABASE_URL = "sqlite:///rotation.db"

engine = create_engine(
    SQL_ALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

config = {
    "apiKey": "AIzaSyAjrQGkPixTsCzTit6Vnw6AXC8Pj2fPlQA",
    "authDomain": "rotation-bot-6399a.firebaseapp.com",
    "databaseURL": "https://rotation-bot-6399a-default-rtdb.asia-southeast1.firebasedatabase.app",
    "storageBucket": "rotation-bot-6399a.appspot.com"
}

firebase = pyrebase.initialize_app(config)