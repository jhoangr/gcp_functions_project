# gcp_functions_project
A project that uses gcp functions to get information from a video (labels and subtitles) using VideoIntelligence API, and it's possible to translate the subtitles. The video is first uploaded to CloudStorage 

Cloud_function-1 allows detecting the frames changes inside de video. 

Cloud_function-2 is used for generating the video with subtitles using ffmpy.

Cloud_function-3 generates labels from a video.
