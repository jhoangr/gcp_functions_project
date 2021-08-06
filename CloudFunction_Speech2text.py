Speech2text: Aquesta funcio agafa el audio del video i extreu el que diu en el idioma
que especifiquem, després converteix la resposta en un document srt amb el format 
dels subtitols. 

from google.cloud import videointelligence_v1 as vi
from datetime import timedelta
import srt
from google.cloud import storage
import subprocess


def transcribe_speech(video_uri, language_code, segments=None):
    video_client = vi.VideoIntelligenceServiceClient()
    features = [vi.Feature.SPEECH_TRANSCRIPTION]
    config = vi.SpeechTranscriptionConfig(
        language_code=language_code,
        enable_automatic_punctuation=True,
    )
    context = vi.VideoContext(
        segments=segments,
        speech_transcription_config=config,
    )
    request = vi.AnnotateVideoRequest(
        input_uri=video_uri,
        features=features,
        video_context=context,
    )
    print(f"Processing video: {video_uri}...")
    operation = video_client.annotate_video(request)
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



            
def print_word_timestamps(response, file_name,min_confidence=0.8):
    def keep_transcription(transcription):
        return min_confidence <= transcription.alternatives[0].confidence

    # First result only, as a single video is processed
    transcriptions = response.annotation_results[0].speech_transcriptions
    transcriptions = [t for t in transcriptions if keep_transcription(t)]

    print(f" Word Timestamps ".center(80, "-"))
    data=(f" Word Timestamps ".center(80, "-"))
    data= data +"<br>"
    subs=[]
    for transcription in transcriptions:
        best_alternative = transcription.alternatives[0]
        confidence = best_alternative.confidence
        t1 = 0
        frase = ""
        n_paraules = 0
        ide = 0
        last = 0
        for i,word in enumerate(best_alternative.words):
            if t1 == 0:
                t1 = word.start_time.total_seconds()
            
            if frase == "":
                frase = word.word
            else:
                frase = frase +" "+word.word
            n_paraules = n_paraules + 1

            if n_paraules == 18 or frase[-1] == ".":
                t2 = word.end_time.total_seconds()
                subs.append(srt.Subtitle(ide,timedelta(seconds=t1),timedelta(seconds=t2),frase))
                print(f"{confidence:4.0%} | {t1:7.3f} | {t2:7.3f} | {frase}")
                data=data+str(f"{confidence:4.0%}")+" | "+"00:" + str(f"{t1:7.3f}") + " | " + str(f"{t2:7.3f}") + " | "+ str(f"{frase}")
                data= data +"<br>"
                t1 = 0
                frase = ""
                n_paraules = 0
                ide = ide + 1

    composed=srt.compose(subs)
    index = file_name.index('.')
    file_name = file_name[:index]

    print(composed)
    storage_client = storage.Client()
    bucket = storage_client.bucket("sm5-hackaton.appspot.com")
    blob = bucket.blob("subtitles/"+file_name+".srt")
    blob.upload_from_string(composed,content_type="text/srt")
    blob.make_public()

    return composed



def main(request):
    language_code = request.args.get('language')

    storage_client = storage.Client()
    bucket = storage_client.bucket("sm5-hackaton.appspot.com")
    blob = bucket.blob("video/"+request.args.get('video'))
    name = "/tmp/video.mp4"
    blob.download_to_filename(name)
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", name],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    sec = float(result.stdout)

    segment = vi.VideoSegment(
    start_time_offset=timedelta(seconds=0),
    end_time_offset=timedelta(seconds=sec),)

    video_uri="gs://sm5-hackaton.appspot.com/video/" + request.args.get('video')
    response = transcribe_speech(video_uri, language_code, [segment])
    headers=cors_enabled_function(request)
    return (print_word_timestamps(response,request.args.get('video')), 200, headers)
