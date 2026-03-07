import os
import sys
import zipfile
import requests
import pygame
import yaml
from pathlib import Path
import shutil
from pypresence import Presence
import time

# ==============================
# Discord RPC
# ==============================

CLIENT_ID = "1479950020294869012"

RPC = None

def start_rpc():
    global RPC
    try:
        RPC = Presence(CLIENT_ID)
        RPC.connect()
        print("Discord RPC connected")
    except Exception as e:
        print("RPC failed:", e)

def update_rpc(state="Menu", details="Idle", large_text="sonata_logo"):
    if RPC is None:
        return

    try:
        RPC.update(
            state=state,
            details=details,
            large_image="sonata",
            large_text=large_text,
            start=time.time()
        )
    except:
        pass

def update_rpc_gameplay(chart, elapsed, end_time):

    if RPC is None:
        return

    try:

        progress = int((elapsed / end_time) * 100)
        progress = max(0, min(100, progress))

        RPC.update(
            state="Playing Sonata",
            details=f"{chart.artist} - {chart.title}",
            large_image="sonata",
            large_text="Sonata Rhythm Game",

            small_image="play",
            small_text=f"{chart.keys}K • {timewarp:.2f}x rate • {progress}% progress",

            start=time.time() - (elapsed / 1000)
        )

    except:
        pass

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

# ==============================
# POSSIBLE GAME DIRS
# ==============================

POSSIBLE_OSU_DIRS = [
    HOME / "AppData" / "Local" / "osu!" / "Songs",
    HOME / "AppData" / "Roaming" / "osu!" / "Songs"
]

POSSIBLE_QUAVER_DIRS = [
    Path("C:/Program Files (x86)/Steam/steamapps/common/Quaver/Songs"),
    Path("C:/Program Files/Steam/steamapps/common/Quaver/Songs")
]

POSSIBLE_ETTERNA_DIRS = [
    HOME / "AppData" / "Roaming" / "Etterna" / "Songs",
    Path("C:/Games/Etterna/Songs"),
    Path("C:/Program Files/Etterna/Songs")
]

OSU_DIR = None
QUAVER_DIR = None
ETTERNA_DIR = None

# ==============================
# Song Source Detection
# ==============================

def detect_song_sources():

    global OSU_DIR, QUAVER_DIR, ETTERNA_DIR

    for p in POSSIBLE_OSU_DIRS:
        if p.exists():
            OSU_DIR = p
            print("Detected osu! Songs:", p)
            break

    for p in POSSIBLE_QUAVER_DIRS:
        if p.exists():
            QUAVER_DIR = p
            print("Detected Quaver Songs:", p)
            break

    for p in POSSIBLE_ETTERNA_DIRS:
        if p.exists():
            ETTERNA_DIR = p
            print("Detected Etterna Songs:", p)
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

        dest = SKINS_DIR / folder.name
        dest.mkdir(exist_ok=True)

        for item in folder.iterdir():
            if item.is_file():
                shutil.copy(item, dest / item.name)

# ==============================
# Advanced Skin Importer (Default Circle Skin)
# ==============================

CURRENT_SKIN = None
DEFAULT_SKIN_IMAGES = {}
SKIN_IMAGES = DEFAULT_SKIN_IMAGES.copy()

def create_default_skin():
    global DEFAULT_SKIN_IMAGES
    
    # ---------------- CIRCULAR NOTE ----------------
    note = pygame.Surface((60,60), pygame.SRCALPHA)
    pygame.draw.circle(note, (107,33,255), (30,30), 28)
    DEFAULT_SKIN_IMAGES["Note"] = note

    # ---------------- CIRCULAR RECEPTOR ----------------
    receptor = pygame.Surface((60,60), pygame.SRCALPHA)
    pygame.draw.circle(receptor, (255,255,255), (30,30), 28, 4)
    DEFAULT_SKIN_IMAGES["Receptor"] = receptor

    # ---------------- HOLD NOTE ----------------
    hold = pygame.Surface((60,20), pygame.SRCALPHA)
    pygame.draw.rect(hold,(160,80,255), hold.get_rect(), border_radius=8)
    DEFAULT_SKIN_IMAGES["Hold"] = hold

create_default_skin()

# ---------------- fallback SKIN_IMAGES so it’s always defined
SKIN_IMAGES = DEFAULT_SKIN_IMAGES.copy()

def import_all_skins():

    print("\nImporting skins...")

    skins_dest = SKINS_DIR
    skins_dest.mkdir(exist_ok=True)

    HOME = Path.home()

    sources = [

        HOME / "AppData" / "Local" / "osu!" / "Skins",

        Path("C:/Program Files (x86)/Steam/steamapps/content/980610"),

        HOME / "AppData" / "Roaming" / "Etterna" / "NoteSkins" / "dance"
    ]

    for source in sources:

        if not source.exists():
            continue

        for folder in source.iterdir():

            if not folder.is_dir():
                continue

            dest = skins_dest / folder.name

            if dest.exists():
                continue

            try:
                shutil.copytree(folder, dest)
                print("Imported skin:", folder.name)
            except:
                pass

    print("Skin import finished.\n")

    # ---------------- OSU SKINS ----------------
    osu_skins = HOME / "AppData" / "Local" / "osu!" / "Skins"

    if osu_skins.exists():

        print("Copying osu skins...")

        for skin in osu_skins.iterdir():

            if not skin.is_dir():
                continue

            dest = skins_dest / ("osu_" + skin.name)

            if dest.exists():
                continue

            try:
                shutil.copytree(skin, dest)
                print("Imported osu skin:", skin.name)
            except Exception as e:
                print("Skin copy error:", e)

    # ---------------- QUAVER SKINS ----------------
    quaver_skins = Path("C:/Program Files (x86)/Steam/steamapps/workshop/content/980610")

    if quaver_skins.exists():

        print("Copying Quaver workshop skins...")

        for skin_folder in quaver_skins.iterdir():

            if not skin_folder.is_dir():
                continue

            dest = skins_dest / ("quaver_" + skin_folder.name)

            if dest.exists():
                continue

            try:
                shutil.copytree(skin_folder, dest)
                print("Imported quaver skin:", skin_folder.name)
            except Exception as e:
                print("Quaver skin error:", e)

    # ---------------- ETTERNA SKINS ----------------
    etterna_skins = HOME / "AppData" / "Roaming" / "Etterna" / "NoteSkins" / "dance"

    if etterna_skins.exists():

        print("Copying Etterna skins...")

        for skin in etterna_skins.iterdir():

            if not skin.is_dir():
                continue

            dest = skins_dest / ("etterna_" + skin.name)

            if dest.exists():
                continue

            try:
                shutil.copytree(skin, dest)
                print("Imported etterna skin:", skin.name)
            except Exception as e:
                print("Etterna skin error:", e)

    print("Skin import finished.\n")

# ==============================
# Skin Loader
# ==============================

def load_skin(skin_folder):

    global CURRENT_SKIN, SKIN_IMAGES

    CURRENT_SKIN = skin_folder
    SKIN_IMAGES = {}

    ini_file = skin_folder / "skin.ini"

    if not ini_file.exists():
        return

    print("Loading skin:", skin_folder.name)

    with open(ini_file, "r", encoding="utf8", errors="ignore") as f:
        lines = f.readlines()

    # Parse image references
    for line in lines:

        if "=" not in line:
            continue

        key, value = line.split("=",1)

        key = key.strip()
        value = value.strip()

        image_path = skin_folder / value

        if image_path.exists() and image_path.suffix.lower() in [".png",".jpg",".jpeg"]:

            try:
                img = pygame.image.load(str(image_path)).convert_alpha()
                SKIN_IMAGES[key] = img
                print("Loaded:", key)
            except:
                pass

# ==============================
# FFmpeg Auto Installer
# ==============================

FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"


def install_ffmpeg():

    if (FFMPEG_DIR / "ffmpeg.exe").exists():
        return

    print("Downloading FFmpeg...")

    zip_path = ENGINE_DIR / "ffmpeg.zip"

    r = requests.get(FFMPEG_URL, stream=True)

    with open(zip_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    print("Extracting FFmpeg...")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(ENGINE_DIR)

    for root, dirs, files in os.walk(ENGINE_DIR):
        for file in files:
            if file == "ffmpeg.exe":
                src = Path(root) / file
                FFMPEG_DIR.mkdir(exist_ok=True)
                shutil.move(src, FFMPEG_DIR / "ffmpeg.exe")

    print("FFmpeg installed")

def load_audio_with_timewarp(audio_path, timewarp):
    """
    Returns a pygame.mixer.Sound object that is resampled
    according to timewarp. Uses FFmpeg to process the file.
    """
    import subprocess
    import tempfile

    # output temp file
    tmp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp_path = tmp_file.name
    tmp_file.close()

    # FFmpeg command to change speed/pitch
    # atempo only supports 0.5x - 2.0x, so clamp
    tw = max(0.5, min(timewarp, 2.0))

    cmd = [
        str(FFMPEG_DIR / "ffmpeg.exe"),
        "-y",
        "-i", str(audio_path),
        "-filter:a", f"atempo={tw}",
        "-vn",
        tmp_path
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return pygame.mixer.Sound(tmp_path)

# ==============================
# Chart Structure
# ==============================

class Chart:

    def __init__(self):

        self.notes = []      
        self.lns = []        
        self.audio = None
        self.bg = None

        self.keys = 4

        self.title = "Unknown"
        self.artist = "Unknown"
        self.diff = "Normal"

# ==============================
# OSU Parser
# ==============================

def parse_osu(path):

    chart = Chart()
    mode = None

    with open(path,"r",encoding="utf8",errors="ignore") as f:

        for line in f:

            if line.startswith("Mode:"):
                mode=int(line.split(":")[1])

            if line.startswith("CircleSize:"):
                chart.keys=int(float(line.split(":")[1]))

            if line.startswith("Title:"):
                chart.title=line.split(":",1)[1].strip()

            if line.startswith("Artist:"):
                chart.artist=line.split(":",1)[1].strip()

            if line.startswith("Version:"):
                chart.diff=line.split(":",1)[1].strip()

            if line.startswith("AudioFilename"):
                chart.audio=line.split(":")[1].strip()

            if line.startswith("0,0,\""):
                chart.bg=line.split(",")[2].replace("\"","")

            if line.count(",")>=4 and mode==3:

                parts=line.split(",")

                x=int(parts[0])
                time=int(parts[2])
                obj=int(parts[3])

                column=int(x/(512/chart.keys))

                if obj & 128:

                    end=int(parts[5].split(":")[0])
                    chart.lns.append((time,end,column))

                else:
                    chart.notes.append((time,column))

    return chart
# ==============================
# Quaver Parser
# ==============================

def parse_qua(path):

    chart=Chart()

    with open(path,"r",encoding="utf8") as f:
        data=yaml.safe_load(f)

    chart.title=data.get("Title","Unknown")
    chart.artist=data.get("Artist","Unknown")
    chart.audio=data.get("AudioFile")
    chart.bg=data.get("BackgroundFile")
    chart.diff=data.get("DifficultyName","Normal")

    mode=data.get("Mode","Keys4")

    if "4" in mode:
        chart.keys=4
    elif "7" in mode:
        chart.keys=7

    for note in data.get("HitObjects",[]):

        start=note["StartTime"]
        lane=note["Lane"]

        if "EndTime" in note:
            chart.lns.append((start,note["EndTime"],lane-1))
        else:
            chart.notes.append((start,lane-1))

    return chart

# ==============================
# Stepmania Parser
# ==============================

def parse_sm(path):

    chart=Chart()

    with open(path,"r",encoding="utf8",errors="ignore") as f:
        lines=f.readlines()

    for line in lines:

        if line.startswith("#TITLE:"):
            chart.title=line.replace("#TITLE:","").replace(";","")

        if line.startswith("#ARTIST:"):
            chart.artist=line.replace("#ARTIST:","").replace(";","")

        if line.startswith("#MUSIC:"):
            chart.audio=line.replace("#MUSIC:","").replace(";","")

        if line.startswith("#BACKGROUND:"):
            chart.bg=line.replace("#BACKGROUND:","").replace(";","")

    time=0
    ln_start=[None]*4

    for line in lines:

        line=line.strip()

        if len(line)==4:

            for i,c in enumerate(line):

                if c=="1":
                    chart.notes.append((time,i))

                if c=="2":
                    ln_start[i]=time

                if c=="3" and ln_start[i] is not None:

                    chart.lns.append((ln_start[i],time,i))
                    ln_start[i]=None

            time+=120

    return chart

# ==============================
# Chart Loader
# ==============================

def load_chart(path):

    ext = path.suffix.lower()

    if ext == ".osu":
        return parse_osu(path)

    if ext == ".qua":
        return parse_qua(path)

    if ext == ".sm":
        return parse_sm(path)

# ==============================
# Mania Detection
# ==============================

def is_osu_mania(file):

    try:
        with open(file, "r", encoding="utf8", errors="ignore") as f:
            return "Mode: 3" in f.read()
    except:
        return False

# ==============================
# Copy Helper
# ==============================

def copy_song(src_folder):

    dest = SONGS_DIR / src_folder.name

    if dest.exists():
        return False

    try:
        shutil.copytree(src_folder, dest)
        return True
    except:
        return False

# ==============================
# Universal Scanner
# ==============================

def scan_all_games():

    detect_song_sources()

    imported = 0

    if OSU_DIR:

        print("\nScanning osu!mania...")

        for folder in OSU_DIR.iterdir():

            if not folder.is_dir():
                continue

            mania_found = False

            for file in folder.glob("*.osu"):
                if is_osu_mania(file):
                    mania_found = True
                    break

            if mania_found:

                if copy_song(folder):
                    imported += 1
                    print("Imported:", folder.name)

    if QUAVER_DIR:

        print("\nScanning Quaver...")

        for folder in QUAVER_DIR.iterdir():

            if not folder.is_dir():
                continue

            for file in folder.glob("*.qua"):

                if copy_song(folder):
                    imported += 1
                    print("Imported:", folder.name)

                break

    if ETTERNA_DIR:

        print("\nScanning Etterna...")

        for pack in ETTERNA_DIR.iterdir():

            if not pack.is_dir():
                continue

            for song in pack.iterdir():

                if not song.is_dir():
                    continue

                for file in song.glob("*.sm"):

                    if copy_song(song):
                        imported += 1
                        print("Imported:", song.name)

                    break

    print("\nScan complete.")
    print("Total imported:", imported)

# ==============================
# Pygame Engine
# ==============================
pygame.mixer.init()
pygame.init()

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sonata")

font = pygame.font.SysFont("Arial", 32)

clock = pygame.time.Clock()

# ==============================
# States
# ==============================

STATE_MENU = "menu"
STATE_SELECT = "select"
STATE_GAME = "game"
STATE_SETTINGS = "settings"
STATE_DIFF_SELECT = "diff_select"
STATE_RESULTS = "results"

current_state = STATE_MENU

songs_list = []
selected_song = 0
current_chart = None

STATE_SETTINGS = "settings"
STATE_DIFF_SELECT = "diff_select"

settings = {
    "scroll_speed":0.6,
    "offset":0,
    "hitsound":True
}

settings_menu = ["Scroll Speed","Offset","Hitsound","Back"]
settings_index = 0

# ==============================
# Song Loader
# ==============================

def load_songs():

    global songs_list
    songs_list = []

    for folder in SONGS_DIR.iterdir():

        if not folder.is_dir():
            continue

        name = folder.name

        for file in folder.glob("*.osu"):
            with open(file,"r",encoding="utf8",errors="ignore") as f:
                for line in f:
                    if line.startswith("Title:"):
                        name = line.split(":",1)[1].strip()
                        break
            break

        songs_list.append((folder,name))

# ==============================
# Menu
# ==============================

menu = ["Play","Import Songs","Import Skins","Settings","Quit"]
menu_index = 0

def menu_loop():

    global menu_index, current_state

    # ---- RPC UPDATE WHEN MENU OPENS ----
    update_rpc("Menu", "Browsing menu")

    while current_state == STATE_MENU:

        screen.fill((20,20,20))

        for i,item in enumerate(menu):

            prefix = "> " if i == menu_index else ""
            text = font.render(prefix + item,True,(107,33,255))

            screen.blit(text,(100,200+i*50))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:
                    menu_index = (menu_index-1)%len(menu)

                if event.key == pygame.K_DOWN:
                    menu_index = (menu_index+1)%len(menu)

                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:

                    if menu[menu_index] == "Play":
                        current_state = STATE_SELECT

                    elif menu[menu_index] == "Import Songs":
                        scan_all_games()

                    elif menu[menu_index] == "Import Skins":
                        import_skins()

                    elif menu[menu_index] == "Settings":
                        current_state = STATE_SETTINGS

                    elif menu[menu_index] == "Quit":
                        pygame.quit()
                        sys.exit()

        pygame.display.flip()
        clock.tick(60)

def settings_loop():

    global settings_index, current_state

    while current_state == STATE_SETTINGS:

        screen.fill((15,15,15))

        for i,item in enumerate(settings_menu):

            prefix="> " if i==settings_index else ""

            value=""

            if item=="Scroll Speed":
                value=f": {settings['scroll_speed']}"

            if item=="Offset":
                value=f": {settings['offset']}"

            if item=="Hitsound":
                value=f": {'ON' if settings['hitsound'] else 'OFF'}"

            text=font.render(prefix+item+value,True,(107,33,255))
            screen.blit(text,(100,200+i*50))

        for event in pygame.event.get():

            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type==pygame.KEYDOWN:

                if event.key==pygame.K_ESCAPE:
                    current_state=STATE_MENU
                    return

                if event.key==pygame.K_UP:
                    settings_index=(settings_index-1)%len(settings_menu)

                if event.key==pygame.K_DOWN:
                    settings_index=(settings_index+1)%len(settings_menu)

                if event.key==pygame.K_LEFT:

                    if settings_menu[settings_index]=="Scroll Speed":
                        settings["scroll_speed"]=max(0.2,settings["scroll_speed"]-0.1)

                    if settings_menu[settings_index]=="Offset":
                        settings["offset"]-=5

                if event.key==pygame.K_RIGHT:

                    if settings_menu[settings_index]=="Scroll Speed":
                        settings["scroll_speed"]+=0.1

                    if settings_menu[settings_index]=="Offset":
                        settings["offset"]+=5

                if event.key==pygame.K_RETURN or event.key == pygame.K_KP_ENTER:

                    if settings_menu[settings_index]=="Hitsound":
                        settings["hitsound"]=not settings["hitsound"]

                    if settings_menu[settings_index]=="Back":
                        current_state=STATE_MENU
                        return

        pygame.display.flip()
        clock.tick(60)

# ==============================
# Song Select + Timewarp + Diff Select (Fixed Boot)
# ==============================

update_rpc("Song Select", "Choosing a song")
timewarp = 1.0  # default
selected_song = 0
selected_diff = 0
current_chart = None
songs_list = []
diff_list = []

def select_loop():
    global current_state, selected_song, current_chart, timewarp

    load_songs()

    while current_state == STATE_SELECT:
        screen.fill((10,10,10))

        # ---- SCROLL LOGIC ----
        page_size = 10
        start_index = max(0, selected_song - page_size//2)
        end_index = min(len(songs_list), start_index + page_size)
        if end_index - start_index < page_size:
            start_index = max(0, end_index - page_size)

        for i in range(start_index, end_index):
            folder, name = songs_list[i]
            prefix = "> " if i == selected_song else ""
            text = font.render(prefix + name, True, (107,33,255))
            screen.blit(text, (100, 200 + (i-start_index)*40))

        # ---- TIMEWARP DISPLAY ----
        tw_text = font.render(f"Timewarp: {timewarp:.2f}x", True, (255,255,255))
        screen.blit(tw_text, (600, 200))

        # ---- INPUT ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_state = STATE_MENU
                    return

                if event.key == pygame.K_UP and selected_song > 0:
                    selected_song -= 1

                if event.key == pygame.K_DOWN and selected_song < len(songs_list)-1:
                    selected_song += 1

                # LEFT/RIGHT arrows change timewarp
                if event.key == pygame.K_LEFT:
                    timewarp = max(0.5, timewarp - 0.05)
                if event.key == pygame.K_RIGHT:
                    timewarp = min(2.0, timewarp + 0.05)

                if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                    folder = songs_list[selected_song][0]
                    diff_list.clear()
                    for file in folder.glob("*"):
                        if file.suffix.lower() in [".osu",".qua",".sm"]:
                            diff_list.append(file)
                    if diff_list:
                        selected_diff = 0
                        current_chart = load_chart(diff_list[selected_diff])
                        current_state = STATE_DIFF_SELECT

        pygame.display.flip()
        clock.tick(60)

def diff_select_loop():
    global current_state, selected_diff, current_chart

    folder = songs_list[selected_song][0]

    while current_state == STATE_DIFF_SELECT:
        screen.fill((20,20,20))

        # show diff list
        for i, file in enumerate(diff_list):
            prefix = "> " if i == selected_diff else ""
            text = font.render(prefix + file.stem, True, (107,33,255))
            screen.blit(text, (120, 200 + i*40))

        # show timewarp too
        tw_text = font.render(f"Timewarp: {timewarp:.2f}x", True, (255,255,0))
        screen.blit(tw_text, (120, 150))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_state = STATE_SELECT
                    return
                if event.key == pygame.K_UP:
                    selected_diff = max(0, selected_diff - 1)
                if event.key == pygame.K_DOWN:
                    selected_diff = min(len(diff_list) - 1, selected_diff + 1)
                if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                    current_chart = load_chart(diff_list[selected_diff])
                    if current_chart is None:
                        print("Error: chart failed to load!")
                        current_state = STATE_SELECT
                        return
                    current_state = STATE_GAME

        pygame.display.flip()
        clock.tick(60)
       
# ==============================
# SPP Calculation 
# ==============================

def calculate_spp(score, accuracy, note_count, timewarp=1.0):

    score_factor = score / 1_000_000            # normalized score
    acc_bonus = (accuracy / 100) ** 4          # accuracy power curve
    density = min(note_count / 1000, 2)        # note density factor

    # timewarp multiplier
    # easier if <1.0, harder if >1.0, clamped 0.5x - 2x
    tw_mult = max(0.5, min(timewarp, 2.0))

    # SPP formula
    spp = 120 * score_factor * acc_bonus * density * tw_mult

    return round(spp, 2)

# ==============================
# Gameplay (Circle Skin + Countdown + Timewarp)
# ==============================
import numpy as np
import pygame.sndarray

def load_audio_with_timewarp(file_path, timewarp):
    """Load audio as pygame.Sound and apply timewarp correctly."""
    sound = pygame.mixer.Sound(str(file_path))
    arr = pygame.sndarray.array(sound).astype(np.float32)

    # Resample array to match the timewarp correctly
    indices = np.arange(0, len(arr), timewarp)
    indices = indices[indices < len(arr)].astype(np.int32)
    warped_arr = arr[indices]

    warped_sound = pygame.sndarray.make_sound(warped_arr.astype(np.int16))
    return warped_sound

def game_loop():
    global score, combo, max_combo
    global marv, perf, great, good, miss
    global current_state

    score = combo = max_combo = 0
    marv = perf = great = good = miss = 0

    chart = current_chart

    # ---- DISCORD RPC UPDATE ----
    try:
        update_rpc(
            "Playing",
            f"{chart.artist} - {chart.title} [{chart.diff}] | {chart.keys}K {timewarp:.2f}x"
        )
    except:
        pass

    folder = songs_list[selected_song][0]

    # load audio
    audio_file = None
    for f in folder.iterdir():
        if f.name == chart.audio:
            audio_file = f
            break

    # load background
    bg = None
    if chart.bg:
        bg_path = folder / chart.bg
        if bg_path.exists():
            bg = pygame.image.load(bg_path)
            bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

    keys = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
    hit_windows = {"MARV":22,"PERFECT":45,"GREAT":90,"GOOD":135}
    judgement = ""
    hit_notes = set()

    scroll_speed = settings["scroll_speed"]

    # ------------------ 3-second countdown ------------------
    countdown_start = pygame.time.get_ticks()
    countdown_done = False
    start_time = None
    audio_playing = None

    while current_state == STATE_GAME:
        screen.fill((0,0,0))
        if bg:
            screen.blit(bg, (0,0))

        current_time = pygame.time.get_ticks() - countdown_start

        # show countdown
        if not countdown_done:
            remaining = 3 - current_time // 1000
            if remaining > 0:
                text = font.render(f"{remaining}", True, (255,255,255))
                screen.blit(text, (WIDTH//2-20, HEIGHT//2-20))
                pygame.display.flip()
                clock.tick(60)
                continue
            else:
                countdown_done = True
                # start music with correct timewarp
                if audio_file:
                    try:
                        audio_playing = load_audio_with_timewarp(audio_file, timewarp)
                        audio_playing.play()
                    except Exception as e:
                        print("Audio failed to load with timewarp:", e)
                start_time = pygame.time.get_ticks()
                continue

        # elapsed time for notes (map)
        elapsed = (pygame.time.get_ticks() - start_time) * timewarp

        # detect end of map
        last_note = max([t for t,_ in chart.notes], default=0)
        last_ln = max([e for _,e,_ in chart.lns], default=0)
        end_time = max(last_note, last_ln)
        update_rpc_gameplay(chart, elapsed, end_time)
        if elapsed > end_time + 3000:
            if audio_playing:
                audio_playing.stop()
            current_state = STATE_RESULTS
            return

        # draw receptors
        for i in range(chart.keys):
            receptor_img = SKIN_IMAGES.get("Receptor", DEFAULT_SKIN_IMAGES["Receptor"])
            screen.blit(receptor_img, (200+i*80, HEIGHT-120))

        # draw notes
        for i,(time,col) in enumerate(chart.notes):
            if i in hit_notes:
                continue
            y = HEIGHT-120-(time-elapsed)*scroll_speed
            if y > HEIGHT:
                continue
            note_img = SKIN_IMAGES.get("Note", DEFAULT_SKIN_IMAGES["Note"])
            screen.blit(note_img, (200+col*80, y))

            if elapsed - time > 150:
                judgement = "MISS"
                hit_notes.add(i)
                combo = 0
                miss += 1

        # draw hold notes
        for start_ln,end_ln,col in chart.lns:
            y1 = HEIGHT-120-(start_ln-elapsed)*scroll_speed
            y2 = HEIGHT-120-(end_ln-elapsed)*scroll_speed
            hold_img = SKIN_IMAGES.get("Hold", DEFAULT_SKIN_IMAGES["Hold"])
            hold_scaled = pygame.transform.scale(hold_img, (60, max(1, int(y2-y1))))
            screen.blit(hold_scaled, (200+col*80, y1))

        # show judgement text
        if judgement:
            text = font.render(judgement, True, (255,255,255))
            screen.blit(text, (WIDTH//2-60, HEIGHT//2))

        # input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if audio_playing:
                    audio_playing.stop()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if audio_playing:
                        audio_playing.stop()
                    current_state = STATE_SELECT
                    return

                for col,key in enumerate(keys):
                    if event.key == key:
                        for i,(time,ncol) in enumerate(chart.notes):
                            if ncol != col or i in hit_notes:
                                continue
                            diff = abs(elapsed - time)
                            for j,w in hit_windows.items():
                                if diff <= w:
                                    judgement = j
                                    hit_notes.add(i)
                                    if j == "MARV":
                                        score += 1000; marv += 1; combo += 1
                                    elif j == "PERFECT":
                                        score += 800; perf += 1; combo += 1
                                    elif j == "GREAT":
                                        score += 500; great += 1; combo += 1
                                    elif j == "GOOD":
                                        score += 200; good += 1; combo += 1
                                    max_combo = max(max_combo, combo)
                                    break
                            break

        pygame.display.flip()
        clock.tick(120)

# ==============================
# Results Loop
# ==============================
def results_loop():
    global current_state

    total_hits = marv + perf + great + good + miss
    if total_hits > 0:
        accuracy = ((marv*1.0 + perf*0.9 + great*0.7 + good*0.4)/total_hits)*100
    else:
        accuracy = 100

    note_count = len(current_chart.notes) + len(current_chart.lns)
    spp = calculate_spp(score, accuracy, note_count, timewarp)
    update_rpc(
        "Results",
        f"{current_chart.artist} - {current_chart.title} | Score {score}"
    )

    while current_state == STATE_RESULTS:
        screen.fill((10,10,10))

        lines = [
            f"Score: {score}",
            f"Accuracy: {accuracy:.2f}%",
            f"SPP: {spp}",
            f"Timewarp: {timewarp:.2f}x",
            "",
            f"Marvelous: {marv}",
            f"Perfect: {perf}",
            f"Great: {great}",
            f"Good: {good}",
            f"Miss: {miss}",
            "",
            "Press ENTER to continue"
        ]

        for i, line in enumerate(lines):
            text = font.render(line, True, (255,255,255))
            screen.blit(text, (WIDTH//2-200, 200 + i*40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                    current_state = STATE_SELECT
                    return

        pygame.display.flip()
        clock.tick(60)

# ==============================
# Boot
# ==============================

if __name__=="__main__":

    start_rpc()

    install_ffmpeg()
    import_skins()
    if SKINS_DIR.exists():
        skins = list(SKINS_DIR.iterdir())
        if skins:
            load_skin(skins[0])

    while True:

        if current_state==STATE_MENU:
            menu_loop()

        if current_state==STATE_SELECT:
            select_loop()

        if current_state==STATE_GAME:
            game_loop()

        if current_state==STATE_SETTINGS:
            settings_loop()

        if current_state==STATE_DIFF_SELECT:
            diff_select_loop()

        if current_state==STATE_RESULTS:
            results_loop()
