from flask import request, jsonify, session
from flask_appbuilder.api import BaseApi, expose
from flask_appbuilder.security.decorators import protect

from superset.chat.chat_service import ChatMessage, Message, ChatSession, save_message, save_chat_session, add_context_to_query, get_openai_response, save_chat_message
from superset.chat.schema_processing import get_schemas_and_tables

from datetime import datetime

import uuid

class ChatRestApi(BaseApi):

    resource_name = "chat"
    allow_browser_login = True
    openapi_spec_tag = "Chat"
    include_route_methods =  {
        "message",
        "query",
        "invalidate",
    }

    
    @expose("/message", methods=["POST"])
    @protect()
    def message(self):

        data = request.get_json()
        user = data.get("user")
        message = data.get("message")
        dbid = data.get("dbid")

        if not user or not message or not dbid:
            return jsonify({"error": "User , message and dbid are required"}), 400

        schema_info = get_schemas_and_tables(dbid)
        # Store message in chatbot DB
        new_message = ChatMessage(user=user, message=message)
        save_message(new_message)
        return jsonify({"success": True, "message": "Message stored successfully", "database":schema_info})

    @expose("/query", methods=["POST"])
    @protect()
    def query(self):
        data = request.json
        user_query = data.get("query")
        conversation_id = data.get("conversation_id")
        request_time = datetime.utcnow()

        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            new_session = ChatSession(id=conversation_id, username="")
            save_chat_session(new_session)

        enhanced_query = add_context_to_query(conversation_id)
        response = get_openai_response(enhanced_query, user_query)
        response_time = datetime.utcnow()

        new_message = Message(conversation_id=conversation_id, user_message=user_query,
                              bot_response=response, request_timestamp=request_time,
                              response_timestamp=response_time)
        save_chat_message(new_message)
        return jsonify({"conversation_id": conversation_id, "response": response})

    @expose("/invalidate", methods=["POST"])
    @protect()
    def invalidate(self):
        """Invalidate the current session."""
        data = request.json
        conversation_id = data.get("conversation_id")
        return jsonify({"message": "Session invalidated." +conversation_id+""})
