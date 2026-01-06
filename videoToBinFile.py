import cv2, os, struct, numpy as np, io
from moviepy import VideoFileClip

VIDEO_IN = "P:/VideoProject.mp4"
OUT_DIR  = "P:/"
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 96, 54
ROWS_PER_ZONE = 9
ZONES = 6
FPS_TARGET = 10
BPP = 2
PIXEL_FORMAT = 1

# --- Video ---
cap = cv2.VideoCapture(VIDEO_IN)
src_fps = cap.get(cv2.CAP_PROP_FPS)
if not src_fps or src_fps <= 0 or np.isnan(src_fps):
    src_fps = 30.0
step = max(1, int(round(src_fps / FPS_TARGET)))

zone_paths = [os.path.join(OUT_DIR, f"zvideo_zone{z}.bin") for z in range(ZONES)]
zone_files = [open(p, "wb") for p in zone_paths]
for f in zone_files:
    f.write(b"ZVID" + b"\x00"*20) 

def rgb888_to_rgb565(arr):
    r = (arr[:,:,0] >> 3).astype(np.uint16)
    g = (arr[:,:,1] >> 2).astype(np.uint16)
    b = (arr[:,:,2] >> 3).astype(np.uint16)
    rgb565 = (r << 11) | (g << 5) | b
    lo = (rgb565 & 0xFF).astype(np.uint8)
    hi = (rgb565 >> 8).astype(np.uint8)
    out = np.dstack((lo,hi)).reshape(-1)
    return out.tobytes()

saved_frames = 0
frame_idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    if frame_idx % step != 0:
        frame_idx += 1
        continue
    small = cv2.resize(frame, (W, H), interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    for z, f in enumerate(zone_files):
        r0, r1 = z*ROWS_PER_ZONE, (z+1)*ROWS_PER_ZONE
        f.write(rgb888_to_rgb565(rgb[r0:r1,:,:]))
    saved_frames += 1
    frame_idx += 1
cap.release()

for f in zone_files:
    f.flush()
    f.seek(0)
    f.write(struct.pack("<4sHHHHIB7s", b"ZVID", W, H,
                        ROWS_PER_ZONE, BPP, saved_frames,
                        PIXEL_FORMAT, b"\x00"*7))
    f.close()

# --- Audio ---
clip = VideoFileClip(VIDEO_IN)
wav_path = os.path.join(OUT_DIR, "audio_22k_mono.wav")
pcm_path = os.path.join(OUT_DIR, "audio_22k_mono.pcm")
clip.audio.write_audiofile(
    wav_path,
    fps=22050,
    nbytes=2,
    codec="pcm_s16le",
    ffmpeg_params=["-ac","1"]
)
clip.close()

# Extract PCM bytes from WAV
with open(wav_path, "rb") as f:
    data = f.read()
buf = io.BytesIO(data)
riff = buf.read(12)
pcm_bytes = None
import struct as st
while True:
    ch = buf.read(8)
    if len(ch) < 8: break
    cid, clen = ch[:4], st.unpack("<I", ch[4:8])[0]
    if cid == b"data":
        pcm_bytes = buf.read(clen)
        break
    else:
        buf.seek(clen, 1)
if pcm_bytes is None:
    pcm_bytes = data[44:]
with open(pcm_path, "wb") as f:
    f.write(pcm_bytes)

print("Done. Files written to", OUT_DIR)
