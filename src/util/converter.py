import ffmpeg
import os
import subprocess

# Codec maps for video formats, audio formats, and image formats.
VIDEO_CODEC_MAP = {
    ".mp4": ("libx264", "aac"),
    ".mkv": ("libx264", "aac"),
    ".webm": ("libvpx-vp9", "libopus"),
    ".avi": ("libxvid", "mp3"),
    ".mov": ("libx264", "aac")
}
AUDIO_CODEC_MAP = {
    ".mp3": "libmp3lame", 
    ".wav": "pcm_s16le",
    ".aac": "aac",
    ".flac": "flac",
    ".ogg": "libvorbis"
}
IMAGE_CODEC_MAP = { 
    ".jpg": "mjpeg",
    ".jpeg": "mjpeg",
    ".png": "png",
    ".webp": "libwebp",
    ".bmp": "bmp",
    ".tiff": "tiff"
}

def detect_hw_accelerator():
    """Detect available hardware encoder."""
    try:
        output = subprocess.check_output(['ffmpeg', '-encoders'], stderr=subprocess.DEVNULL).decode()
        if 'h264_nvenc' in output:
            return 'nvenc'
        elif 'h264_qsv' in output:
            return 'qsv'
        elif 'h264_vaapi' in output:
            return 'vaapi'
    except Exception:
        pass
    return None


def convert_video(input_file: str, output_file: str, video_codec: str = "", audio_codec: str = ""):
    if not video_codec or not audio_codec:
        ext = os.path.splitext(output_file)[1].lower()

        hw = detect_hw_accelerator()
        if hw:
            # try hardware codec first
            hw_ext_map = {
                "nvenc": f"{ext}_hw",
                "qsv": f"{ext}_qsv",
                "vaapi": f"{ext}_vaapi"
            }
            hw_ext = hw_ext_map.get(hw, "")
            video_codec, audio_codec = VIDEO_CODEC_MAP.get(hw_ext, VIDEO_CODEC_MAP.get(ext))
        else:
            # fallback to software codec
            video_codec, audio_codec = VIDEO_CODEC_MAP.get(ext, ("libx264", "aac"))

    try:
        ffmpeg.input(input_file).output(
            output_file,
            vcodec=video_codec,
            acodec=audio_codec
        ).run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        print('Video conversion successful!')
    except ffmpeg.Error as e:
        print('Error converting video:', e.stderr.decode())

def convert_audio(input_file: str, output_file: str, audio_codec: str = 'mp3'):
    if audio_codec == "": # If audio codec is not specified, determine it based on the output file extension.
            ext = os.path.splitext(output_file)[1].lower()
            audio_codec = AUDIO_CODEC_MAP.get(ext, "libmp3lame")
    try:
        (
            ffmpeg
            .input(input_file)
            .output(output_file,vn=True, acodec=audio_codec)
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        print('Audio conversion successful!')
    except ffmpeg.Error as e:
        print('Error converting audio:', e.stderr.decode())

def convert_image(input_file: str, output_file: str, image_codec: str = ""):
    if image_codec == "": # If image codec is not specified, determine it based on the output file extension.
        ext = os.path.splitext(output_file)[1].lower()
        image_codec = IMAGE_CODEC_MAP.get(ext, "png")

    try:
        (
            ffmpeg
            .input(input_file)
            .output(output_file, vcodec=image_codec, frames=1)
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        print("Image conversion successful!")
    except ffmpeg.Error as e:
        print("Error converting image:", e.stderr.decode())
