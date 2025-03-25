from sqlalchemy import create_engine
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker
import logging


logger = logging.getLogger(__name__)
# Load the chatbot database URI from Superset config
chatbot_db_uri = current_app.config.get("SQLALCHEMY_CHATBOT_URI")
# Create a new database engine
chatbot_engine = create_engine(chatbot_db_uri)
ChatBase = declarative_base()
Session = sessionmaker(bind=chatbot_engine)
session = Session()

class ChatMessage(ChatBase):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String, nullable=False)
    message = Column(Text, nullable=False)

def save_message(message):
    session.add(message)
    try:
        session.commit()
    except SQLAlchemyError as ex:
        print(f"An error occurred while adding messages: {ex}")
        session.rollback()


# Create table if it doesn’t exist
ChatBase.metadata.create_all(chatbot_engine)
