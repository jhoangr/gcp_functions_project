

from google.cloud import videointelligence
from google.cloud.videointelligence import enums, types

#funció per detectar els labels.
def detect_labels(video_uri, mode, segments=None):
    #obtenim un video_client per comunicarnos amb l'api.
    video_client = videointelligence.VideoIntelligenceServiceClient()
    #configurem les característiques que volem fer servir.
    features = [enums.Feature.LABEL_DETECTION]
    config = types.LabelDetectionConfig(label_detection_mode=mode)
    context = types.VideoContext(
        segments=segments,
        label_detection_config=config,
    )
    #processem el video
    print(f'Processing video "{video_uri}"...')
    operation = video_client.annotate_video(
        input_uri=video_uri,
        features=features,
        video_context=context,
    )
    #returnem les etiquetes.
    return operation.result()


#funció necessaria per generar els headers
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

#funció per ordenar les labels a partir del % de confidence
def sort_by_first_segment_confidence(labels):
    labels.sort(key=lambda label: label.segments[0].confidence, reverse=True)


def category_entities_to_str(category_entities):
    if not category_entities:
        return ""
    entities = ", ".join([e.description for e in category_entities])
    return f" ({entities})"

#generem la resposta de labels, primer el número de etiquetes. Després per cada etiqueta, % confidence,temps_inicial,temps_final i el nom.
def print_video_labels(response):
    # First result only, as a single video is processed
    labels = response.annotation_results[0].segment_label_annotations
    sort_by_first_segment_confidence(labels)

    print(f" Video labels: {len(labels)} ".center(80, "-"))
    data=(f" Video labels: {len(labels)} ".center(80, "-"))
    data= data +"<br>"
    for label in labels:
        categories = category_entities_to_str(label.category_entities)
        for segment in label.segments:
            confidence = segment.confidence
            start_ms = segment.segment.start_time_offset.ToMilliseconds()
            end_ms = segment.segment.end_time_offset.ToMilliseconds()
            print(
                f"{confidence:4.0%}",
                f"{start_ms:>7,}",
                f"{end_ms:>7,}",
                f"{label.entity.description}{categories}",
                
            )
            data= data + str(f"{confidence:4.0%}")+"|"+ str(f"{start_ms:>7,}")+"|"+str(f"{end_ms:>7,}")+"|"+str(f"{label.entity.description}{categories}")
            data= data +"<br>"
    return data
            



def main(request):
    #especifiquem les opcions per detectar les etiquetes
    mode = enums.LabelDetectionMode.SHOT_MODE
    segment = types.VideoSegment()
    segment.start_time_offset.FromSeconds(0)
    segment.end_time_offset.FromSeconds(37)
    #generem la uri del video de gcp-storage
    video_uri="gs://sm5-hackaton.appspot.com/video/" + request.args.get('video')
    #cridem la funció detec_labels
    response = detect_labels(video_uri, mode, [segment])
    #generem la capçalera per la resposta.
    headers=cors_enabled_function(request)
    #returnem les labels
    return (print_video_labels(response), 200, headers)
