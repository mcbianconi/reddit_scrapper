import os
import shutil
import subprocess

from robot.config import (IMG_HEIGHT, IMG_WIDTH, OUTPUT_DIR,
                          RESIZED_VIDEO_SUFFIX)

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

    video_file.write(
        f" file '{submission_folder}/{comment_list[0].submission.fullname}.png'\n")
    audio_file.write(
        f" file '{submission_folder}/{comment_list[0].submission.fullname}.mp3'\n")

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


def scale_video(input_path: str):
    output = input_path + RESIZED_VIDEO_SUFFIX
    cmnd = [
        "ffmpeg", "-i", input_path, "-vf",
        f"scale={IMG_WIDTH}:{IMG_HEIGHT}",
        "-max_muxing_queue_size", "9999",
        "-y",
        output]
    subprocess.call(cmnd)
    return output


def concat_videos(video, edition_path):
    shutil.copy(video, edition_path)

    edit_list = (
        os.path.join(edition_path, "intro.mp4"),
        os.path.join(edition_path, video),
        os.path.join(edition_path, "outro.mp4"),
    )

    list_file = os.path.join(edition_path, "tmp_edit_file.txt")

    with open(list_file, "a+") as file:
        for partial_video in filter(
                lambda video: os.path.exists(video),
                edit_list):
            resized_video = scale_video(
                os.path.join(edition_path, partial_video))
            file.write(f"file '{resized_video}'\n")

    cmnd = [
        "ffmpeg",
        "-safe", "0", "-f", "concat", "-i", list_file,
        "-c", "copy", video + "_FINAL.mp4",
    ]
    process = subprocess.call(cmnd)
    os.remove(list_file)
    os.remove(os.path.join(edition_path, video))
    return process
