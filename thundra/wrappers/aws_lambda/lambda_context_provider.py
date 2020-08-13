class LambdaContextProvider:
    context = None

    @staticmethod
    def set_context(context):
        LambdaContextProvider.context = context

    @staticmethod
    def get_context():
        return LambdaContextProvider.context
