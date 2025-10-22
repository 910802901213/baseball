from datetime import datetime, timedelta
import ffmpeg

video_path_1 = "D:/GoProMocapSystem_Released/server/data/202503171731/GX010056.mp4"
video_path_2 = "D:/GoProMocapSystem_Released/server/data/202503171731/GX010066.mp4"

# 取得影片資訊，獲取 creation_time
metadata = ffmpeg.probe(video_path_1, show_entries="format_tags=creation_time", of="json")
timecode_1 = metadata["streams"][0]["tags"]["timecode"]

# 解析 UTC 起始時間，將其保持為 datetime 物件
timecode_1 = datetime.strptime(timecode_1, "%H:%M:%S:%f")

# 取得影片資訊，獲取 creation_time
metadata = ffmpeg.probe(video_path_2, show_entries="format_tags=creation_time", of="json")
timecode_2 = metadata["streams"][0]["tags"]["timecode"]

# 解析 UTC 起始時間，將其保持為 datetime 物件
timecode_2 = datetime.strptime(timecode_2, "%H:%M:%S:%f")

# time_diff = timecode_1 - timecode_2
# time_diff = time_diff.total_seconds()
#print(time_diff.total_seconds())

# 比較時間
if timecode_1 < timecode_2:
    time_diff = (timecode_2 - timecode_1).total_seconds()
    ffmpeg.input(video_path_1).output("video1_output_file.MP4", ss=0.981).run()
    ffmpeg.input(video_path_2).output("video2_output_file.MP4").run()
else:
    time_diff = (timecode_1 - timecode_2).total_seconds()
    ffmpeg.input(video_path_2).output("video2_output_file.MP4", ss=0.981).run()
    ffmpeg.input(video_path_1).output("video1_output_file.MP4").run()

