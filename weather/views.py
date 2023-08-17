from rest_framework.decorators import api_view
from rest_framework.response import Response

import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent 

@api_view(['GET'])
def ping(request):

    version = (BASE_DIR / 'VERSION').read_text().strip()
    
    data = {
        "name": "weatherservice",
        "status": "ok",
        "version": version
    }
    
    return Response(data)