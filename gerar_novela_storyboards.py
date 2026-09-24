import asyncio, base64, json, os, shutil, sqlite3, subprocess, sys, time, re, html

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import urllib.request

WORK = r"C:\xampp\htdocs\agente\output\novela_bizu"
os.makedirs(WORK, exist_ok=True)
SHOTS = os.path.join(WORK, "shots")
CLIPS = os.path.join(WORK, "clips")
os.makedirs(SHOTS, exist_ok=True)
os.makedirs(CLIPS, exist_ok=True)

ADAPTER = "http://127.0.0.1:5123/v1/images/generations"
DB_PATH = r"C:\xampp\htdocs\agente\LocalMiniDrama\backend-node\data\drama_generator.db"
FONT = r"C\:/Windows/Fonts/arialbd.ttf"
FOTO_FMT = 1080
cp = 0


def cmd(args, timeout=600):
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-800:])
    return r.stdout


def gen_image(prompt_val, path):
    body = json.dumps({"prompt": prompt_val, "size": "1080x1920", "n": 1}).encode()
    req = urllib.request.Request(ADAPTER, data=body, headers={"Content-Type": "application/json"}, method="POST")
    out = json.load(urllib.request.urlopen(req, timeout=300))
    url = out["data"][0]["url"]
    if url.startswith("data:"):
        raw = base64.b64decode(url.split(",", 1)[1])
    else:
        raw = urllib.request.urlopen(url, timeout=300).read()
    with open(path, "wb") as f:
        f.write(raw)
    return path


def annotate_caption(img_path, text):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.open(img_path).convert("RGB")
    font = ImageFont.truetype(r"C:/Windows/Fonts/arialbd.ttf", 46)
    d = ImageDraw.Draw(im)
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if d.textlength(test, font=font) <= 980:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    lines = lines[:3]
    y = im.height - 30 - 46 * len(lines) - 12
    for ln in lines:
        d.text((20, y), ln, font=font, fill="white", stroke_width=6, stroke_fill="black")
        y += 58
    im.save(img_path, "JPEG", quality=92)


def make_clip(img_path, out_path, dur):
    vf = (
        "zoompan=z='zoom+0.0012':d=120:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=24"
    )
    cmd(["ffmpeg", "-y", "-i", img_path, "-vf", vf, "-t", str(dur), "-c:v", "libx264", "-preset", "fast", "-crf", "23", out_path])


def clean(t):
    if not t:
        return ""
    t = re.sub(r"^\d+:\s*", "", str(t))
    return t.strip()


db = sqlite3.connect(DB_PATH)
db.row_factory = sqlite3.Row
rows = db.execute(
    "SELECT storyboard_number, action, dialogue, image_prompt FROM storyboards WHERE episode_id=2 AND deleted_at IS NULL ORDER BY storyboard_number"
).fetchall()
print("shots:", len(rows))

# 1. imagens
for r in rows:
    n = r["storyboard_number"]
    img = os.path.join(SHOTS, f"shot_{n:02d}.jpg")
    if not os.path.exists(img):
        prompt_v = r["image_prompt"] or (clean(r["action"]) + ", cinematic Brazilian drama, vertical")
        gen_image(prompt_v, img)
        print("img", n, "ok", os.path.getsize(img) // 1024, "KB")
        time.sleep(2)

# 2. legenda + clipes (5s cada)
seg_meta = []
for r in rows:
    n = r["storyboard_number"]
    img = os.path.join(SHOTS, f"shot_{n:02d}.jpg")
    cap = clean(r["dialogue"]) or clean(r["action"])
    if cap:
        annotate_caption(img, cap)
    out = os.path.join(CLIPS, f"clip_{n:02d}.mp4")
    if not os.path.exists(out):
        make_clip(img, out, 5.0)
    seg_meta.append((out, cap))
    print("clip", n, "ok")

# 3. concat
lst = os.path.join(WORK, "list.txt")
with open(lst, "w", encoding="utf-8") as f:
    for out, _ in seg_meta:
        f.write(f"file '{out}'\n")
raw = os.path.join(WORK, "raw.mp4")
cmd(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", raw])

# 4. narração (voz por shot via edge-tts, juntando com silêncio)
async def narrar():
    nums = ""
    for out, cap in seg_meta:
        nums += (cap[:140] + ". ") if cap else ""
    mp3 = os.path.join(WORK, "narr.mp3")
    if not os.path.exists(mp3):
        import edge_tts
        comm = edge_tts.Communicate(nums, voice="pt-BR-AntonioNeural")
        await comm.save(mp3)
        print("narr ok")
    return mp3

narr = asyncio.run(narrar())
final = os.path.join(os.path.expanduser("~"), "Desktop", "mini_novela_BIZU_story.mp4")
cmd(["ffmpeg", "-y", "-i", raw, "-i", narr, "-map", "0:v", "-map", "1:a", "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", final])
sz = os.path.getsize(final) // 1048576
dur = cmd(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", final]).strip()
print(f"FINAL: {final} | {sz}MB | {float(dur):.1f}s")