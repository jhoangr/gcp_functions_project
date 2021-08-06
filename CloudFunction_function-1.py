function-1: Aquesta funcio detecta la quantitat de frames que te el video y el
seu posicionament temporal.

from google.cloud import videointelligence
from google.cloud.videointelligence import enums


def detect_shot_changes(video_uri):
    video_client = videointelligence.VideoIntelligenceServiceClient()
    features = [enums.Feature.SHOT_CHANGE_DETECTION]

    print(f'Processing video "{video_uri}"...')
    operation = video_client.annotate_video(
        input_uri=video_uri,
        features=features,
    )
    return operation.result()



def cors_enabled_function(request):
    # For more information about CORS and CORS preflight requests, see
    # https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request
    # for more information.

    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    return  headers

#funció que rep els video shots generats per l'api i genera un string com a resposta per retornar.
#el format és Número de shots. Índex del shot, temps_inicial i temps_final.
def print_video_shots(response):
    # First result only, as a single video is processed
    shots = response.annotation_results[0].shot_annotations
    print(f" Video shots: {len(shots)} ".center(40, "-"))
    data=(f" Video shots: {len(shots)} ".center(40, "-"))
    data= data +"<br>"
    for i, shot in enumerate(shots):
        start_ms = shot.start_time_offset.ToMilliseconds()
        end_ms = shot.end_time_offset.ToMilliseconds()
        data = data + (f"{i+1:>3} | {start_ms:>7,} | {end_ms:>7,}")
        data= data +"<br>"
    return data


def main(request):
    #generem la capçalera 
    headers=cors_enabled_function(request)
    #construim la url del objecte a tractar
    video_uri="gs://sm5-hackaton.appspot.com/video/" + request.args.get('video')
    #cridem a la funció que detecta els canvis de "shots"
    response = detect_shot_changes(video_uri)
    #retornem els shots del vídeo
    return (print_video_shots(response), 200, headers)
