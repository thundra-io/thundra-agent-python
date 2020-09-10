import wrapt


class CursorWrapper(wrapt.ObjectProxy):

    def __init__(self, cursor, connection_wrapper, integration):
        super(CursorWrapper, self).__init__(cursor)
        self._self_connection = connection_wrapper
        self.integration = integration

    def execute(self, *args, **kwargs):
        return self.integration.run_and_trace(
            self.__wrapped__.execute,
            self._self_connection,
            args,
            kwargs,
        )

    def callproc(self, *args, **kwargs):
        return self.integration.run_and_trace(
            self.__wrapped__.callproc,
            self._self_connection,
            args,
            kwargs,
        )

    def __enter__(self):
        # raise appropriate error if api not supported (should reach the user)
        self.__wrapped__.__enter__
        return self


class ConnectionWrapper(wrapt.ObjectProxy):
    def __init__(self, conn, integration=None):
        self.integration = integration

    def cursor(self, *args, **kwargs):
        cursor = self.__wrapped__.cursor(*args, **kwargs)
        return CursorWrapper(cursor, self, integration=self.integration)
