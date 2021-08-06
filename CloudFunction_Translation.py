

from google.cloud import translate
from google.cloud import storage
import srt
import os

def traducir(file_name,target):
    storage_client = storage.Client()
    bucket = storage_client.bucket("sm5-hackaton.appspot.com")
    blob = bucket.blob("subtitles/"+file_name+".srt")
    blob.download_to_filename("/tmp/subs.srt")
    fitxer = open("/tmp/subs.srt","r")
    subs = fitxer.read()
    fitxer.close()
    originals = list(srt.parse(subs))
    project_id = "sm5-hackaton"
    location = "global"
    parent = f"projects/{project_id}/locations/{location}"
    client = translate.TranslationServiceClient()
    for i,sub in enumerate(originals):
        new = ""
        response = client.translate_text(
            contents=[sub.content],
            target_language_code=target,
            parent=parent,
        )
        for translation in response.translations:
            new = new + translation.translated_text
        originals[i].content = new
    composed=srt.compose(originals)
    bucket = storage_client.bucket("sm5-hackaton.appspot.com")
    blob = bucket.blob("subtitles/"+file_name+".srt")
    blob.upload_from_string(composed,content_type="text/srt")
    blob.make_public()
    return composed

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


def main(request):
    file_name=request.args.get('video')
    index = file_name.index('.')
    file_name = file_name[:index]
    language_code = request.args.get('language')
    headers=cors_enabled_function(request)
    return (traducir(file_name,language_code), 200, headers)
