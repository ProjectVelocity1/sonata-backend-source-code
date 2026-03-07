import os, sys, zipfile, requests, pygame, yaml, shutil, sys
from pathlib import Path

if sys.platform.startswith("win"):
    import tkinter as tk
    subprocess = None
elif sys.platform.startswith("linux"):
    import subprocess
    tk = None
else:
    subprocess = None
    tk = None

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

def ask_folder_path(game_title:str = "that unknown game idk about"):
    dir = None
    titel = "Please choose a folder path for " + game_title
    if tk:
            root = tk.Tk()
            root.withdraw()
            dir = tk.filedialog.askdirectory(
                title=titel
            )
    elif subprocess:
        try:
            dir = subprocess.check_output(
                ["kdialog", "--getexistingdirectory", ".", "--title", titel]
            ).decode().strip()
        except FileNotFoundError:
            try:
                dir = subprocess.check_output(
                    ["flatpak-spawn", "--host", "kdialog", "--getexistingdirectory", ".", "--title", titel]
                ).decode().strip()
            except subprocess.CalledProcessError:
                pass
    return Path(dir)

def detect_song_sources():

    global OSU_DIR, QUAVER_DIR, ETTERNA_DIR

    for p in POSSIBLE_OSU_DIRS:
        if p.exists():
            OSU_DIR = p
            print("Detected osu! Songs:", p)
            break
    if not OSU_DIR:
        OSU_DIR = ask_folder_path('osu!')

    for p in POSSIBLE_QUAVER_DIRS:
        if p.exists():
            QUAVER_DIR = p
            print("Detected Quaver Songs:", p)
            break
    if not QUAVER_DIR:
        QUAVER_DIR = ask_folder_path('Quaver')

    for p in POSSIBLE_ETTERNA_DIRS:
        if p.exists():
            ETTERNA_DIR = p
            print("Detected Etterna Songs:", p)
            break
    if not ETTERNA_DIR:
        ETTERNA_DIR = ask_folder_path('Etterna')


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
# Advanced Skin Importer
# ==============================

CURRENT_SKIN = None
# Default fallback skin
DEFAULT_SKIN_IMAGES = {}

def create_default_skin():
    global DEFAULT_SKIN_IMAGES
    
    note = pygame.Surface((60,20), pygame.SRCALPHA)
    pygame.draw.ellipse(note, (107,33,255), note.get_rect())
    DEFAULT_SKIN_IMAGES["Note"] = note

    receptor = pygame.Surface((60,10), pygame.SRCALPHA)
    pygame.draw.ellipse(receptor, (255,255,255), receptor.get_rect())
    DEFAULT_SKIN_IMAGES["Receptor"] = receptor

    hold = pygame.Surface((60,20), pygame.SRCALPHA)
    pygame.draw.rect(hold,(160,80,255), hold.get_rect())
    DEFAULT_SKIN_IMAGES["Hold"] = hold

create_default_skin()

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

    print("Scan complete.")
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
# Song Select
# ==============================
diff_list = []
selected_diff = 0

def select_loop():

    global current_state, selected_song, current_chart

    load_songs()

    while current_state == STATE_SELECT:

        screen.fill((10,10,10))

        for i,(folder,name) in enumerate(songs_list):

            prefix="> " if i==selected_song else ""
            text=font.render(prefix+name,True,(107,33,255))

            screen.blit(text,(100,200+i*40))

        for event in pygame.event.get():

            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type==pygame.KEYDOWN:

                if event.key==pygame.K_ESCAPE:
                    current_state=STATE_MENU
                    return

                if event.key==pygame.K_UP and selected_song>0:
                    selected_song-=1

                if event.key==pygame.K_DOWN and selected_song<len(songs_list)-1:
                    selected_song+=1

                if event.key==pygame.K_RETURN or event.key == pygame.K_KP_ENTER:

                    folder=songs_list[selected_song][0]
                    diff_list.clear()

                    for file in folder.glob("*"):
                        if file.suffix.lower() in [".osu",".qua",".sm"]:
                            diff_list.append(file)

                        if diff_list:
                            selected_diff = 0
                            current_state = STATE_DIFF_SELECT
                            current_chart=load_chart(file)
                            break

                    current_state=STATE_GAME

        pygame.display.flip()
        clock.tick(60)

def diff_select_loop():

    global current_state, selected_diff, current_chart

    folder=songs_list[selected_song][0]

    while current_state==STATE_DIFF_SELECT:

        screen.fill((20,20,20))

        for i,file in enumerate(diff_list):

            name=file.stem
            prefix="> " if i==selected_diff else ""

            text=font.render(prefix+name,True,(107,33,255))
            screen.blit(text,(120,200+i*40))

        for event in pygame.event.get():

            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type==pygame.KEYDOWN:

                if event.key==pygame.K_ESCAPE:
                    current_state=STATE_SELECT
                    return

                if event.key==pygame.K_UP and selected_diff>0:
                    selected_diff-=1

                if event.key==pygame.K_DOWN and selected_diff<len(diff_list)-1:
                    selected_diff+=1

                if event.key==pygame.K_RETURN or event.key == pygame.K_KP_ENTER:

                    chart_file=diff_list[selected_diff]
                    current_chart=load_chart(chart_file)
                    current_state=STATE_GAME

        pygame.display.flip()
        clock.tick(60)

# ==============================
# Gameplay
# ==============================

def game_loop():

    global score, combo, max_combo
    global marv, perf, great, good, miss

    score = 0
    combo = 0
    max_combo = 0

    marv = 0
    perf = 0
    great = 0
    good = 0
    miss = 0

    global current_state

    chart=current_chart

    folder=songs_list[selected_song][0]

    audio=None

    for f in folder.iterdir():
        if f.name==chart.audio:
            audio=f

    if audio:
        pygame.mixer.music.load(audio)
        pygame.mixer.music.play()

    bg=None

    if chart.bg:
        bg_path=folder/chart.bg
        if bg_path.exists():
            bg=pygame.image.load(bg_path)
            bg=pygame.transform.scale(bg,(WIDTH,HEIGHT))

    start=pygame.time.get_ticks()

    keys=[pygame.K_d,pygame.K_f,pygame.K_j,pygame.K_k]

    hit_windows={
        "MARV":22,
        "PERFECT":45,
        "GREAT":90,
        "GOOD":135
    }

    judgement=""
    hit_notes=set()

    while current_state==STATE_GAME:

        if bg:
            screen.blit(bg,(0,0))
        else:
            screen.fill((0,0,0))

        current_time=pygame.time.get_ticks()-start

        for i in range(chart.keys):

            pygame.draw.rect(
                screen,
                (200,200,200),
                (200+i*80,HEIGHT-120,60,10)
            )

        scroll_speed=0.6

        for i,(time,col) in enumerate(chart.notes):

            if i in hit_notes:
                continue

            y=HEIGHT-120-(time-current_time)*scroll_speed

            if y>HEIGHT:
                continue

            pygame.draw.rect(
                screen,
                (107,33,255),
                (200+col*80,y,60,20)
            )

            if current_time-time>150:
                judgement="MISS"
                hit_notes.add(i)
                combo=0
                miss+=1

        for start_ln,end_ln,col in chart.lns:

            y1=HEIGHT-120-(start_ln-current_time)*scroll_speed
            y2=HEIGHT-120-(end_ln-current_time)*scroll_speed

            pygame.draw.rect(
                screen,
                (160,80,255),
                (200+col*80,y1,60,y2-y1)
            )

        if judgement:

            text=font.render(judgement,True,(255,255,255))
            screen.blit(text,(WIDTH//2-60,HEIGHT//2))

        for event in pygame.event.get():

            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type==pygame.KEYDOWN:

                if event.key==pygame.K_ESCAPE:

                    pygame.mixer.music.stop()
                    current_state=STATE_SELECT
                    return

                for col,key in enumerate(keys):

                    if event.key==key:

                        for i,(time,ncol) in enumerate(chart.notes):

                            if ncol!=col or i in hit_notes:
                                continue

                            diff=abs(current_time-time)

                            for j,w in hit_windows.items():

                                if diff<=w:

                                    judgement=j
                                    hit_notes.add(i)

                                    if j == "MARV":
                                        score+=1000
                                        marv+=1
                                        combo+=1

                                    elif j == "PERFECT":
                                        score+=800
                                        perf+=1
                                        combo+=1

                                    elif j == "GREAT":
                                        score+=500
                                        great+=1
                                        combo+=1

                                    elif j == "GOOD":
                                        score +=200
                                        great+=1
                                        combo+=1
                                    max_combo=max(max_combo,combo)
                                    break

                            break

        pygame.display.flip()
        clock.tick(120)
score = 0
combo = 0
max_combo = 0
marv = 0
perf = 0
great = 0
good = 0
miss = 0

total_hits = marv+perf+great+good+miss

if total_hits>0:
    accuracy = (
        (marv*1.0 + perf*0.9 + great*0.7 + good*0.4)
        / total_hits
    )*100
else:
    accuracy=100

rank="F"

if accuracy>=99:
    rank="SS"
elif accuracy>=96:
    rank="S"
elif accuracy>=90:
    rank="A"
elif accuracy>=80:
    rank="B"
elif accuracy>=70:
    rank="C"
elif accuracy>=60:
    rank="D"

score_text=font.render(f"Score: {score}",True,(255,255,255))
combo_text=font.render(f"Combo: {combo}",True,(255,255,255))
acc_text=font.render(f"Acc: {accuracy:.2f}%",True,(255,255,255))
rank_text=font.render(f"Rank: {rank}",True,(255,255,0))

screen.blit(score_text,(20,20))
screen.blit(combo_text,(20,60))
screen.blit(acc_text,(20,100))
screen.blit(rank_text,(20,140))

# ==============================
# Boot
# ==============================

if __name__=="__main__":

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
