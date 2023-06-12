from catchpoint.wrappers.fastapi.fastapi_wrapper import FastapiWrapper, logger
from catchpoint.config import config_names

from catchpoint.wrappers.fastapi.fastapi_utils import extract_headers

from catchpoint.config.config_provider import ConfigProvider
from catchpoint import constants

import traceback

RESPONSE_REDIRECT_STATUS_CODE = 307

def handle_error(exception, exception_handler, execution_context = None):
    error = {
        'type': type(exception).__name__,
        'message': str(exception),
        'traceback': traceback.format_exc()
    }
    exception_handler(error, execution_context)

class CatchpointMiddleware(object):
    def __init__(self, app, wrapper):
        self.app = app
        self._wrapper = wrapper

    async def __call__(self, scope, receive, send):
        """ASGI Middleware

        Args:
            scope (Dict): Connection information
            receive (Callable): Get request from client
            send (Callable): Send response to client
            
        """
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        try:
            scope["_catchpoint_wrapped"] = True
            scope["catchpoint_execution_context"] = self._wrapper.before_request(scope, None)
            execution_context = scope["catchpoint_execution_context"]
        except Exception as e:
            logger.error("Error during the before part of Catchpoint fastapi: {}".format(e))

        def handle_response(message):
            """ Checking response should be redirect or not. If redirected, then pass the response body by
            setting res_redirected field in scope.

            Args:
                message (Response):  
            """
            try:
                if "status" in message and message.get("status") == RESPONSE_REDIRECT_STATUS_CODE:
                    scope["res_redirected"] = True
                if message and message.get("type") == "http.response.start" and message.get("status") != 307:
                    execution_context.response = message
                    execution_context.response["body"] = b""
                    scope["res_redirected"] = False
                elif message and message.get("type") == "http.response.body" and not scope["res_redirected"]:
                    if execution_context.response["body"]:
                        execution_context.response["body"] += message.get("body")
                    else:
                        execution_context.response["body"] = message.get("body")
                    try:
                        if not message.get("more_body") or message.get("more_body") == False:
                            execution_context.response = {
                                "status_code": execution_context.response.get("status"),
                                "headers": extract_headers(execution_context.response),
                                "body": execution_context.response.get("body") if execution_context.response.get("body") else None
                            }
                            self._wrapper.after_request(execution_context)
                    except Exception as e:
                        try:
                            handle_error(e, self._wrapper.error_handler, execution_context)
                        except Exception as exc:
                            logger.error("Error during the after part of Catchpoint fastapi: {}".format(exc))
            except Exception as e:
                logger.error("Error during getting res body in fast api: {}".format(e))
    

        async def wrapped_send(message):
            handle_response(message)
            await send(message)


        def handle_request(req):
            """Manipulate request for catchpoint tracer. If request has "more_body" field, then add it
            to current request body in execution context request body.

            Args:
                req (Request): Gathered from asgi receive function
            """
            if req["type"] == "http.request":
                try:
                    if "body" in req:
                        req_body = req.get("body", b"")
                        if execution_context.platform_data["request"]["body"]:
                            execution_context.platform_data["request"]["body"] += req_body
                        else:
                            execution_context.platform_data["request"]["body"] = req_body
                        if not ConfigProvider.get(config_names.CATCHPOINT_TRACE_REQUEST_SKIP, True):
                            execution_context.root_span.set_tag(constants.HttpTags['BODY'], execution_context.platform_data["request"]["body"])
                except Exception as e:
                    logger.error("Error during getting req body in fast api: {}".format(e))


        async def wrapped_receive():
            """Wrap asgi receive function to get request and add it to catchpoint tracer

            Raises:
                e: Exception occurs in receive function

            Returns:
                Request: Request gather from asgi receive function
            """
            try:
                req = await receive()
            except Exception as e:
                try:
                    handle_error(e, self._wrapper.error_handler, execution_context)
                except Exception as exc:
                    logger.error("Error during receive request fast api asgi function: {}".format(exc))
                raise e
            handle_request(req)
            return req

        try:
            await self.app(scope, wrapped_receive, wrapped_send)
        except Exception as e:
            try:
                handle_error(e, self._wrapper.error_handler, execution_context)
            except Exception as exc:
                logger.error("Error in the app fastapi: {}".format(exc))
            raise e