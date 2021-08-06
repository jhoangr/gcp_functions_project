
from google.cloud import storage
import ffmpeg
import os
import subprocess
import ffmpy

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
#funció que fusiona els subtítols generats (.srt) amb el vídeo (.mp4) fent servir ffmpy
def addsubtitles2video(request):

    file_name=request.args.get('video')
    index = file_name.index('.')
    file_name = file_name[:index]
    print(file_name)
    #obtenim un client del storage per descarregar i pujar objectes.
    storage_client = storage.Client()
    #indiquem el bucket del qual volem descarregar els objectes
    bucket = storage_client.bucket("sm5-hackaton.appspot.com")
    #seleccionem dos arxius(.mp4 i el .srt corresponent) i els descarreguem al /tmp
    blob = bucket.blob("subtitles/"+file_name+".srt")
    blob2 = bucket.blob("video/"+file_name+".mp4")
    blob.download_to_filename("/tmp/subs.srt")
    blob2.download_to_filename("/tmp/"+file_name+".mp4")
    
    inp="/tmp/"+file_name+".mp4"
    out="/tmp/"+file_name+"_subs.mp4"
    sub="/tmp/"+file_name+".srt"
    #cridem ffmpy i fem la fusió
    ff = ffmpy.FFmpeg(
     inputs={inp: None},
     outputs={out: '-vf subtitles=/tmp/subs.srt'}
    )
    ff.run()
    #tornem a pujar el vídeo (públic) amb els subtítols generats.
    blob3=bucket.blob("video/"+file_name+"_subs.mp4")
    blob3.upload_from_filename(out)
    blob3.make_public()
    headers=cors_enabled_function(request)
    return ("Los subtitulos y el video se han fusionado", 200, headers)
