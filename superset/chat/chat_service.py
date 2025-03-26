from sqlalchemy import create_engine
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)
# Load the chatbot database URI from Superset config
chatbot_db_uri = current_app.config.get("SQLALCHEMY_CHATBOT_URI")
# Create a new database engine
chatbot_engine = create_engine(chatbot_db_uri)
ChatBase = declarative_base()
Session = sessionmaker(bind=chatbot_engine)
session = Session()

OPENAI_API_URL = current_app.config.get("OPENAI_API_URL")
OPENAI_API_KEY = current_app.config.get("OPENAI_API_KEY")

class ChatMessage(ChatBase):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String, nullable=False)
    message = Column(Text, nullable=False)


class ChatSession(ChatBase):
    __tablename__ = "chat_session"
    id = Column(String(36), primary_key=True)
    username = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Message(ChatBase):
    __tablename__ = "message"
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(36), ForeignKey("chat_session.id"), nullable=False)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    request_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    response_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


# Create table if it doesn’t exist
ChatBase.metadata.create_all(chatbot_engine)

def getDBSession():
    Session = sessionmaker(bind=chatbot_engine)
    return Session()

def save_message(message):
    db_session = getDBSession()
    db_session.add(message)
    try:
        db_session.commit()
    except SQLAlchemyError as ex:
        print(f"An error occurred while adding messages: {ex}")
        db_session.rollback()
    finally:
        db_session.close()

def save_chat_message(message):
    db_session = getDBSession()
    db_session.add(message)
    try:
        db_session.commit()
    except SQLAlchemyError as ex:
        print(f"An error occurred while adding messages: {ex}")
        db_session.rollback()
    finally:
        db_session.close()

def save_chat_session(chat_session):
    db_session = getDBSession()
    db_session.add(chat_session)
    try:
        db_session.commit()
    except SQLAlchemyError as ex:
        print(f"An error occurred while saving chat session: {ex}")
        db_session.rollback()
    finally:
        db_session.close()


def add_context_to_query(conversation_id):
    """Enhance user query with additional context."""
    context = "This is a chatbot that provides intelligent responses based on context. "
    db_session = getDBSession()
    chat_history = db_session.query(Message).filter_by(
        conversation_id=conversation_id).all()
    db_session.close()
    history = []
    for msg in chat_history:
        history.append({"role": "user", "content": msg.user_message})
        history.append({"role": "assistant", "content": msg.bot_response})
    return history

def get_openai_response(chat_history, user_query):
    """Make a request to OpenAI API and get response."""
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    chat_history.append({"role": "user", "content": user_query})
    payload = {
        "model": "gpt-4o-mini",
        "messages": chat_history
    }
    print(payload)
    response = requests.post(OPENAI_API_URL, json=payload, headers=headers)
    if response.status_code != 200:
        return f"Error: {response.json().get('error', {}).get('message', 'Unknown error')}"

    response_data = response.json()
    print(response_data)
    return response_data["choices"][0]["message"]["content"]
