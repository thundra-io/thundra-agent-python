from thundra.application_info_provider import ApplicationInfoProvider

_application_info_provider = None
_application_info = None

def set_application_info_provider(application_info_provider):
    global _application_info_provider
    _application_info_provider = application_info_provider


def get_application_info():
    global _application_info_provider
    if isinstance(_application_info_provider, ApplicationInfoProvider):
        return _application_info_provider.get_application_info()
    
    return None


def parse_application_info():
    global _application_info
    _application_info = get_application_info()