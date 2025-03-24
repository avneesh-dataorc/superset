from flask import request, jsonify
from flask_appbuilder.api import BaseApi, expose
from flask_appbuilder.security.decorators import protect

class ChatRestApi(BaseApi):
    resource_name = "chat"
    allow_browser_login = True
    openapi_spec_tag = "Chat"

    
    @expose("/message", methods=["GET"])
    @protect()
    def message(self):
        return self.response(200, message="Hello from the new API!")
