import os
import sys
import zipfile
import requests
import subprocess
import pygame
import yaml
from pathlib import Path

# ==============================
# Directories
# ==============================

SONATA_DIR = Path.cwd()
SONGS_DIR = SONATA_DIR / "Songs"
ENGINE_DIR = SONATA_DIR / "engine"
FFMPEG_DIR = ENGINE_DIR / "ffmpeg"

SONGS_DIR.mkdir(exist_ok=True)
ENGINE_DIR.mkdir(exist_ok=True)

HOME = Path.home()
OSU_DIR = HOME / "AppData" / "Local" / "osu!" / "Songs"
POSSIBLE_STEAM_DIRS = [
    Path("C:/Program Files (x86)/Steam"),
    Path("C:/Program Files/Steam"),
    HOME / "AppData" / "Local" / "Steam"
]

QUAVER_DIR = None

for steam in POSSIBLE_STEAM_DIRS:
    candidate = steam / "steamapps" / "common" / "Quaver" / "Songs"
    if candidate.exists():
        QUAVER_DIR = candidate
        break

# ==============================
# Skin System
# ==============================

SKINS_DIR = SONATA_DIR / "Skins"
SKINS_DIR.mkdir(exist_ok=True)


def import_skins():

    source_skins = SONATA_DIR / "Skins_Source"

    if not source_skins.exists():
        return

    for folder in source_skins.iterdir():

        if not folder.is_dir():
            continue

        def_settings = SKINS_DIR / folder.name
        def_settings.mkdir(exist_ok=True)

        for item in folder.glob("*"):

            if item.is_file():

                with open(item, "rb") as src:
                    with open(def_settings / item.name, "wb") as out:
                        out.write(src.read())

# ==============================
# Settings
# ==============================

def def_settings():
    return {
        "keys": ["d", "f", "j", "k"],
        "volume": 1.0
    }

settings = def_settings()

# ==============================
# FFmpeg Auto Installer
# ==============================

FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"


def install_ffmpeg():

    if (FFMPEG_DIR / "ffmpeg.exe").exists():
        return

    print("Downloading FFmpeg...")

    zip_path = ENGINE_DIR / "ffmpeg.zip"

    r = requests.get(FFMPEG_URL, stream=True, timeout=15)

    with open(zip_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    print("Extracting FFmpeg...")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(ENGINE_DIR)

    for root, dirs, files in os.walk(ENGINE_DIR):
        for file in files:
            if file == "ffmpeg.exe":
                src = Path(root) / file
                dst = FFMPEG_DIR / "ffmpeg.exe"
                FFMPEG_DIR.mkdir(exist_ok=True)
                os.rename(src, dst)
                break

    print("FFmpeg installed")

# ==============================
# Chart Data Structure
# ==============================

class Chart:

    def __init__(self):

        self.notes = []
        self.audio = None
        self.bpm = 120
        self.keys = 4
        self.difficulty = "Unknown"
        self.title = "Unknown"
        self.artist = "Unknown"

# ==============================
# OSU Parser (Mania only)
# ==============================

def parse_osu(path):

    chart = Chart()

    with open(path, "r", encoding="utf8", errors="ignore") as f:

        mode = None

        for line in f:

            if line.startswith("Mode:"):
                mode = int(line.split(":")[1])

            if line.startswith("CircleSize:"):
                chart.keys = int(float(line.split(":")[1]))

            if line.startswith("Title:"):
                chart.title = line.split(":",1)[1].strip()

            if line.startswith("Artist:"):
                chart.artist = line.split(":",1)[1].strip()

            if line.startswith("AudioFilename"):
                chart.audio = line.split(":")[1].strip()

            if line.count(",") >= 4:

                if mode != 3:
                    continue

                parts = line.split(",")

                x = int(parts[0])
                time = int(parts[2])

                column = int(x / (512 / chart.keys))

                chart.notes.append((time, column))

    return chart

# ==============================
# Quaver Parser (.qua YAML)
# ==============================

def parse_qua(path):

    chart = Chart()

    with open(path, "r", encoding="utf8") as f:

        data = yaml.safe_load(f)

    chart.title = data.get("Title", "Unknown")
    chart.artist = data.get("Artist", "Unknown")
    chart.audio = data.get("AudioFile")

    for note in data.get("HitObjects", []):

        time = note.get("StartTime")
        lane = note.get("Lane")

        chart.notes.append((time, lane))

    chart.keys = data.get("Mode", 4)

    return chart

# ==============================
# Stepmania Parser
# ==============================

def parse_sm(path):

    chart = Chart()

    with open(path, "r", encoding="utf8", errors="ignore") as f:

        lines = f.readlines()

    for line in lines:

        if line.startswith("#TITLE:"):
            chart.title = line.replace("#TITLE:","").replace(";","")

        if line.startswith("#ARTIST:"):
            chart.artist = line.replace("#ARTIST:","").replace(";","")

        if line.startswith("#MUSIC:"):
            chart.audio = line.replace("#MUSIC:","").replace(";","")

    time = 0

    for line in lines:

        line=line.strip()

        if len(line)==4 and set(line).issubset({"0","1","2","3","4"}):

            for i,c in enumerate(line):

                if c=="1":
                    chart.notes.append((time,i))

            time+=120

    return chart

# ==============================
# Chart Loader
# ==============================

def load_chart(path):

    ext = Path(path).suffix.lower()

    if ext==".osu":
        return parse_osu(path)

    if ext==".qua":
        return parse_qua(path)

    if ext==".sm":
        return parse_sm(path)

    raise Exception("Unsupported format")

# ==============================
# Song Library Importer
# ==============================

def import_osu_songs():

    if not OSU_DIR.exists():
        return

    for folder in OSU_DIR.iterdir():

        if not folder.is_dir():
            continue

        has_mania = False

        for file in folder.glob("*.osu"):

            with open(file, "r", encoding="utf8", errors="ignore") as f:
                text = f.read()
                if "Mode: 3" in text:
                    has_mania = True
                    break

        if has_mania:
            chart_name = folder.name
            def_settings.mkdir(exist_ok=True)

            # Copy entire folder (audio + bg + charts)
            for item in folder.glob("*"):
                if item.is_file():
                    try:
                        with open(item, "rb") as src:
                            with open(def_settings / item.name, "wb") as out:
                                out.write(src.read())
                    except Exception as e:
                        print("Copy error:", e)


def import_quaver_songs():

    if not QUAVER_DIR or not QUAVER_DIR.exists():
        return

    for folder in QUAVER_DIR.iterdir():

        if not folder.is_dir():
            continue

        for file in folder.glob("*.qua"):

            chart_name = folder.name
            def_settings.mkdir(exist_ok=True)

            # Copy entire folder
            for item in folder.glob("*"):
                if item.is_file():
                    try:
                        with open(item, "rb") as src:
                            with open(def_settings / item.name, "wb") as out:
                                out.write(src.read())
                    except Exception as e:
                        print("Copy error:", e)

# ==============================
# Accuracy System
# ==============================

JUDGE_PRESETS = {
    "easy": {
        "marv": 25,
        "perf": 50,
        "great": 100,
        "good": 150,
        "miss": 200
    },
    "normal": {
        "marv": 16,
        "perf": 34,
        "great": 67,
        "good": 100,
        "miss": 150
    },
    "hard": {
        "marv": 10,
        "perf": 20,
        "great": 40,
        "good": 75,
        "miss": 120
    },
    "expert": {
        "marv": 5,
        "perf": 15,
        "great": 30,
        "good": 60,
        "miss": 100
    },
    "custom": {
        "marv": 20,
        "perf": 40,
        "great": 80,
        "good": 120,
        "miss": 180
    }
}

ACTIVE_JUDGE = "normal"

HIT_WINDOWS = JUDGE_PRESETS.get(ACTIVE_JUDGE, JUDGE_PRESETS["normal"])


# ==============================
# SPP SYSTEM
# ==============================

JUDGE_SPP_MULT = {
    "easy": 0.7,
    "normal": 1.0,
    "hard": 1.2,
    "expert": 1.5,
    "custom": 1.0
}


def calculate_spp(score, accuracy, note_count, judge_mode):

    score_factor = score / 1_000_000

    acc_bonus = (accuracy / 100) ** 4

    density = min(note_count / 1000, 2)

    diff_mult = JUDGE_SPP_MULT.get(judge_mode, 1.0)

    spp = 120 * score_factor * acc_bonus * density * diff_mult

    return round(spp, 2)

# ==============================
# pygame engine
# ==============================

pygame.init()

WIDTH=1000
HEIGHT=700

screen=pygame.display.set_mode((WIDTH,HEIGHT))

pygame.display.set_caption("Sonata")

font=pygame.font.SysFont("Monsterrat.ttf",32)

clock=pygame.time.Clock()


def draw(text,x,y):

    surf=font.render(text,True,(107, 33, 255))

    screen.blit(surf,(x,y))

# ==============================
# Game States
# ==============================

STATE_MENU = "menu"
STATE_SONG_SELECT = "song_select"
STATE_GAMEPLAY = "gameplay"

current_state = STATE_MENU
selected_song_index = 0
songs_list = []
current_chart = None
bg_image = None

scroll_offset = 0
max_visible = 10

def load_songs():
    global songs_list

    songs_list = []

    for folder in SONGS_DIR.iterdir():

        if not folder.is_dir():
            continue

        chart_name = folder.name

        for file in folder.glob("*"):

            if file.suffix in [".osu", ".qua", ".sm"]:

                with open(file, "r", encoding="utf8", errors="ignore") as f:

                    for line in f:

                        if line.startswith("Title:"):
                            chart_name = line.split(":", 1)[1].strip()
                            break

                break

        songs_list.append((folder, chart_name))

        songs_list.append((folder, chart_name))

def song_select_loop():
    global selected_song_index, current_state, current_chart, bg_image, scroll_offset

    load_songs()
    scroll_offset = 0

    while current_state == STATE_SONG_SELECT:
        screen.fill((10, 10, 10))

        # ==== DRAW SONGS ====
        for i in range(scroll_offset, min(scroll_offset + max_visible, len(songs_list))):
            folder, name = songs_list[i]
            prefix = "> " if i == selected_song_index else ""
            text = font.render(prefix + name, True, (107,33,255))
            screen.blit(text, (100, 200 + (i - scroll_offset) * 40))

        # ==== HANDLE EVENTS ====
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_state = STATE_MENU
                    return

                if event.key == pygame.K_UP and selected_song_index > 0:
                    selected_song_index -= 1
                    if selected_song_index < scroll_offset:
                        scroll_offset -= 1

                if event.key == pygame.K_DOWN and selected_song_index < len(songs_list) - 1:
                    selected_song_index += 1
                    if selected_song_index >= scroll_offset + max_visible:
                        scroll_offset += 1

                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    selected_folder = songs_list[selected_song_index][0]

                    chart_file = None
                    for file in selected_folder.glob("*"):
                        if file.suffix.lower() in [".osu", ".qua", ".sm"]:
                            chart_file = file
                            break

                    if chart_file:
                        current_chart = load_chart(chart_file)

                    bg_image = None
                    for file in selected_folder.glob("*"):
                        if file.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                            bg_image = pygame.image.load(str(file))
                            bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
                            break

                    pygame.time.delay(200)  # small pause
                    current_state = STATE_GAMEPLAY

        pygame.display.flip()
        clock.tick(60)


def gameplay_loop():
    global current_state

    start_time = pygame.time.get_ticks()

    while current_state == STATE_GAMEPLAY:

        screen.fill((0, 0, 0))

        if bg_image:
            screen.blit(bg_image, (0, 0))

        if current_chart:
            for note in current_chart.notes:
                time, column = note
                y = (pygame.time.get_ticks() - start_time - 3000) * 0.5
                pygame.draw.rect(
                    screen,
                    (107, 33, 255),
                    (column * 80 + 200, y, 60, 20)
                )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_state = STATE_SONG_SELECT

        pygame.display.flip()
        clock.tick(60)

# ==============================
# Main Menu
# ==============================

menu = ["Play", "Import Songs", "Import Skins", "Change Skin", "Quit"]
selected = 0

def menu_loop():
    global selected, current_state

    while current_state == STATE_MENU:

        screen.fill((20, 20, 20))

        for i, item in enumerate(menu):

            prefix = "> " if i == selected else ""
            text = font.render(prefix + item, True, (107, 33, 255))
            screen.blit(text, (100, 200 + i * 50))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(menu)

                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(menu)

                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):

                    if menu[selected] == "Play":
                        current_state = STATE_SONG_SELECT

                    elif menu[selected] == "Import Songs":
                        import_osu_songs()
                        import_quaver_songs()

                    elif menu[selected] == "Quit":
                        pygame.quit()
                        sys.exit()
                    elif menu[selected] == "Import Skins":
                        import_skins()
                    elif menu[selected] == "Change Skin":
                        print("Skin selection UI not built yet")

        pygame.display.flip()
        clock.tick(60)

# ==============================
# Boot
# ==============================

if __name__=="__main__":

    install_ffmpeg()
    import_skins()

    while True:

        if current_state == STATE_MENU:
            menu_loop()

        elif current_state == STATE_SONG_SELECT:
            song_select_loop()

        elif current_state == STATE_GAMEPLAY:
            gameplay_loop()