from flask import request, jsonify
from flask_appbuilder.api import BaseApi, expose
from flask_appbuilder.security.decorators import protect

from superset.chat.chat_service import ChatMessage, save_message
from superset.chat.schema_processing import get_schemas_and_tables


class ChatRestApi(BaseApi):

    resource_name = "chat"
    allow_browser_login = True
    openapi_spec_tag = "Chat"

    
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
