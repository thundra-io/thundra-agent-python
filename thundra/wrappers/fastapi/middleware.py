from thundra.wrappers.fastapi.fastapi_wrapper import FastapiWrapper, logger
from thundra.config import config_names

from starlette.requests import Request
from starlette.background import BackgroundTask

from thundra.context.execution_context_manager import ExecutionContextManager
from thundra.wrappers.fastapi.fastapi_utils import extract_headers

import traceback


class ThundraMiddleware(object):
    def __init__(self, app, opts=None):
        self.app = app
        self.opts = opts
        self._wrapper = FastapiWrapper()

    async def __call__(self, scope, receive, send):
        """ASGI Middleware

        Args:
            scope (Dict): Connection information
            receive (Callable): Get request from client
            send (Callable): Send response to client
            
        """
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
 
        async def wrapped_send(message):
            execution_context = ExecutionContextManager.get()
            if message and message.get("type") == "http.response.start":
                execution_context.response = message
            await send(message)
        
        async def wrapped_receive():
            req = await receive()

            if req["type"] == "http.request":
                req_body = req.get("body", b"")
                try:
                    self._wrapper.before_request(scope, req_body)
                except Exception as e:
                    logger.error("Error during the before part of Thundra: {}".format(e))
            return req

        try:
            await self.app(scope, wrapped_receive, wrapped_send)
        except:
            error = {
                'type': type(e).__name__,
                'message': str(e),
                'traceback': traceback.format_exc()
            }
            try:
                self._wrapper.error_handler(error)
            except Exception as e:
                logger.error("Error in the app: {}".format(e))
        finally:
            try:
                execution_context = ExecutionContextManager.get()
                execution_context.response = {
                    "status_code": execution_context.response.get("status"),
                    "headers": extract_headers(execution_context.response)
                }
                self._wrapper.after_request(execution_context)  
            except Exception as e:
                logger.error("Error during the after part of Thundra: {}".format(e))