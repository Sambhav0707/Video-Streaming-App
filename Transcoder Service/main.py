from secrets_keys import Settings
import boto3
import subprocess  # subprocess allow us to run diff process at the system level
import os
from pathlib import Path
import requests


settings = Settings()


class VideoTranscoder:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            region_name=settings.REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,  # passing these because ECS will need them to spin up the container
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    """
    A function to get the content types of files like is it 
    mp4 , m3u8 ...etc
    """

    def _get_content_type(self, file_path: str):
        if file_path.endswith(".m3u8"):
            return "application/vnd.apple.mpegurl"
        elif file_path.endswith(".ts"):
            return "video/MP2T"
        elif file_path.endswith(".mpd"):
            return "application/dash+xml"
        elif file_path.endswith(".m4s"):
            return "video/mp4"

    """
    Function to Download the videos from S3 and saving to the local path that we will mention 
    """

    def download_video(self, local_path):
        print(
            f"Downloading from Bucket: '{settings.S3_BUCKET_NAME}' with Key: '{settings.S3_KEY}'"
        )
        # downloading from the s3 bucket
        self.s3_client.download_file(
            settings.S3_BUCKET_NAME,
            settings.S3_KEY,
            local_path,
        )

    """
    After downloading from the s3 we have to transcod the video 
    so we will need input_path :- from where we have to take the video 
    output_dir:- to where we have to upload the transcoded videos
    """

    def transcode_video(self, input_path, output_dir):
        # Command for HLS
        cmdHLS = [
            "ffmpeg",  # invoking the ffmpeg process
            # basically if you have a '-' that means that is the key and after that there is value
            "-i",  # input path
            input_path,  # giving the input path
            "-filter_complex",  # filter_complex takes diff inputs and apply filters to them
            "[0:v]split=3[v1][v2][v3];"  # so here we are taking the first input i.e. [0:v] and splitting it into three diff streams :- [v1][v2][v3]
            # so here we are scalling the v1 stream to 640 by 360 i.e. 360p resolution
            # we are using fast_biliean algo for the concvertion
            "[v1]scale=640:360:flags=fast_bilinear[360p];"
            "[v2]scale=1280:720:flags=fast_bilinear[720p];"
            "[v3]scale=1920:1080:flags=fast_bilinear[1080p]",
            # so here we are mapping the stream 360p , 720p and 1080p to there req output streams
            "-map",
            "[360p]",
            "-map",
            "[720p]",
            "-map",
            "[1080p]",
            "-map",  # here we  are keeping the original audio and mapping it to the output streams
            "[0:a]",
            # here we are encoding the video stream with a h264 encoder :- libx264
            "-c:v",
            "libx264",
            "-preset",  # then we are setting the encoding to be fast trading off the compression efficiency bcz in live streaming application we need fast encoding
            "veryfast",
            # here we are setting the encoder's compression quality to be high
            "-profile:v",
            "high",
            # here we have set the h64 level to 4.1
            # so it defines the compression and ensure compatibility with diff streams
            "-level:v",
            "4.1",
            # here we are setting up the gop that Group of Pictures to 48
            # this ensures a boundary b/w streams segments so that user can switch to any other stream seaminglessly
            "-g",
            "48",
            # here we are setting the minimun interval b/w frames to 48 it helps in ABS
            "-keyint_min",
            "48",
            # then we are setting the screen change to 0
            # that enables the 48 key frames consistenly throughout the frames
            "-sc_threshold",
            "0",
            # here we are ssetting the bit rate for diff streams
            "-b:v:0",
            "1000k",  # 360p :- 1000 kilo bit per second
            "-b:v:1",
            "4000k",
            "-b:v:2",
            "8000k",
            # here we are setting the audio codec to AAC
            "-c:a",
            "aac",
            # here we are setting the audio bitrate to 128 kilo bits per second
            "-b:a",
            "128k",
            "-f",  # this specifies the output format to hls
            "hls",
            "-hls_time",  # here we are tellin that every segment should be 6 seconds long
            "6",
            # then we are setting the hls playlist format to vod :- Video on Demand
            # generally that is used for static content but for live streaming others are used
            "-hls_playlist_type",
            "vod",
            "-hls_flags",  # here we are making every segment independent of each other so that they can be decoded without refference of the previous one
            "independent_segments",
            # now we are setting the type of the segments to mpegts
            # it is widely supported container format for streaming
            "-hls_segment_type",
            "mpegts",
            # here we are setting the playlist to 0 bcz it is necessary for us to have the full size rather than a sliding window for VOD
            "-hls_list_size",
            "0",
            # then we are setting the master playlist name :- this container all the stuff
            "-master_pl_name",
            "master.m3u8",
            # now we are specifying the video streams to the audio streams
            "-var_stream_map",
            "v:0 v:1 v:2",
            # here we are changing the naming pattern for segment files
            # output_dir followed by version [360,720] followed by segment number that will be 000 , 001 ....
            "-hls_segment_filename",
            f"{output_dir}/%v/segment_%03d.ts",
            # here we are setting the playlist.m3u8 file that is :-
            # - output_dir
            #   - 1080p
            #     - segment 000
            #     - segment 001
            #      .
            #      .
            #      .
            #      .
            #     - the playlist.m3u8 [with which the segment files will cordinate]
            f"{output_dir}/%v/playlist.m3u8",
        ]
        # Command for DASH
        cmd = [
            "ffmpeg",
            "-i",
            input_path,
            "-filter_complex",
            "[0:v]split=3[v1][v2][v3];"
            "[v1]scale=640:360:flags=fast_bilinear[360p];"
            "[v2]scale=1280:720:flags=fast_bilinear[720p];"
            "[v3]scale=1920:1080:flags=fast_bilinear[1080p]",
            # 360p video stream
            "-map",
            "[360p]",
            "-c:v:0",
            "libx264",
            "-b:v:0",
            "1000k",
            "-preset",
            "veryfast",
            "-profile:v",
            "high",
            "-level:v",
            "4.1",
            "-g",
            "48",
            "-keyint_min",
            "48",
            # 720p video stream
            "-map",
            "[720p]",
            "-c:v:1",
            "libx264",
            "-b:v:1",
            "4000k",
            "-preset",
            "veryfast",
            "-profile:v",
            "high",
            "-level:v",
            "4.1",
            "-g",
            "48",
            "-keyint_min",
            "48",
            # 1080p video stream
            "-map",
            "[1080p]",
            "-c:v:2",
            "libx264",
            "-b:v:2",
            "8000k",
            "-preset",
            "veryfast",
            "-profile:v",
            "high",
            "-level:v",
            "4.1",
            "-g",
            "48",
            "-keyint_min",
            "48",
            # Audio stream
            "-map",
            "0:a",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            # DASH specific settings
            "-use_timeline",
            "1",
            "-use_template",
            "1",
            "-window_size",
            "5",
            "-adaptation_sets",
            "id=0,streams=v id=1,streams=a",
            "-f",
            "dash",
            f"{output_dir}/manifest.mpd",
        ]

        # running the proccess
        process = subprocess.run(cmd)

        # if process doesn't return 0 raise expection
        if process.returncode != 0:
            print(process.stderr)
            raise Exception("Transcoding failed")

    """
    Fuction for uploading the transcoded videos
    """

    def upload_files(self, prefix: str, local_dir):
        # Looping over the output / local directory and uploading the results to processed video
        """
        This os.walk will return a tuple of three things Iterator[tuple[AnyStr, list[AnyStr], list[AnyStr]]]
        """
        for root, _, files in os.walk(local_dir):
            """
            Then we are looping thorough each file in files
            """
            for file in files:

                local_path = os.path.abspath(os.path.join(root, file))
                if not os.path.exists(local_path):
                    print(f"Warning: File {local_path} does not exist. Skipping.")
                    continue
                print(f"Uploading {local_path} to S3...")

                """
                NOw we cant really upload just the local path to s3 because 2 video might have the same dir name and so on 
                so we need a differentiator in this and that is the s3_key :- BUT the s3_key from raw videos can we same for two videos 
                so in reality we will be joining a userid and a random uid to the prefix 
                so in the end it is :- videos/{user_id}/{ruuid}/{path} so this will be the s3_key
                """
                s3_key = f"{prefix}/{os.path.relpath(local_path , local_dir)}"

                # uploadin it to the s3 bucket :- processed videos
                # here local path mean the files where from to upload
                self.s3_client.upload_file(
                    local_path,
                    settings.S3_PROCESSED_VIDEOS_BUCKET,
                    s3_key,
                    # we need extra args because we need to explicitly tell that the ACL needs to be publically read and
                    # the content type should be mentioned
                    ExtraArgs={
                        "ACL": "public-read",
                        "ContentType": self._get_content_type(local_path),
                    },
                )

    """
    This process_video function acts as an orchestrator for a complete video processing pipeline. 
    It manages the lifecycle of a video file from download to upload, including setting up 
    temporary workspace directories and ensuring they are cleaned up afterward.
    """

    def process_video(self):
        """
        Workspace Setup:-
        """
        work_dir = Path("/tmp/workspace")  # sets up a temporary directory
        work_dir.mkdir(exist_ok=True)
        input_path = work_dir / "input.mp4"  # defines paths for an input file
        output_path = (
            work_dir / "output"
        )  # output directory (output) inside this workspace.
        output_path.mkdir(exist_ok=True)

        """
         The Core Pipeline (Try Block)
        """
        try:
            self.download_video(input_path)  # Downloads the source video
            self.transcode_video(
                str(input_path), str(output_path)
            )  # Takes the downloaded input video and transcodes/converts it
            self.upload_files(
                settings.S3_KEY, str(output_path)
            )  # Uploads all the newly transcoded files from the output directory to an AWS S3 bucket
            self.update_video()
        except Exception as e:
            raise Exception("Something Went wrong") from e
        finally:
            """
            Cleanup (Finally Block)
            """
            if input_path.exists():
                input_path.unlink()  # It checks if the input.mp4 file exists and deletes it

            """
            It checks if the output directory exists and uses shutil.rmtree() 
            to delete the directory and recursively remove all files inside it.

            NOTE: import shutil is done locally inside the if statement j
            just for the cleanup step.
            """
            if output_path.exists():
                import shutil

                shutil.rmtree(str(output_path))
        
    def update_video(self):
        try:
            response = requests.put(
                f"{settings.BACKEND_URL}/videos?id={settings.S3_KEY}"
            )
            print(response.json())
            return response.json()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    transcoder = VideoTranscoder()
    transcoder.process_video()
