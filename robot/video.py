import os
import subprocess
from robot.config import OUTPUT_DIR

VIDEO_FILE_NAME = "video_input_list"
AUDIO_FILE_NAME = "audio_input_list"


def make_files(comment_list):
    submission_folder = os.path.join(
        OUTPUT_DIR, comment_list[0].submission.fullname)
    video_input_list = os.path.join(submission_folder, VIDEO_FILE_NAME)
    audio_input_list = os.path.join(submission_folder, AUDIO_FILE_NAME)
    comment_list_file_path = os.path.join(submission_folder, "comment_list")

    video_file = open(video_input_list, "a+")
    audio_file = open(audio_input_list, "a+")
    comment_list_file = open(comment_list_file_path, "a+")

    video_file.write(f" file '{submission_folder}/{comment_list[0].submission.fullname}.png'\n")
    audio_file.write(f" file '{submission_folder}/{comment_list[0].submission.fullname}.mp3'\n")

    for c in comment_list:
        video_file.write(f" file '{submission_folder}/{c.fullname}.png'\n")
        audio_file.write(f" file '{submission_folder}/{c.fullname}.mp3'\n")
        comment_list_file.write(f"{c.fullname}\n")

    video_file.close()
    audio_file.close()


def create_submission_video(submission):
    submission_folder = os.path.join(OUTPUT_DIR, submission.fullname)

    video_file = os.path.join(submission_folder, VIDEO_FILE_NAME)
    audio_file = os.path.join(submission_folder, AUDIO_FILE_NAME)

    video_title = submission.title.replace(" ", "_")
    output_video = os.path.join(submission_folder, video_title + ".mp4")
    cmnd = [
        "ffmpeg -r 24 -f concat -safe 0 -i", video_file,
        "-f concat -safe 0 -i", audio_file,
        "-c:a aac -pix_fmt yuv420p -crf 23 -r 24 -shortest -y", output_video]

    p = subprocess.call(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def test_video_creatin():
    submission_folder = '/data/code/projetos/upwork/reddit_speaker/output/t3_d4i8np'

    video_file = os.path.join(submission_folder, VIDEO_FILE_NAME)
    audio_file = os.path.join(submission_folder, AUDIO_FILE_NAME)

    video_title = "This is a test for a submission title".replace(" ", "_")
    output_video = os.path.join(submission_folder, video_title + ".mp4")
    cmnd = ["ffmpeg",
            "-r",
            "24",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            video_file,
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            audio_file,
            "-c:a",
            "aac",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "23",
            "-r",
            "24",
            "-shortest",
            "-y",
            "output_video",
            ]

    p = subprocess.call(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(p)
