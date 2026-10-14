import math
import sys
import os
import io
import struct
import wave
import random
import pygame

# ==============================================================================
# SILENT GLITCH: HAUNTED CASTLE EDITION (PSYCHOLOGICAL HORROR OVERHAUL)
# - 8 Deeply Haunted Rooms with rotting peeling walls, mould, and creaky floorboards
# - Final 25-Second Ghost Chase AI with accelerating dynamic heartbeat audio
# - Level 2 Sudden Blackout & Eternal Flame Lantern with illuminated routes
# - Level 3 Dual-Dimension Phasing Stalker (Invisible in Real, Revealed in Glitch)
# - "Silent Glitch" effect: Sensory-deprived dead silence, tinnitus hum & analog tear
# - Graphical Gothic Arched Castle Double Doors with interactive [E] controls
# ==============================================================================

pygame.init()
pygame.font.init()
pygame.mixer.init(22050, -16, 1, 512)

WIDTH, HEIGHT = 960, 600
HALF_W = WIDTH // 2
HALF_H = HEIGHT // 2
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SILENT GLITCH | Old Haunted Castle")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("consolas", 20)
SMALL = pygame.font.SysFont("consolas", 14)
BIG = pygame.font.SysFont("consolas", 38, bold=True)
TITLE_FONT = pygame.font.SysFont("georgia", 28, bold=True)

FOV = math.radians(66)
NUM_RAYS = 320
MAX_DEPTH = 20.0
RAY_STEP = 0.025
PLAYER_RADIUS = 0.22
MOVE_SPEED = 2.6
TURN_SPEED = 2.2

# ------------------------------------------------------------------------------
# PROCEDURAL HORROR AUDIO SYNTHESIZER
# Generates heartbeats, banshee shrieks, thunder, whisper drones, and tinnitus.
# ------------------------------------------------------------------------------
class HorrorSoundEngine:
    def __init__(self):
        self.sounds = {}
        try:
            self.sounds["crystal"] = self._synth_arpeggio([523, 659, 784, 1046], [0.08, 0.08, 0.1, 0.25], 0.22)
            self.sounds["door"] = self._synth_creak(0.48, 0.26)
            self.sounds["shift"] = self._synth_tinnitus_silence(0.55, 0.24)
            self.sounds["trap"] = self._synth_zap(0.35, 0.3)
            self.sounds["click"] = self._synth_tone(880, 0.04, 0.12)
            self.sounds["win"] = self._synth_arpeggio([440, 554, 659, 880, 1108], [0.12, 0.12, 0.12, 0.18, 0.5], 0.3)
            self.sounds["heartbeat"] = self._synth_heartbeat(0.42, 0.45)
            self.sounds["banshee"] = self._synth_banshee(0.85, 0.35)
            self.sounds["thunder"] = self._synth_thunder(1.2, 0.45)
            self.sounds["lantern"] = self._synth_arpeggio([440, 660, 880], [0.12, 0.15, 0.4], 0.28)
            self.sounds["jumpscare"] = self._synth_jumpscare(0.65, 0.5)
            self.sounds["step"] = self._synth_step(0.06, 0.08)
        except Exception as e:
            print(f"Sound synthesis note: {e}")

    def _pack_wav(self, samples, rate=22050):
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(struct.pack("<" + "h" * len(samples), *samples))
        return pygame.mixer.Sound(buf.getvalue())

    def _synth_tone(self, freq, duration, vol=0.2, rate=22050):
        n = int(rate * duration)
        samples = []
        for i in range(n):
            t = i / rate
            env = math.exp(-3.0 * (i / n))
            val = int(32767 * vol * env * math.sin(2 * math.pi * freq * t))
            samples.append(max(-32767, min(32767, val)))
        return self._pack_wav(samples, rate)

    def _synth_arpeggio(self, freqs, durations, vol=0.2, rate=22050):
        samples = []
        for freq, dur in zip(freqs, durations):
            n = int(rate * dur)
            for i in range(n):
                t = i / rate
                env = 1.0 - (i / n) * 0.7
                val = int(32767 * vol * env * (math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(4 * math.pi * freq * t)))
                samples.append(max(-32767, min(32767, val)))
        return self._pack_wav(samples, rate)

    def _synth_heartbeat(self, duration=0.42, vol=0.45, rate=22050):
        n = int(rate * duration)
        samples = []
        for i in range(n):
            t = i / rate
            p1 = math.exp(-32 * t) * math.sin(2 * math.pi * 52 * t)
            p2 = math.exp(-32 * max(0, t - 0.16)) * math.sin(2 * math.pi * 48 * max(0, t - 0.16)) if t >= 0.16 else 0
            val = int(32767 * vol * (p1 + p2))
            samples.append(max(-32767, min(32767, val)))
        return self._pack_wav(samples, rate)

    def _synth_banshee(self, duration=0.85, vol=0.35, rate=22050):
        n = int(rate * duration)
        samples = []
        for i in range(n):
            t = i / rate
            prog = t / duration
            freq = 1300 - 700 * prog + 90 * math.sin(36 * math.pi * t)
            env = math.sin(math.pi * prog) ** 2
            noise = (random.random() * 2 - 1) * 0.25
            val = int(32767 * vol * env * (math.sin(2 * math.pi * freq * t) + noise))
            samples.append(max(-32767, min(32767, val)))
        return self._pack_wav(samples, rate)

    def _synth_thunder(self, duration=1.2, vol=0.45, rate=22050):
        n = int(rate * duration)
        samples = []
        for i in range(n):
            t = i / rate
            env = math.exp(-2.2 * t)
            noise = (random.random() * 2 - 1) * 0.7
            rumble = math.sin(2 * math.pi * 42 * t) * 0.3
            val = int(32767 * vol * env * (noise + rumble))
            samples.append(max(-32767, min(32767, val)))
        return self._pack_wav(samples, rate)

    def _synth_tinnitus_silence(self, duration=0.55, vol=0.24, rate=22050):
        # High-frequency ear ringing + vacuum drop for the "Silent Glitch"
        n = int(rate * duration)
        samples = []
        for i in range(n):
            t = i / rate
            env = math.sin(math.pi * (t / duration)) ** 1.5
            ring = math.sin(2 * math.pi * 4200 * t) * 0.5
            val = int(32767 * vol * env * ring)
            samples.append(max(-32767, min(32767, val)))
        return self._pack_wav(samples, rate)

    def _synth_creak(self, duration=0.48, vol=0.26, rate=22050):
        n = int(rate * duration)
        samples = []
        for i in range(n):
            prog = i / n
            freq = 85 + 45 * math.sin(16 * math.pi * prog) + (prog * 35)
            env = math.sin(math.pi * prog)
            noise = (random.random() * 2 - 1) * 0.2
            val = int(32767 * vol * env * (math.sin(2 * math.pi * freq * (i / rate)) + noise))
            samples.append(max(-32767, min(32767, val)))
        return self._pack_wav(samples, rate)

    def _synth_zap(self, duration=0.35, vol=0.3, rate=22050):
        n = int(rate * duration)
        samples = []
        for i in range(n):
            prog = i / n
            freq = 180 + (1.0 - prog) * 420
            noise = (random.random() * 2 - 1) * 0.6
            env = (1.0 - prog) ** 1.8
            val = int(32767 * vol * env * (math.sin(2 * math.pi * freq * (i / rate)) * 0.4 + noise))
            samples.append(max(-32767, min(32767, val)))
        return self._pack_wav(samples, rate)

    def _synth_jumpscare(self, duration=0.65, vol=0.5, rate=22050):
        n = int(rate * duration)
        samples = []
        for i in range(n):
            t = i / rate
            env = math.exp(-3.5 * t)
            noise = (random.random() * 2 - 1) * 0.8
            bass = math.sin(2 * math.pi * 75 * t) * 0.4
            screech = math.sin(2 * math.pi * 1400 * t) * 0.3
            val = int(32767 * vol * env * (noise + bass + screech))
            samples.append(max(-32767, min(32767, val)))
        return self._pack_wav(samples, rate)

    def _synth_step(self, duration=0.06, vol=0.08, rate=22050):
        n = int(rate * duration)
        samples = []
        for i in range(n):
            t = i / rate
            env = math.exp(-45 * t)
            noise = (random.random() * 2 - 1) * 0.4
            wood = math.sin(2 * math.pi * 95 * t) * 0.6
            val = int(32767 * vol * env * (noise + wood))
            samples.append(max(-32767, min(32767, val)))
        return self._pack_wav(samples, rate)

    def play(self, name):
        if name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception:
                pass

SOUNDS = HorrorSoundEngine()

# ------------------------------------------------------------------------------
# 8 HAUNTED ROOM DEFINITIONS (MATCHING REFERENCE PICTURES 1, 2, & 3)
# Mood: Decayed, water-stained, peeling wallpaper, mould, candlelit gloom
# ------------------------------------------------------------------------------
ROOM_INFO = [
    # Top Row (y < 10)
    {
        "id": 0, "name": "LIVING ROOM", "col": 0, "row": 0,
        "desc": "Peeling grimy walls, rotting ceiling medallion & worn leather sofa",
        "crystal_color": (60, 220, 255), "crystal_inner": (220, 250, 255), "crystal_name": "Sapphire Tear",
        "floor": (24, 20, 18), "rug": (62, 28, 26), "ceiling": (16, 14, 12), "accent": (215, 85, 95)
    },
    {
        "id": 1, "name": "MASTER BEDROOM", "col": 1, "row": 0,
        "desc": "Pitch-black bedchamber, kerosene lantern & moonlit shadow window",
        "crystal_color": (210, 75, 255), "crystal_inner": (250, 215, 255), "crystal_name": "Amethyst Eye",
        "floor": (20, 16, 22), "rug": (55, 22, 52), "ceiling": (14, 12, 18), "accent": (205, 85, 245)
    },
    {
        "id": 2, "name": "CASTLE KITCHEN", "col": 2, "row": 0,
        "desc": "Grimy stone hearth, mouldy flagstones & iron cooking stove",
        "crystal_color": (50, 245, 140), "crystal_inner": (215, 255, 235), "crystal_name": "Emerald Spark",
        "floor": (26, 26, 24), "rug": (42, 38, 30), "ceiling": (18, 18, 16), "accent": (65, 235, 145)
    },
    {
        "id": 3, "name": "STUDY ROOM", "col": 3, "row": 0,
        "desc": "Dusty crumbling bookshelves, faded partner desk & tarnished globe",
        "crystal_color": (255, 175, 45), "crystal_inner": (255, 240, 190), "crystal_name": "Topaz Core",
        "floor": (24, 18, 14), "rug": (22, 45, 32), "ceiling": (16, 14, 10), "accent": (245, 185, 65)
    },
    # Bottom Row (y >= 10)
    {
        "id": 4, "name": "GUEST ROOM", "col": 0, "row": 1,
        "desc": "Water-damaged peeling walls, rusted spindle bed & cold moonbeams",
        "crystal_color": (255, 65, 125), "crystal_inner": (255, 210, 230), "crystal_name": "Ruby Blossom",
        "floor": (18, 20, 26), "rug": (52, 28, 38), "ceiling": (12, 14, 20), "accent": (245, 95, 145)
    },
    {
        "id": 5, "name": "STORAGE ROOM", "col": 1, "row": 1,
        "desc": "Rotting timber vault with cobwebs, wine barrels & leaning ladder",
        "crystal_color": (255, 225, 50), "crystal_inner": (255, 255, 200), "crystal_name": "Solar Citrine",
        "floor": (22, 20, 15), "rug": (48, 38, 22), "ceiling": (15, 12, 9), "accent": (245, 215, 75)
    },
    {
        "id": 6, "name": "DUSTY ATTIC", "col": 2, "row": 1,
        "desc": "Slanted dark rafters, heavy cobwebs, rocking chair & antique trunk",
        "crystal_color": (70, 230, 255), "crystal_inner": (230, 252, 255), "crystal_name": "Sky Diamond",
        "floor": (20, 18, 15), "rug": (44, 34, 28), "ceiling": (14, 13, 18), "accent": (80, 225, 245)
    },
    {
        "id": 7, "name": "SECRET HALLWAY", "col": 3, "row": 1,
        "desc": "Ancient stone corridor with flickering torches & askew portraits",
        "crystal_color": (180, 70, 250), "crystal_inner": (245, 205, 255), "crystal_name": "Void Crystal",
        "floor": (18, 18, 22), "rug": (85, 16, 26), "ceiling": (12, 12, 16), "accent": (195, 80, 245)
    },
]

def get_room_id(x, y):
    col = 0 if x <= 6 else (1 if x <= 12 else (2 if x <= 18 else 3))
    row = 0 if y <= 10 else 1
    return row * 4 + col

# ------------------------------------------------------------------------------
# PROCEDURAL HIGH-RESOLUTION HAUNTED TEXTURES (MATCHING REFERENCE PICS)
# Peeling wallpaper, water damage, mould, soot, and authentic decayed surfaces.
# ------------------------------------------------------------------------------
class TextureBank:
    def __init__(self):
        self.raw_textures = {}
        self.shaded_banks = {}
        self._build_textures()
        self._pre_shade_all()

    def _build_textures(self):
        # Room 0: LIVING ROOM (Grungy, peeling wallpaper with water stains & rot)
        t0 = pygame.Surface((128, 128))
        t0.fill((52, 42, 36)) # Decayed dirty base
        # Peeling plaster patches & water stains (Matching Image 2)
        for y in range(0, 128, 4):
            shade = random.Random(y * 19).randint(-12, 12)
            c = (max(0, min(255, 48 + shade)), max(0, min(255, 38 + shade)), max(0, min(255, 32 + shade)))
            pygame.draw.line(t0, c, (0, y), (128, y))
        # Mould & grime dripping downwards
        for gx in (14, 38, 72, 98, 115):
            gh = random.Random(gx * 7).randint(40, 95)
            pygame.draw.line(t0, (26, 22, 18), (gx, 0), (gx, gh), 3)
            pygame.draw.line(t0, (32, 28, 22), (gx + 1, 0), (gx + 1, gh - 8), 1)
        # Faded, peeling burgundy damask wallpaper remains
        for y in range(8, 68, 18):
            for x in range(8, 128, 22):
                pygame.draw.circle(t0, (75, 28, 32), (x, y), 4)
                pygame.draw.line(t0, (55, 20, 24), (x - 4, y), (x + 4, y), 1)
        # Decayed dark wainscot paneling bottom (Matching Image 1)
        pygame.draw.rect(t0, (32, 24, 20), (0, 75, 128, 53))
        pygame.draw.rect(t0, (22, 16, 12), (0, 74, 128, 2))
        for px in (8, 68):
            pygame.draw.rect(t0, (40, 28, 22), (px, 82, 52, 42), border_radius=2)
            pygame.draw.rect(t0, (20, 14, 10), (px, 82, 52, 42), 2, border_radius=2)
            # Scratches on wood
            pygame.draw.line(t0, (18, 12, 8), (px + 6, 88), (px + 14, 104), 1)
        self.raw_textures[0] = t0

        # Room 1: MASTER BEDROOM (Cold dark walls, peeling mould & bedside lantern glow)
        t1 = pygame.Surface((128, 128))
        t1.fill((36, 28, 38))
        # Water damage streaks & damp mould
        for gx in (18, 48, 85, 110):
            gh = random.Random(gx * 11).randint(35, 90)
            pygame.draw.line(t1, (20, 16, 24), (gx, 0), (gx, gh), 4)
        # Faded purple wallpaper remnants
        for y in range(10, 70, 20):
            for x in range(10, 128, 20):
                pygame.draw.circle(t1, (58, 32, 65), (x, y), 3)
        # Dark rotting timber wainscot
        pygame.draw.rect(t1, (26, 18, 28), (0, 75, 128, 53))
        for x in range(0, 128, 10):
            pygame.draw.line(t1, (16, 10, 18), (x, 75), (x, 127), 1)
        # Tarnished askew frame (Matching Image 1)
        pygame.draw.rect(t1, (55, 42, 30), (52, 25, 26, 32), 2)
        pygame.draw.rect(t1, (18, 14, 16), (54, 27, 22, 28))
        self.raw_textures[1] = t1

        # Room 2: CASTLE KITCHEN (Mouldy ancient stone ashlar & hanging iron)
        t2 = pygame.Surface((128, 128))
        t2.fill((48, 48, 46))
        for row, y in enumerate(range(0, 128, 22)):
            offset = 18 if row % 2 else 0
            for x in range(-offset, 130, 36):
                shade = random.Random(x * 19 + y).randint(-10, 8)
                c = (max(0, min(255, 52 + shade)), max(0, min(255, 50 + shade)), max(0, min(255, 48 + shade)))
                pygame.draw.rect(t2, c, (x + 1, y + 1, 34, 20))
                pygame.draw.rect(t2, (22, 22, 20), (x, y, 36, 22), 1)
        # Dark grime & mould on stones
        for mx in (24, 70, 105):
            pygame.draw.circle(t2, (28, 34, 28), (mx, 55), 8)
        # Rusty hanging pot rack
        pygame.draw.line(t2, (24, 24, 26), (18, 42), (110, 42), 3)
        for hx in (38, 64, 90):
            pygame.draw.line(t2, (24, 24, 26), (hx, 42), (hx, 52), 2)
            pygame.draw.circle(t2, (75, 45, 35), (hx, 60), 8)
        self.raw_textures[2] = t2

        # Room 3: STUDY ROOM (Dusty, deteriorating bookshelves & decayed volumes)
        t3 = pygame.Surface((128, 128))
        t3.fill((38, 26, 18))
        book_colors = [(75, 22, 24), (24, 55, 32), (85, 68, 30), (22, 32, 58), (62, 38, 25)]
        for shelf_y in (6, 38, 70, 102):
            pygame.draw.rect(t3, (52, 34, 22), (0, shelf_y + 26, 128, 6))
            pygame.draw.line(t3, (18, 10, 8), (0, shelf_y + 32), (128, shelf_y + 32), 2)
            cur_x = 4
            rng = random.Random(shelf_y * 43)
            while cur_x < 124:
                bw = rng.randint(4, 9)
                bh = rng.randint(18, 24)
                bc = rng.choice(book_colors)
                pygame.draw.rect(t3, bc, (cur_x, shelf_y + 26 - bh, bw, bh))
                pygame.draw.line(t3, (16, 10, 6), (cur_x, shelf_y + 26 - bh), (cur_x, shelf_y + 26), 1)
                cur_x += bw + 1
        # Cobwebs across books
        pygame.draw.line(t3, (110, 115, 125), (0, 0), (35, 30), 1)
        pygame.draw.line(t3, (110, 115, 125), (128, 0), (95, 28), 1)
        self.raw_textures[3] = t3

        # Room 4: GUEST ROOM (Water-stained slate wallpaper & cracked mouldings)
        t4 = pygame.Surface((128, 128))
        t4.fill((34, 42, 48))
        for x in range(0, 128, 14):
            pygame.draw.line(t4, (44, 54, 62), (x, 0), (x, 75), 1)
        # Peeling water stains
        for wx in (25, 78, 108):
            pygame.draw.line(t4, (20, 24, 28), (wx, 0), (wx, 68), 3)
        # Decayed lower wainscoting
        pygame.draw.rect(t4, (48, 52, 58), (0, 75, 128, 53))
        pygame.draw.rect(t4, (24, 26, 30), (0, 74, 128, 2))
        for px in (10, 70):
            pygame.draw.rect(t4, (58, 62, 70), (px, 82, 48, 40), border_radius=2)
            pygame.draw.rect(t4, (28, 30, 35), (px, 82, 48, 40), 2, border_radius=2)
        self.raw_textures[4] = t4

        # Room 5: STORAGE ROOM (Splintered weathered timber planks & rusty nails)
        t5 = pygame.Surface((128, 128))
        t5.fill((44, 34, 24))
        for y in range(0, 128, 18):
            pygame.draw.line(t5, (22, 16, 10), (0, y), (128, y), 2)
            pygame.draw.line(t5, (58, 46, 34), (0, y + 2), (128, y + 2), 1)
            for nx in (12, 64, 116):
                pygame.draw.circle(t5, (16, 12, 10), (nx, y + 8), 2)
        # Shelving with dusty cobwebbed bottles
        pygame.draw.rect(t5, (55, 40, 28), (0, 68, 128, 6))
        for bx in (22, 32, 75, 88):
            pygame.draw.rect(t5, (28, 38, 28), (bx, 52, 6, 16), border_radius=1)
        self.raw_textures[5] = t5

        # Room 6: DUSTY ATTIC (Exposed rafters, heavy cobwebs & timber slats)
        t6 = pygame.Surface((128, 128))
        t6.fill((36, 28, 22))
        pygame.draw.line(t6, (52, 38, 28), (0, 0), (128, 128), 8)
        pygame.draw.line(t6, (20, 14, 10), (0, 0), (128, 128), 2)
        pygame.draw.line(t6, (52, 38, 28), (128, 0), (0, 128), 8)
        pygame.draw.line(t6, (20, 14, 10), (128, 0), (0, 128), 2)
        # Thick cobwebs (Matching horror attic)
        for r in (18, 34, 50):
            pygame.draw.arc(t6, (125, 130, 140), (-10, -10, r * 2, r * 2), 0, math.pi / 2, 1)
            pygame.draw.arc(t6, (125, 130, 140), (128 - r, -10, r * 2, r * 2), math.pi / 2, math.pi, 1)
        self.raw_textures[6] = t6

        # Room 7: SECRET HALLWAY (Ancient mouldy stone blocks & flaming sconce)
        t7 = pygame.Surface((128, 128))
        t7.fill((36, 38, 44))
        for y in range(0, 128, 24):
            pygame.draw.line(t7, (18, 18, 22), (0, y), (128, y), 2)
        pygame.draw.arc(t7, (55, 58, 68), (14, 12, 100, 100), 0, math.pi, 3)
        # Wall torch sconce
        pygame.draw.line(t7, (18, 18, 20), (64, 60), (64, 85), 4)
        pygame.draw.circle(t7, (255, 130, 30), (64, 46), 8)
        pygame.draw.circle(t7, (255, 215, 60), (64, 45), 5)
        self.raw_textures[7] = t7

        # GOTHIC ARCHED DOUBLE DOOR (Matching Image 1 & 2)
        td = pygame.Surface((128, 128))
        td.fill((58, 60, 68)) # Decayed stone arch surround
        pygame.draw.arc(td, (82, 85, 95), (8, 6, 112, 80), 0, math.pi, 6)
        pygame.draw.rect(td, (92, 95, 105), (58, 4, 12, 14))
        # Heavy Dark Oak door panels
        pygame.draw.rect(td, (38, 25, 18), (16, 22, 96, 106))
        pygame.draw.line(td, (14, 10, 6), (64, 22), (64, 127), 3)
        for dx in (22, 70):
            pygame.draw.rect(td, (26, 16, 12), (dx, 32, 36, 42), border_radius=4)
            pygame.draw.rect(td, (52, 34, 24), (dx, 32, 36, 42), 2, border_radius=4)
            pygame.draw.rect(td, (26, 16, 12), (dx, 82, 36, 40), border_radius=3)
            pygame.draw.rect(td, (52, 34, 24), (dx, 82, 36, 40), 2, border_radius=3)
        for hy in (44, 96):
            pygame.draw.polygon(td, (18, 18, 22), [(16, hy - 4), (54, hy - 2), (58, hy), (54, hy + 2), (16, hy + 4)])
            pygame.draw.polygon(td, (18, 18, 22), [(112, hy - 4), (74, hy - 2), (70, hy), (74, hy + 2), (112, hy + 4)])
        # Brass lion ring handles
        pygame.draw.circle(td, (165, 130, 45), (52, 74), 5, 2)
        pygame.draw.circle(td, (165, 130, 45), (76, 74), 5, 2)
        self.raw_textures["door"] = td

        # SILENT GLITCH REALM VARIANT (Desaturated psychological horror / ash void)
        tg = pygame.Surface((128, 128))
        tg.fill((16, 16, 20))
        for y in range(0, 128, 6):
            c_val = random.Random(y * 37).randint(15, 35)
            pygame.draw.line(tg, (c_val, c_val, c_val + 4), (0, y), (128, y), 1)
        # Ghostly spiritual runes & cold fissures
        pygame.draw.line(tg, (180, 190, 210), (12, 18), (55, 18), 1)
        pygame.draw.line(tg, (180, 190, 210), (55, 18), (85, 85), 1)
        pygame.draw.circle(tg, (220, 230, 255), (55, 18), 3)
        self.raw_textures["glitch"] = tg

    def _pre_shade_all(self):
        for key, surf in self.raw_textures.items():
            for dim in (0, 1):
                bank = []
                for level in range(10):
                    factor = 1.0 - (level / 9.0) * 0.88
                    shaded = surf.copy()
                    if dim == 1 and key != "glitch":
                        # Ash-grey desaturation for Silent Glitch
                        gray_surf = pygame.Surface((128, 128))
                        gray_surf.fill((120, 125, 140))
                        shaded.blit(gray_surf, (0, 0), special_flags=pygame.BLEND_MULT)
                    if factor < 1.0:
                        dark_overlay = pygame.Surface((128, 128))
                        dark_overlay.fill((0, 0, 0))
                        dark_overlay.set_alpha(int(255 * (1.0 - factor)))
                        shaded.blit(dark_overlay, (0, 0))
                    bank.append(shaded)
                self.shaded_banks[(key, dim)] = bank

    def get_column(self, tex_key, dim, u, depth, max_depth=20.0, blackout=False, lantern_boost=0.0):
        # Darkness factor under blackout or lantern illumination
        eff_depth = depth
        if blackout:
            eff_depth = max(0.01, depth * 2.8 - lantern_boost)
        level = min(9, max(0, int((eff_depth / max_depth) * 9.5)))
        surf = self.shaded_banks.get((tex_key, dim), self.shaded_banks[(0, 0)])[level]
        col_x = max(0, min(127, int(u * 128)))
        return surf.subsurface((col_x, 0, 1, 128))

TEXTURES = TextureBank()

# ------------------------------------------------------------------------------
# GRAPHIC GOTHIC CASTLE DOOR CLASS
# ------------------------------------------------------------------------------
class CastleDoor:
    def __init__(self, x, y, orientation, label="Castle Gate"):
        self.x = x
        self.y = y
        self.orientation = orientation
        self.open_amount = 0.0
        self.target_open = 0.0
        self.label = label

    def update(self, dt):
        if self.open_amount < self.target_open:
            self.open_amount = min(self.target_open, self.open_amount + 2.4 * dt)
        elif self.open_amount > self.target_open:
            self.open_amount = max(self.target_open, self.open_amount - 2.4 * dt)

    def toggle(self):
        self.target_open = 1.0 if self.target_open <= 0.1 else 0.0
        SOUNDS.play("door")

    def is_solid(self):
        return self.open_amount < 0.65

# ------------------------------------------------------------------------------
# THE CHASING GHOST CLASS (FINAL 25-SECOND HORROR MECHANIC)
# Matches Image 3: Shadow silhouette, hollow glowing eyes, outstretched hands
# ------------------------------------------------------------------------------
class ChasingGhost:
    def __init__(self):
        self.x = 22.0
        self.y = 15.0
        self.active = False
        self.speed = 1.85
        self.heartbeat_timer = 0.0
        self.jumpscare_cooldown = 0.0

    def spawn(self, px, py):
        # Spawn away from the player
        self.active = True
        self.x = 22.5 if px < 13.0 else 2.5
        self.y = 15.5 if py < 10.0 else 3.5
        SOUNDS.play("banshee")

    def update(self, dt, px, py, level_num, current_dim):
        if not self.active:
            return

        dx = px - self.x
        dy = py - self.y
        dist = math.hypot(dx, dy)

        # Move towards player
        spd = self.speed * (1.2 if level_num == 3 else 1.0)
        if dist > 0.1:
            self.x += (dx / dist) * spd * dt
            self.y += (dy / dist) * spd * dt

        # Accelerating Proximity Heartbeat Audio
        if dist < 8.0:
            self.heartbeat_timer -= dt
            # Interval scales from 1.0s down to 0.35s
            beat_interval = max(0.32, min(1.0, dist / 8.0))
            if self.heartbeat_timer <= 0.0:
                SOUNDS.play("heartbeat")
                self.heartbeat_timer = beat_interval

        # Jumpscare attack on collision
        self.jumpscare_cooldown = max(0.0, self.jumpscare_cooldown - dt)
        if dist < 0.6 and self.jumpscare_cooldown <= 0.0:
            self.jumpscare_cooldown = 2.0
            SOUNDS.play("jumpscare")
            return True # Damage dealt
        return False

# ------------------------------------------------------------------------------
# LEVEL BUILDER
# ------------------------------------------------------------------------------
def build_room_level(level_no):
    width, height = 26, 20
    cells = [["." for _ in range(width)] for _ in range(height)]
    for x in range(width):
        cells[0][x] = cells[height - 1][x] = "#"
    for y in range(height):
        cells[y][0] = cells[y][width - 1] = "#"

    vdoor_y_up = 3 + (level_no % 2)
    vdoor_y_down = 14 + (level_no % 2)
    for wall_x in (6, 12, 18):
        for y in range(1, height - 1):
            if y == vdoor_y_up or y == vdoor_y_down:
                cells[y][wall_x] = "D"
            else:
                cells[y][wall_x] = "#"

    for x in range(1, width - 1):
        if x in (4, 16):
            cells[10][x] = "D"
        else:
            cells[10][x] = "#"

    crystals_pos = [
        (3.5, 3.5), (9.5, 3.5), (15.5, 3.5), (22.0, 3.5),
        (3.5, 15.5), (9.5, 15.5), (15.5, 15.5), (22.0, 15.5),
    ]
    traps_pos = [
        [(4.0, 7.0), (10.0, 5.5), (16.0, 7.0), (23.0, 8.0), (3.5, 17.5), (11.0, 16.5), (17.0, 17.5), (23.5, 13.5)],
        [(4.0, 5.5), (10.0, 8.0), (16.0, 5.5), (23.0, 7.5), (4.5, 16.5), (10.0, 17.5), (16.0, 16.5), (23.0, 17.0)],
        [(4.0, 7.0), (10.0, 6.5), (16.0, 7.0), (23.0, 6.0), (4.0, 17.5), (10.5, 16.5), (16.5, 17.5), (23.5, 16.5)],
    ][level_no]
    exit_pos = (24.2, 18.2)
    lantern_pos = (15.5, 4.5) if level_no == 1 else (9.5, 15.5)
    return cells, crystals_pos, traps_pos, exit_pos, lantern_pos

LEVELS = [build_room_level(i) for i in range(3)]

def load_level(idx):
    cells_raw, crys_pos, tr_pos, exit_pos, lant_pos = LEVELS[idx]
    grid = [list(row) for row in cells_raw]
    doors = {}
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            if c == "D":
                orient = "H" if y == 10 else "V"
                doors[(x, y)] = CastleDoor(x, y, orient)
    crystals = []
    for i, (cx, cy) in enumerate(crys_pos):
        crystals.append({
            "x": cx, "y": cy, "active": True, "room_id": i,
            "color": ROOM_INFO[i]["crystal_color"],
            "inner": ROOM_INFO[i]["crystal_inner"],
            "name": ROOM_INFO[i]["crystal_name"]
        })
    traps = list(tr_pos)
    ghost = ChasingGhost()
    return grid, doors, crystals, traps, exit_pos, lant_pos, ghost

level_index = 0
grid, doors, crystals, traps, exit_pos, lantern_pos, ghost = load_level(level_index)
player_x, player_y = 2.0, 2.5
player_angle = 0.0
dimension = 0
health = 100
lives = 3
score = 0
message = "Explore all 8 haunted rooms & collect every crystal!"
message_timer = 4.0
trap_cooldown = 0.0
game_won = False
game_over = False
time_expired = False
LEVEL_TIME_LIMITS = [140.0, 130.0, 110.0]
time_left = LEVEL_TIME_LIMITS[0]
level_elapsed = 0.0
blackout_active = False
has_lantern = False
jumpscare_flash = 0.0
walk_timer = 0.0
step_timer = 0.0
bob_offset = 0

gift_chosen = False
gift_name = "No gift selected"
gift_bonus = 0
gift_shield = 0

# Extended Narrative & Achievement States (Silent Glitch: The Shadow Is You)
l1_surprise_shown = False
has_crimson_key = False
crimson_key_pos = (9.5, 14.5)
total_crystals_collected = 0
ending_slide = 0
ending_slide_timer = 0.0

def is_solid(x, y):
    ix, iy = int(x), int(y)
    if iy < 0 or iy >= len(grid) or ix < 0 or ix >= len(grid[iy]):
        return True
    cell = grid[iy][ix]
    if cell == "#":
        return True
    if cell == "D":
        door = doors.get((ix, iy))
        if door and door.is_solid():
            return True
    return False

def can_move(x, y):
    for ox, oy in [(-PLAYER_RADIUS, -PLAYER_RADIUS), (PLAYER_RADIUS, -PLAYER_RADIUS),
                   (-PLAYER_RADIUS, PLAYER_RADIUS), (PLAYER_RADIUS, PLAYER_RADIUS)]:
        if is_solid(x + ox, y + oy):
            return False
    return True

def reset_player():
    global player_x, player_y, player_angle
    player_x, player_y, player_angle = 2.0, 2.5, 0.0

# ------------------------------------------------------------------------------
# RAYCASTING WITH DOOR PENETRATION & DYNAMIC LIGHTING
# ------------------------------------------------------------------------------
def cast_ray(angle):
    ray_x, ray_y = math.cos(angle), math.sin(angle)
    depth = 0.0
    last_door_cell = None

    while depth < MAX_DEPTH:
        depth += RAY_STEP
        px = player_x + ray_x * depth
        py = player_y + ray_y * depth
        ix, iy = int(px), int(py)

        if iy < 0 or iy >= len(grid) or ix < 0 or ix >= len(grid[iy]):
            return MAX_DEPTH, False, 0, 0.0, "wall"

        cell = grid[iy][ix]
        if cell == "D" and (ix, iy) != last_door_cell:
            door = doors.get((ix, iy))
            if door:
                if door.orientation == "V" and abs(ray_x) > 1e-5:
                    d_mid = (ix + 0.5 - player_x) / ray_x
                    if d_mid > 0:
                        y_at = player_y + ray_y * d_mid
                        if int(y_at) == iy:
                            u = y_at - iy
                            if u >= door.open_amount:
                                return d_mid, True, "door", (u - door.open_amount) / max(0.01, 1.0 - door.open_amount), "door"
                            else:
                                last_door_cell = (ix, iy)
                elif door.orientation == "H" and abs(ray_y) > 1e-5:
                    d_mid = (iy + 0.5 - player_y) / ray_y
                    if d_mid > 0:
                        x_at = player_x + ray_x * d_mid
                        if int(x_at) == ix:
                            u = x_at - ix
                            if u >= door.open_amount:
                                return d_mid, False, "door", (u - door.open_amount) / max(0.01, 1.0 - door.open_amount), "door"
                            else:
                                last_door_cell = (ix, iy)

        if cell == "#":
            hit_side = int(px) != int(px - ray_x * RAY_STEP)
            u = (py % 1.0) if hit_side else (px % 1.0)
            room_id = get_room_id(ix, iy)
            return depth, hit_side, room_id, u, "wall"

    return MAX_DEPTH, False, 0, 0.0, "wall"

# ------------------------------------------------------------------------------
# 3D WORLD RENDERING
# ------------------------------------------------------------------------------
def draw_world():
    cur_room_id = get_room_id(int(player_x), int(player_y))
    room_cfg = ROOM_INFO[cur_room_id]

    is_blackout = (blackout_active and not has_lantern)
    lantern_boost = 3.5 if has_lantern else 0.0
    horizon = HALF_H + bob_offset

    # 1. CEILING PERSPECTIVE & SOOT STAIN
    ceil_color = (8, 8, 10) if is_blackout else ((14, 14, 18) if dimension == 1 else room_cfg["ceiling"])
    screen.fill(ceil_color)
    if not is_blackout:
        for band in range(1, 8):
            y = int(horizon * (band / 8) ** 1.6)
            c_shade = 4 + band * 2
            line_col = (min(255, ceil_color[0] + c_shade),
                        min(255, ceil_color[1] + c_shade),
                        min(255, ceil_color[2] + c_shade + (3 if dimension == 0 else 8)))
            pygame.draw.line(screen, line_col, (0, y), (WIDTH, y), 1)

    # 2. FLOOR: CREAKY WEATHERED WOODEN FLOORBOARDS (Matching Image 1 & 2)
    floor_color = (10, 8, 8) if is_blackout else ((16, 16, 20) if dimension == 1 else room_cfg["floor"])
    pygame.draw.rect(screen, floor_color, (0, horizon, WIDTH, HEIGHT - horizon))

    # Horizontal floorboard plank seams receding into the gloom (No route light!)
    if not is_blackout:
        for i in range(1, 15):
            y = horizon + int((i / 15) ** 2.2 * max(1, HEIGHT - horizon))
            seam_col = (max(0, floor_color[0] - 5), max(0, floor_color[1] - 4), max(0, floor_color[2] - 4))
            pygame.draw.line(screen, seam_col, (0, y), (WIDTH, y), 1)

    # 3. TEXTURED RAYCASTED WALLS
    z_buffer = [MAX_DEPTH] * NUM_RAYS
    ray_angle = player_angle - FOV / 2
    ray_width = WIDTH / NUM_RAYS

    for ray in range(NUM_RAYS):
        depth, side, hit_id, u, hit_type = cast_ray(ray_angle)
        corrected = max(0.001, depth * math.cos(ray_angle - player_angle))
        z_buffer[ray] = corrected

        wall_height = min(HEIGHT * 2.0, int(HEIGHT / corrected))
        top = horizon - wall_height // 2
        col_x = int(ray * ray_width)
        col_w = int(ray_width + 1)

        tex_key = "door" if hit_type == "door" else (hit_id if dimension == 0 else "glitch")
        col_surf = TEXTURES.get_column(tex_key, dimension, u, corrected, blackout=blackout_active, lantern_boost=lantern_boost)
        scaled_slice = pygame.transform.scale(col_surf, (col_w, wall_height))
        screen.blit(scaled_slice, (col_x, top))

        ray_angle += FOV / NUM_RAYS

    # 4. BILLBOARD PROPS & HORROR ENTITIES
    room_props = [
        # Room 0: LIVING ROOM (Matching Image 2: Leather chesterfield sofa & oval table)
        (2.8, 6.1, "chesterfield_sofa"), (3.5, 3.5, "oval_table"), (4.4, 5.8, "cabinet"), (5.3, 4.8, "curtain"),
        # Room 1: MASTER BEDROOM (Matching Image 3: Bed & Moonlit Shadow Window)
        (9.2, 6.2, "bedroom_bed"), (10.8, 4.2, "wardrobe"), (9.5, 3.5, "wall_lantern"), (7.5, 3.2, "moon_shadow_window"),
        # Room 2: KITCHEN
        (16.4, 4.3, "stove"), (15.5, 7.0, "dining"), (13.6, 5.4, "potrack"),
        # Room 3: STUDY ROOM
        (23.0, 4.0, "bookshelf"), (21.5, 6.2, "desk"), (23.2, 6.8, "globe"),
        # Room 4: GUEST ROOM
        (3.5, 14.0, "ironbed"), (4.8, 16.2, "moonwindow"), (2.5, 16.5, "vanity"),
        # Room 5: STORAGE ROOM
        (9.5, 14.0, "storage"), (7.8, 14.2, "ladder"), (10.8, 16.5, "barrels"),
        # Room 6: DUSTY ATTIC
        (15.5, 14.0, "attic_chest"), (16.8, 16.0, "rockingchair"), (14.2, 13.0, "skylight"),
        # Room 7: SECRET HALLWAY (Matching Image 1: Staircase banister & dark door)
        (20.4, 13.0, "torch"), (20.4, 16.5, "torch"), (22.7, 13.5, "stair_banister"), (21.0, 16.8, "portrait"),
    ]

    sprites = []
    for px, py, kind in room_props:
        sprites.append((px, py, kind, None))

    # Add the 8 Room Crystals
    for crys in crystals:
        if crys["active"]:
            sprites.append((crys["x"], crys["y"], "crystal", crys))

    # Add Eternal Flame Lantern (Level 2)
    if level_index == 1 and not has_lantern:
        sprites.append((lantern_pos[0], lantern_pos[1], "eternal_lantern", None))

    # Add the Chasing Ghost
    if ghost.active:
        # In Level 3: Invisible in Real World unless in Glitch Dimension!
        if level_index != 2 or dimension == 1:
            sprites.append((ghost.x, ghost.y, "ghost", None))

    # Add Crimson Key in Level 3
    if level_index == 2 and not has_crimson_key:
        sprites.append((crimson_key_pos[0], crimson_key_pos[1], "crimson_key", None))

    # Add Exit Portal Gate
    sprites.append((exit_pos[0], exit_pos[1], "exit", None))

    # Sort back-to-front
    sprites.sort(key=lambda s: math.hypot(s[0] - player_x, s[1] - player_y), reverse=True)
    ticks = pygame.time.get_ticks() / 1000.0

    for sx, sy, kind, extra in sprites:
        dx, dy = sx - player_x, sy - player_y
        dist = math.hypot(dx, dy)
        angle_to = math.atan2(dy, dx)
        rel = (angle_to - player_angle + math.pi) % (2 * math.pi) - math.pi

        if abs(rel) > FOV / 2 + 0.25 or dist < 0.15:
            continue

        screen_x = int((rel + FOV / 2) / FOV * WIDTH)
        ray_idx = max(0, min(NUM_RAYS - 1, int(screen_x / WIDTH * NUM_RAYS)))

        if dist > z_buffer[ray_idx] + 0.2:
            continue

        size = max(6, min(140, int(HEIGHT / dist * 0.38)))

        # DRAW CHASING GHOST (Matching Image 3: Silhouette with outstretched clawed hands)
        if kind == "ghost":
            gw = int(size * 1.5)
            gh = int(size * 2.2)
            gx = screen_x - gw // 2
            gy = horizon - gh // 2 + int(math.sin(ticks * 5.0) * 8)

            # Eerie floating shroud & mist aura
            g_surf = pygame.Surface((gw, gh), pygame.SRCALPHA)
            # Semi-transparent dark shroud with smoky fade
            pygame.draw.ellipse(g_surf, (15, 12, 18, 215), (gw // 4, 0, gw // 2, gh * 4 // 5))
            # Outstretched terrifying shadow arms & claw hands (Matching Image 3)
            pygame.draw.line(g_surf, (15, 12, 18, 230), (gw // 3, gh // 3), (4, gh // 2), 5)
            pygame.draw.line(g_surf, (15, 12, 18, 230), (gw * 2 // 3, gh // 3), (gw - 4, gh // 2), 5)
            # Splayed claw fingers
            for fi in (-4, 0, 4):
                pygame.draw.line(g_surf, (15, 12, 18, 230), (4, gh // 2), (0, gh // 2 + fi), 2)
                pygame.draw.line(g_surf, (15, 12, 18, 230), (gw - 4, gh // 2), (gw, gh // 2 + fi), 2)
            # Glowing hollow red/white eyes
            eye_col = (255, 45, 65) if dimension == 0 else (220, 240, 255)
            pygame.draw.circle(g_surf, eye_col, (gw * 3 // 8, gh // 5), max(2, gw // 16))
            pygame.draw.circle(g_surf, eye_col, (gw * 5 // 8, gh // 5), max(2, gw // 16))
            # Trailing smoke wisps at base
            for si in range(4):
                pygame.draw.circle(g_surf, (30, 24, 35, 120), (gw // 4 + si * (gw // 6), gh - 8), max(4, gw // 10))

            screen.blit(g_surf, (gx, gy))

        # DRAW ETERNAL FLAME LANTERN (Matching Image 3)
        elif kind == "eternal_lantern":
            lw = max(16, int(size * 0.9))
            lh = max(24, int(size * 1.4))
            lx = screen_x - lw // 2
            ly = horizon - lh // 2 + int(math.sin(ticks * 3.0) * 5)
            # Pulsing golden beacon aura
            glow_surf = pygame.Surface((lw * 3, lw * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 195, 65, 80), (lw * 3 // 2, lw * 3 // 2), lw + 8)
            screen.blit(glow_surf, (screen_x - lw * 3 // 2, ly + lh // 2 - lw * 3 // 2))
            # Brass lantern frame
            pygame.draw.rect(screen, (165, 125, 45), (lx, ly, lw, lh), border_radius=3)
            # Glowing flame chamber
            pygame.draw.rect(screen, (255, 245, 160), (lx + 3, ly + 5, lw - 6, lh - 10), border_radius=2)
            pygame.draw.circle(screen, (255, 120, 30), (screen_x, ly + lh // 2), max(2, lw // 6))

        # DRAW CRYSTAL
        elif kind == "crystal":
            c_info = extra
            c_color = c_info["color"] if dimension == 0 else (210, 225, 245)
            c_inner = c_info["inner"] if dimension == 0 else (255, 255, 255)
            float_y = int(math.sin(ticks * 3.5 + c_info["room_id"]) * 7)
            cy = horizon + float_y
            cs = int(size * 0.55)

            glow_surf = pygame.Surface((cs * 3, cs * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*c_color, 45), (cs * 3 // 2, cs * 3 // 2), cs + 8)
            screen.blit(glow_surf, (screen_x - cs * 3 // 2, cy - cs * 3 // 2))

            pts = [(screen_x, cy - cs), (screen_x + cs // 2, cy),
                   (screen_x, cy + cs), (screen_x - cs // 2, cy)]
            pygame.draw.polygon(screen, c_color, pts)
            inner_pts = [(screen_x, cy - cs + 4), (screen_x + cs // 3, cy),
                         (screen_x, cy + cs - 4), (screen_x - cs // 3, cy)]
            pygame.draw.polygon(screen, c_inner, inner_pts)
            pygame.draw.polygon(screen, (255, 255, 255), pts, 1)

        # DRAW CRIMSON KEY (Level 3 Sacred Relic)
        elif kind == "crimson_key":
            kw = max(8, int(size * 0.75))
            kh = max(16, int(size * 1.5))
            kx = screen_x - kw // 2
            ky = horizon - kh // 2 + int(math.sin(ticks * 4.0) * 6)
            glow_surf = pygame.Surface((kw * 3, kh * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 30, 60, 95), (kw * 3 // 2, kh * 3 // 2), kw + 10)
            screen.blit(glow_surf, (screen_x - kw * 3 // 2, ky + kh // 2 - kh * 3 // 2))
            pygame.draw.circle(screen, (255, 45, 75), (screen_x, ky + kh // 4), max(3, kw // 2), 2)
            pygame.draw.line(screen, (255, 70, 95), (screen_x, ky + kh // 4), (screen_x, ky + kh * 4 // 5), max(2, kw // 4))
            pygame.draw.line(screen, (255, 70, 95), (screen_x, ky + kh * 3 // 4), (screen_x + kw // 3, ky + kh * 3 // 4), max(2, kw // 5))

        # DRAW EXIT PORTAL
        elif kind == "exit":
            all_collected = all(not c["active"] for c in crystals)
            portal_color = (255, 210, 65) if all_collected else (65, 62, 75)
            pw, ph = int(size * 1.3), int(size * 2.1)
            px_left = screen_x - pw // 2
            py_top = horizon - ph // 2
            pygame.draw.rect(screen, (28, 28, 35), (px_left - 6, py_top - 6, pw + 12, ph + 12), border_radius=12)
            pygame.draw.rect(screen, portal_color, (px_left, py_top, pw, ph), border_radius=10)
            if all_collected:
                vortex_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
                for ring in range(3):
                    rw = int(pw * (0.3 + ring * 0.25))
                    rh = int(ph * (0.3 + ring * 0.25))
                    pygame.draw.ellipse(vortex_surf, (255, 255, 200, 110), (pw // 2 - rw // 2, ph // 2 - rh // 2, rw, rh), 2)
                screen.blit(vortex_surf, (px_left, py_top))

        # DRAW HAUNTED ROOM PROPS (MATCHING REFERENCE PICS)
        else:
            w = max(12, int(size * 1.85))
            h = max(10, int(size * 0.95))
            left = screen_x - w // 2
            base_y = horizon + h // 2

            if kind == "chesterfield_sofa":
                # Cracked brown leather chesterfield sofa (Matching Image 2)
                leather = (58, 32, 24)
                pygame.draw.rect(screen, (22, 12, 10), (left - 2, base_y - h // 2, w + 4, h // 2 + 5), border_radius=6)
                pygame.draw.rect(screen, leather, (left, base_y - h // 2, w, h // 2), border_radius=6)
                pygame.draw.rect(screen, (85, 48, 35), (left, base_y - h // 2, w, h // 2), 2, border_radius=6)
                # Tufted diamond buttons
                for tx in (left + w // 4, left + w // 2, left + w * 3 // 4):
                    pygame.draw.circle(screen, (28, 16, 12), (tx, base_y - h // 3), 2)

            elif kind == "oval_table":
                # Low dark oval wooden coffee table (Matching Image 2)
                pygame.draw.ellipse(screen, (38, 26, 18), (left, base_y - h // 3, w, h // 3))
                pygame.draw.ellipse(screen, (65, 42, 28), (left, base_y - h // 3, w, h // 3), 2)
                for lx in (left + 6, left + w - 8):
                    pygame.draw.line(screen, (28, 18, 12), (lx, base_y - h // 5), (lx - 2, base_y + max(2, h // 4)), 2)

            elif kind == "moon_shadow_window":
                # Tall window with cold god rays & creepy shadow hands (Matching Image 3)
                win_w = max(14, int(w * 0.8))
                win_h = max(24, int(h * 1.8))
                wx = screen_x - win_w // 2
                wy = base_y - win_h
                pygame.draw.rect(screen, (22, 26, 32), (wx, wy, win_w, win_h))
                # Pale moonlit panes
                for r in range(3):
                    for c in range(2):
                        px = wx + 3 + c * (win_w // 2)
                        py = wy + 3 + r * (win_h // 3)
                        pygame.draw.rect(screen, (175, 205, 230), (px, py, win_w // 2 - 5, win_h // 3 - 5))
                # Shadow figure silhouette with splayed hands on glass!
                pygame.draw.circle(screen, (12, 14, 18), (screen_x, wy + win_h // 4), max(3, win_w // 5))
                pygame.draw.circle(screen, (12, 14, 18), (wx + 6, wy + win_h // 3), 3) # Hand left
                pygame.draw.circle(screen, (12, 14, 18), (wx + win_w - 6, wy + win_h // 3), 3) # Hand right

            elif kind == "stair_banister":
                # Dark wooden staircase railing (Matching Image 1)
                pygame.draw.line(screen, (32, 22, 16), (left, base_y), (left + w, base_y - h), 4)
                for bx in range(left + 4, left + w, max(4, w // 6)):
                    by = base_y - int((bx - left) / w * h)
                    pygame.draw.line(screen, (24, 16, 12), (bx, base_y), (bx, by), 2)

            elif kind == "wall_lantern":
                # Kerosene lantern on wall (Matching Image 3)
                pygame.draw.rect(screen, (45, 34, 20), (screen_x - 3, base_y - h, 6, max(8, h // 2)), border_radius=2)
                pygame.draw.circle(screen, (255, 195, 60), (screen_x, base_y - h + max(4, h // 4)), max(3, h // 6))

            elif kind == "torch":
                pygame.draw.line(screen, (20, 20, 22), (screen_x, base_y - h), (screen_x, base_y - 2), 3)
                pygame.draw.circle(screen, (255, 120, 30), (screen_x, base_y - h), max(4, h // 5))

            else:
                pygame.draw.rect(screen, (42, 28, 20), (left, base_y - h, w, h), border_radius=2)
                pygame.draw.rect(screen, (68, 45, 32), (left, base_y - h, w, h), 2)

    # 5. GHOST PROXIMITY DREAD VIGNETTE
    if ghost.active:
        dist_g = math.hypot(player_x - ghost.x, player_y - ghost.y)
        if dist_g < 7.5:
            vig_factor = max(0.0, min(1.0, (7.5 - dist_g) / 7.5))
            vig_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            border_thick = max(10, int(65 * vig_factor))
            pygame.draw.rect(vig_surf, (15, 0, 5, int(150 * vig_factor)), (0, 0, WIDTH, HEIGHT), border_thick)
            screen.blit(vig_surf, (0, 0))

    # 6. MINIMAP & HUD
    draw_minimap()
    draw_hud(cur_room_id)

    # 7. JUMPSCARE FLASH & RED VIGNETTE
    global jumpscare_flash
    if jumpscare_flash > 0.0:
        js_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        js_surf.fill((180, 10, 25, int(min(220, jumpscare_flash * 255))))
        screen.blit(js_surf, (0, 0))
        jumpscare_flash = max(0.0, jumpscare_flash - 0.05)

# ------------------------------------------------------------------------------
# INTERACTIVE MINIMAP
# ------------------------------------------------------------------------------
def draw_minimap():
    scale = 6
    ox, oy = 18, 86
    pygame.draw.rect(screen, (10, 12, 20, 220), (ox - 4, oy - 4, 26 * scale + 8, 20 * scale + 8), border_radius=6)
    pygame.draw.rect(screen, (50, 60, 80), (ox - 4, oy - 4, 26 * scale + 8, 20 * scale + 8), 1, border_radius=6)

    for y, row in enumerate(grid):
        for x, tile in enumerate(row):
            if tile == "#":
                pygame.draw.rect(screen, (45, 52, 68), (ox + x * scale, oy + y * scale, scale - 1, scale - 1))
            elif tile == "D":
                door = doors.get((x, y))
                color = (75, 230, 160) if (door and not door.is_solid()) else (255, 195, 60)
                pygame.draw.rect(screen, color, (ox + x * scale, oy + y * scale, scale - 1, scale - 1))

    for crys in crystals:
        if crys["active"]:
            pygame.draw.circle(screen, crys["color"], (ox + int(crys["x"] * scale), oy + int(crys["y"] * scale)), 2)

    if level_index == 1 and not has_lantern:
        # Flashing lantern beacon on minimap
        l_color = (255, 220, 75) if int(pygame.time.get_ticks() / 250) % 2 == 0 else (120, 95, 30)
        pygame.draw.circle(screen, l_color, (ox + int(lantern_pos[0] * scale), oy + int(lantern_pos[1] * scale)), 3)

    if ghost.active and (level_index != 2 or dimension == 1):
        pygame.draw.circle(screen, (255, 40, 50), (ox + int(ghost.x * scale), oy + int(ghost.y * scale)), 3)

    pygame.draw.circle(screen, (255, 220, 80), (ox + int(exit_pos[0] * scale), oy + int(exit_pos[1] * scale)), 3)
    pygame.draw.circle(screen, (255, 255, 255), (ox + int(player_x * scale), oy + int(player_y * scale)), 3)

# ------------------------------------------------------------------------------
# HEADS-UP DISPLAY (HUD)
# ------------------------------------------------------------------------------
def draw_heart(index, filled, x, y):
    color = (255, 45, 75) if filled else (55, 28, 38)
    points = [(x, y + 8), (x - 10, y - 2), (x - 10, y - 8), (x - 6, y - 12),
              (x, y - 8), (x + 6, y - 12), (x + 10, y - 8), (x + 10, y - 2)]
    pygame.draw.polygon(screen, color, points)
    pygame.draw.lines(screen, (255, 185, 200), True, points, 1)

def draw_hud(cur_room_id):
    room_cfg = ROOM_INFO[cur_room_id]

    pygame.draw.rect(screen, (8, 10, 18), (0, 0, WIDTH, 74))
    pygame.draw.line(screen, (40, 48, 65), (0, 74), (WIDTH, 74), 1)

    title_surf = pygame.font.SysFont("consolas", 28, bold=True).render("SILENT GLITCH", True, room_cfg["accent"])
    screen.blit(title_surf, (16, 12))
    sub_surf = SMALL.render("Old Haunted Castle", True, (180, 195, 220))
    screen.blit(sub_surf, (18, 46))

    badge_rect = pygame.Rect(235, 14, 205, 46)
    pygame.draw.rect(screen, (20, 24, 38), badge_rect, border_radius=6)
    pygame.draw.rect(screen, room_cfg["accent"], badge_rect, 1, border_radius=6)
    r_name = FONT.render(room_cfg["name"], True, (245, 250, 255))
    screen.blit(r_name, (badge_rect.centerx - r_name.get_width() // 2, badge_rect.y + 6))
    dim_str = "GLITCH VOID" if dimension == 1 else "REAL WORLD"
    dim_surf = SMALL.render(f"[{dim_str}]", True, room_cfg["accent"])
    screen.blit(dim_surf, (badge_rect.centerx - dim_surf.get_width() // 2, badge_rect.y + 26))

    draw_text("LIVES:", 460, 16, (200, 215, 240), SMALL)
    for heart_i in range(3):
        draw_heart(heart_i, lives > heart_i, 520 + heart_i * 26, 20)

    timer_col = (255, 65, 85) if time_left <= 25 else (255, 210, 100)
    draw_text(f"TIME: {max(0, int(math.ceil(time_left))):02d}s", 460, 42, timer_col, FONT)

    active_crystals = sum(1 for c in crystals if c["active"])
    draw_text(f"CRYSTALS: {active_crystals}/8", 640, 16, (100, 255, 230), FONT)
    if level_index == 2:
        k_txt = "CRIMSON KEY: [CARRIED]" if has_crimson_key else "CRIMSON KEY: [IN CRYPT]"
        k_col = (255, 80, 105) if has_crimson_key else (210, 165, 175)
        draw_text(k_txt, 640, 60, k_col, SMALL)

    pygame.draw.rect(screen, (55, 22, 32), (640, 44, 185, 14), border_radius=4)
    hp_w = int(185 * max(0, health) / 100)
    hp_col = (65, 240, 135) if health > 35 else (255, 75, 90)
    pygame.draw.rect(screen, hp_col, (640, 44, hp_w, 14), border_radius=4)
    draw_text(f"{health} HP", 835, 41, (245, 250, 255), SMALL)

    ctrl_str = "W/S move  A/D turn  Q/E strafe  [E] Door  SPACE/SHIFT: Silent Glitch  ESC: Menu"
    draw_text(ctrl_str, 18, HEIGHT - 24, (200, 210, 235), SMALL)

    # NEARBY DOOR PROMPT
    near_door = None
    for door in doors.values():
        if math.hypot(player_x - (door.x + 0.5), player_y - (door.y + 0.5)) < 1.7:
            near_door = door
            break

    if near_door:
        door_action = "CLOSE DOOR" if not near_door.is_solid() else "OPEN DOOR"
        prompt_surf = FONT.render(f"[E] {door_action}", True, (255, 235, 120))
        p_bg = pygame.Surface((prompt_surf.get_width() + 28, prompt_surf.get_height() + 14), pygame.SRCALPHA)
        p_bg.fill((10, 14, 26, 225))
        px = HALF_W - p_bg.get_width() // 2
        py = HEIGHT - 80
        screen.blit(p_bg, (px, py))
        pygame.draw.rect(screen, (255, 205, 80), (px, py, p_bg.get_width(), p_bg.get_height()), 2, border_radius=6)
        screen.blit(prompt_surf, (px + 14, py + 7))

    # BLACKOUT / LANTERN BANNER (Level 2)
    if blackout_active and not has_lantern:
        b_surf = FONT.render("PITCH BLACKNESS FALLS! FIND THE ETERNAL FLAME LANTERN!", True, (255, 215, 80))
        b_bg = pygame.Surface((b_surf.get_width() + 32, 34), pygame.SRCALPHA)
        b_bg.fill((25, 12, 10, 240))
        bx = HALF_W - b_bg.get_width() // 2
        screen.blit(b_bg, (bx, 84))
        pygame.draw.rect(screen, (255, 195, 60), (bx, 84, b_bg.get_width(), 34), 2, border_radius=6)
        screen.blit(b_surf, (bx + 16, 90))

    # GHOST HUNT WARNING
    elif ghost.active:
        g_text = "THE BANSHEE HUNTS! ESCAPE TO THE EXIT PORTAL!" if all(not c["active"] for c in crystals) else "THE GHOST IS HUNTING YOU! DODGE AND COLLECT CRYSTALS!"
        g_surf = FONT.render(g_text, True, (255, 65, 85))
        g_bg = pygame.Surface((g_surf.get_width() + 28, 34), pygame.SRCALPHA)
        g_bg.fill((30, 8, 12, 235))
        gx = HALF_W - g_bg.get_width() // 2
        screen.blit(g_bg, (gx, 84))
        pygame.draw.rect(screen, (255, 45, 65), (gx, 84, g_bg.get_width(), 34), 2, border_radius=6)
        screen.blit(g_surf, (gx + 14, 90))

    elif message_timer > 0:
        msg_surf = FONT.render(message, True, (255, 240, 150))
        msg_bg = pygame.Surface((msg_surf.get_width() + 24, msg_surf.get_height() + 12), pygame.SRCALPHA)
        msg_bg.fill((6, 8, 20, 215))
        screen.blit(msg_bg, (HALF_W - msg_bg.get_width() // 2, 84))
        screen.blit(msg_surf, (HALF_W - msg_surf.get_width() // 2, 90))

def draw_text(text, x, y, color=(235, 245, 255), font=FONT):
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))

# ------------------------------------------------------------------------------
# THE "SILENT GLITCH" PSYCHOLOGICAL HORROR EFFECT
# Sudden sensory desaturation, analog VHS horizontal tear, and shadow flicker
# ------------------------------------------------------------------------------
def draw_silent_glitch_overlay(intense=False):
    rng = random.Random(pygame.time.get_ticks() // (50 if intense else 140))
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((18, 18, 24, 45 if not intense else 95))
    screen.blit(overlay, (0, 0))

    # Horizontal slice tearing (stuttering reality)
    band_count = 14 if intense else 5
    for _ in range(band_count):
        y = rng.randrange(0, HEIGHT)
        h = rng.randrange(2, 12 if intense else 6)
        x_shift = rng.randrange(-30, 31) if intense else rng.randrange(-8, 9)
        col = rng.choice([(180, 190, 210), (120, 125, 140), (220, 225, 240), (30, 30, 40)])
        pygame.draw.rect(screen, (*col, rng.randrange(50, 140)), (x_shift, y, WIDTH, h))

    # Fleeting peripheral shadow apparitions
    if intense or rng.random() < 0.25:
        sx = rng.choice([25, WIDTH - 120])
        sy = rng.randrange(120, HEIGHT - 180)
        pygame.draw.rect(screen, (8, 8, 12, 180), (sx, sy, 75, 140), border_radius=12)

def centered(text, y, font, color):
    surf = font.render(text, True, color)
    rect = pygame.Rect(HALF_W - surf.get_width() // 2, y, surf.get_width(), surf.get_height())
    screen.blit(surf, (rect.x, rect.y))
    return rect

def draw_button(rect, label, mouse_pos, enabled=True, accent=(80, 225, 235)):
    hovered = rect.collidepoint(mouse_pos) and enabled
    fill = (48, 84, 105) if hovered else ((31, 51, 77) if enabled else (34, 36, 48))
    pygame.draw.rect(screen, fill, rect, border_radius=10)
    pygame.draw.rect(screen, accent if enabled else (78, 80, 94), rect, 2, border_radius=10)
    surf = FONT.render(label, True, (245, 250, 255) if enabled else (125, 130, 145))
    screen.blit(surf, (rect.centerx - surf.get_width() // 2, rect.centery - surf.get_height() // 2))
    return rect

# ------------------------------------------------------------------------------
# TITLE & MENUS
# ------------------------------------------------------------------------------
CASTLE_MENU_IMAGE = None
try:
    img_path = os.path.join(os.path.dirname(__file__), "castle_menu.png")
    if os.path.exists(img_path):
        orig = pygame.image.load(img_path).convert()
        scaled_h = HEIGHT
        scaled_w = int(orig.get_width() * scaled_h / orig.get_height())
        scaled = pygame.transform.smoothscale(orig, (scaled_w, scaled_h))
        left_offset = max(0, (scaled_w - WIDTH) // 2)
        CASTLE_MENU_IMAGE = scaled.subsurface(pygame.Rect(left_offset, 0, WIDTH, HEIGHT)).copy()
except Exception as exc:
    print(f"Notice: castle_menu.png: {exc}")

def draw_castle_menu(mouse):
    if CASTLE_MENU_IMAGE:
        screen.blit(CASTLE_MENU_IMAGE, (0, 0))
    else:
        screen.fill((10, 14, 32))
        centered("SILENT GLITCH", 100, BIG, (88, 235, 245))
        centered("THE OLD HAUNTED CASTLE", 160, FONT, (215, 225, 255))
    start_btn = pygame.Rect(350, 270, 260, 48)
    levels_btn = pygame.Rect(350, 327, 260, 48)
    gifts_btn = pygame.Rect(350, 382, 260, 48)
    settings_btn = pygame.Rect(350, 434, 260, 48)
    exit_btn = pygame.Rect(350, 489, 260, 48)
    return start_btn, gifts_btn, levels_btn, settings_btn, exit_btn

def draw_level_map(mouse):
    screen.fill((9, 13, 32))
    centered("CASTLE LEVEL MAP", 30, BIG, (88, 235, 245))
    centered("Level 1: Ghost Chase (25s) | Level 2: Blackout & Lantern (20s) | Level 3: Dual-Stalker", 80, SMALL, (205, 216, 240))
    pygame.draw.line(screen, (77, 94, 130), (480, 160), (480, 460), 6)
    rects = []
    for i, (x, y) in enumerate([(480, 165), (390, 300), (480, 435)]):
        unlocked = i < unlocked_levels
        rect = pygame.Rect(x - 90, y - 31, 180, 62)
        pygame.draw.circle(screen, (18, 26, 50), (x, y), 48)
        pygame.draw.circle(screen, (83, 229, 229) if unlocked else (90, 92, 110), (x, y), 43, 2)
        pygame.draw.rect(screen, (45, 105, 115) if unlocked else (42, 43, 59), rect, border_radius=12)
        pygame.draw.rect(screen, (255, 197, 87) if unlocked else (88, 92, 109), rect, 2, border_radius=12)
        label = f"LEVEL {i + 1} - OPEN" if unlocked else f"LEVEL {i + 1} - LOCKED"
        surf = SMALL.render(label, True, (245, 250, 255) if unlocked else (145, 148, 160))
        screen.blit(surf, (rect.centerx - surf.get_width() // 2, rect.centery - surf.get_height() // 2))
        rects.append(rect)
    back = draw_button(pygame.Rect(25, 530, 150, 42), "BACK", mouse)
    centered(f"Progress: {unlocked_levels}/3 gates unlocked", 550, SMALL, (185, 202, 230))
    return rects, back

def draw_gifts(mouse):
    screen.fill((10, 12, 31))
    centered("TREASURE BOONS & CHARMS", 38, BIG, (255, 204, 94))
    centered("Choose your boon before stepping into the haunted mansion", 86, FONT, (210, 220, 242))
    cards = [
        (pygame.Rect(75, 190, 240, 225), "HEART CHARM", "3 Hearts Max", "Divine protection against evil"),
        (pygame.Rect(360, 190, 240, 225), "SCORE CHEST", "+50 Points", "A royal head start"),
        (pygame.Rect(645, 190, 240, 225), "SHIELD RUNE", "Phantom Shield", "Absorbs one ghost attack")
    ]
    rects = []
    for rect, title, line1, line2 in cards:
        selected = gift_chosen and gift_name == title
        pygame.draw.rect(screen, (47, 77, 91) if selected else (31, 48, 76), rect, border_radius=15)
        pygame.draw.rect(screen, (255, 205, 94) if selected else (80, 210, 230), rect, 2, border_radius=15)
        cx, cy = rect.centerx, rect.y + 55
        if title == "HEART CHARM":
            pygame.draw.polygon(screen, (105, 255, 220), [(cx, cy - 25), (cx + 20, cy), (cx, cy + 25), (cx - 20, cy)])
        elif title == "SCORE CHEST":
            pygame.draw.rect(screen, (255, 195, 75), (cx - 24, cy - 17, 48, 35), border_radius=5)
            pygame.draw.rect(screen, (111, 67, 29), (cx - 5, cy - 17, 10, 35))
        else:
            pygame.draw.polygon(screen, (180, 135, 255), [(cx, cy - 28), (cx + 25, cy - 14), (cx + 20, cy + 15), (cx, cy + 28), (cx - 20, cy + 15), (cx - 25, cy - 14)])
        surf = SMALL.render(title, True, (245, 248, 255))
        screen.blit(surf, (cx - surf.get_width() // 2, rect.y + 105))
        for j, line in enumerate((line1, line2)):
            surf = SMALL.render(line, True, (255, 220, 135) if j == 0 else (190, 211, 240))
            screen.blit(surf, (cx - surf.get_width() // 2, rect.y + 145 + j * 23))
        rects.append(rect)
    centered("Selected: " + gift_name if gift_chosen else "No gift selected yet", 445, FONT, (125, 255, 203) if gift_chosen else (190, 202, 225))
    back = draw_button(pygame.Rect(25, 520, 150, 42), "BACK", mouse)
    cont = draw_button(pygame.Rect(675, 520, 260, 42), "CONTINUE TO LEVELS", mouse, True, (255, 190, 75))
    return rects, back, cont

# ------------------------------------------------------------------------------
# SILENT GLITCH: THE FINAL REVELATION & ACHIEVEMENTS
# ------------------------------------------------------------------------------
def draw_ending_sequence(mouse_pos, dt, clicked):
    global screen_mode, ending_slide, ending_slide_timer, score, lives, total_crystals_collected
    ending_slide_timer += dt
    screen.fill((8, 6, 16))

    # Atmospheric dark purple void gradient
    for y in range(0, HEIGHT, 4):
        p_fade = int(24 * (1.0 - y / HEIGHT))
        pygame.draw.line(screen, (16 + p_fade, 8 + p_fade // 2, 28 + p_fade), (0, y), (WIDTH, y), 4)

    # Subtle purple glitch scanlines
    rng = random.Random(pygame.time.get_ticks() // 120)
    if ending_slide == 3 or rng.random() < 0.25:
        for _ in range(4):
            gy = rng.randrange(0, HEIGHT)
            gh = rng.randrange(2, 6)
            pygame.draw.rect(screen, (160, 90, 230, 60), (0, gy, WIDTH, gh))

    # Box container
    box_rect = pygame.Rect(110, 55, WIDTH - 220, HEIGHT - 110)
    pygame.draw.rect(screen, (16, 14, 28), box_rect, border_radius=16)
    pygame.draw.rect(screen, (175, 110, 245), box_rect, 2, border_radius=16)

    if ending_slide == 0:
        centered("SILENT GLITCH", 90, BIG, (120, 240, 255))
        centered("— THE FINAL REVELATION —", 145, FONT, (215, 150, 255))
        pygame.draw.line(screen, (65, 45, 95), (180, 190), (WIDTH - 180, 190), 1)

        centered("“The final crystal awakens.”", 235, FONT, (240, 245, 255))
        centered("“The castle falls silent, and the shadow stops following you.”", 285, FONT, (240, 245, 255))
        centered("A soothing blue luminescence washes across the stone corridors...", 345, SMALL, (160, 215, 245))

        btn_next = draw_button(pygame.Rect(HALF_W - 90, 420, 180, 42), "NEXT >>", mouse_pos, True, (185, 120, 255))
        if clicked and btn_next.collidepoint(mouse_pos):
            ending_slide = 1
            SOUNDS.play("click")

    elif ending_slide == 1:
        centered("THE UNFORGOTTEN TRUTH", 100, BIG, (255, 215, 110))
        pygame.draw.line(screen, (65, 45, 95), (180, 165), (WIDTH - 180, 165), 1)

        centered("You finally understand the truth:", 210, FONT, (215, 220, 240))
        centered("“The shadow was never your enemy.”", 265, BIG, (140, 235, 255))
        centered("“It was the part of the castle's lost magic that had been trapped between two worlds.”", 335, FONT, (245, 245, 255))

        btn_next = draw_button(pygame.Rect(HALF_W - 90, 420, 180, 42), "NEXT >>", mouse_pos, True, (185, 120, 255))
        if clicked and btn_next.collidepoint(mouse_pos):
            ending_slide = 2
            SOUNDS.play("click")

    elif ending_slide == 2:
        centered("TWO WORLDS UNITED", 100, BIG, (120, 255, 210))
        pygame.draw.line(screen, (65, 45, 95), (180, 165), (WIDTH - 180, 165), 1)

        centered("“With all crystals restored,”", 215, FONT, (245, 245, 255))
        centered("“the Real World and the Glitch Realm become one again.”", 260, FONT, (130, 240, 255))
        centered("“The doors unlock, the darkness fades, and the castle is finally free.”", 315, FONT, (255, 235, 160))

        btn_next = draw_button(pygame.Rect(HALF_W - 90, 420, 180, 42), "NEXT >>", mouse_pos, True, (120, 255, 210))
        if clicked and btn_next.collidepoint(mouse_pos):
            ending_slide = 3
            SOUNDS.play("click")

    elif ending_slide == 3:
        centered("THE CURSE IS BROKEN.", 130, BIG, (255, 235, 110))
        centered("Or is it?", 205, FONT, (215, 130, 255))
        draw_silent_glitch_overlay(intense=True)
        centered("A tiny purple glitch appears on the screen before the credits roll...", 310, SMALL, (190, 140, 245))

        btn_next = draw_button(pygame.Rect(HALF_W - 120, 420, 240, 42), "VIEW ACHIEVEMENTS", mouse_pos, True, (255, 205, 80))
        if clicked and btn_next.collidepoint(mouse_pos):
            ending_slide = 4
            SOUNDS.play("click")

    elif ending_slide == 4:
        centered("HAUNTED CASTLE SURVIVED!", 75, BIG, (95, 245, 240))
        centered(f"Final Score: {score}  |  Lives Remaining: {lives}  |  Total Crystals Collected: {total_crystals_collected}/24", 125, SMALL, (230, 235, 250))

        achieve_survivor = True
        achieve_guardian = (total_crystals_collected >= 20)
        achieve_master = (lives >= 2 and score >= 200)

        achievements = [
            ("CASTLE SURVIVOR", "Completed all 3 levels of the haunted castle.", achieve_survivor, (255, 215, 85)),
            ("CRYSTAL GUARDIAN", f"Collected {total_crystals_collected}/24 crystals across all levels.", achieve_guardian, (85, 235, 255)),
            ("MASTER OF TWO WORLDS", "Preserved high sanity, lives, and high score.", achieve_master, (195, 120, 255))
        ]

        start_y = 160
        for i, (title, desc, unlocked, badge_col) in enumerate(achievements):
            card_rect = pygame.Rect(140, start_y + i * 80, WIDTH - 280, 68)
            pygame.draw.rect(screen, (22, 20, 38) if unlocked else (18, 18, 26), card_rect, border_radius=10)
            pygame.draw.rect(screen, badge_col if unlocked else (60, 60, 75), card_rect, 2 if unlocked else 1, border_radius=10)

            cx, cy = card_rect.x + 36, card_rect.centery
            if unlocked:
                pygame.draw.circle(screen, badge_col, (cx, cy), 18)
                pygame.draw.circle(screen, (10, 12, 22), (cx, cy), 14)
                badge_lbl = "★" if i == 0 else ("◆" if i == 1 else "✦")
                b_surf = FONT.render(badge_lbl, True, badge_col)
                screen.blit(b_surf, (cx - b_surf.get_width() // 2, cy - b_surf.get_height() // 2))
            else:
                pygame.draw.circle(screen, (50, 50, 65), (cx, cy), 18)
                lock_surf = SMALL.render("X", True, (130, 130, 150))
                screen.blit(lock_surf, (cx - lock_surf.get_width() // 2, cy - lock_surf.get_height() // 2))

            t_col = badge_col if unlocked else (140, 140, 160)
            t_surf = FONT.render(f"{title} {'[UNLOCKED]' if unlocked else '[LOCKED]'}", True, t_col)
            screen.blit(t_surf, (card_rect.x + 72, card_rect.y + 12))

            d_surf = SMALL.render(desc, True, (200, 210, 230) if unlocked else (115, 115, 130))
            screen.blit(d_surf, (card_rect.x + 72, card_rect.y + 38))

        play_btn = draw_button(pygame.Rect(HALF_W - 220, 420, 200, 42), "PLAY AGAIN", mouse_pos, True, (255, 190, 75))
        home_btn = draw_button(pygame.Rect(HALF_W + 20, 420, 200, 42), "CASTLE HOME", mouse_pos)

        if clicked:
            SOUNDS.play("click")
            if play_btn.collidepoint(mouse_pos):
                return "retry"
            elif home_btn.collidepoint(mouse_pos):
                return "home"
    return None

# ------------------------------------------------------------------------------
# MAIN GAME LOOP
# ------------------------------------------------------------------------------
screen_mode = "castle"
unlocked_levels = 1

def run_game():
    global screen_mode, unlocked_levels, level_index, time_left, time_expired
    global grid, doors, crystals, traps, exit_pos, lantern_pos, ghost
    global dimension, health, lives, score, game_over, game_won, message, message_timer
    global trap_cooldown, player_x, player_y, player_angle, gift_name, gift_bonus, gift_shield, gift_chosen
    global level_elapsed, blackout_active, has_lantern, jumpscare_flash
    global bob_offset, walk_timer, step_timer
    global l1_surprise_shown, has_crimson_key, total_crystals_collected, ending_slide, ending_slide_timer

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.04)
        mouse_pos = pygame.mouse.get_pos()
        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if screen_mode == "game":
                        screen_mode = "castle"
                    else:
                        running = False
                elif screen_mode == "game" and not game_over and not game_won:
                    # SILENT GLITCH SHIFT
                    if event.key in (pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT):
                        dimension = 1 - dimension
                        SOUNDS.play("shift")
                        if level_index == 0 and l1_surprise_shown and dimension == 1:
                            message = "A shadow silhouette watches from the doorway... 'Remember who you were.'"
                            message_timer = 4.0
                        else:
                            message = "Silent Glitch triggered! The void whispers..." if dimension else "Reality returns."
                            message_timer = 1.8
                    # DOOR INTERACTION [E]
                    elif event.key == pygame.K_e:
                        for door in doors.values():
                            if math.hypot(player_x - (door.x + 0.5), player_y - (door.y + 0.5)) < 1.7:
                                door.toggle()
                                break
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = True

        # 1. CASTLE MENU
        if screen_mode == "castle":
            start_btn, gifts_btn, levels_btn, settings_btn, exit_btn = draw_castle_menu(mouse_pos)
            if clicked:
                SOUNDS.play("click")
                if start_btn.collidepoint(mouse_pos):
                    screen_mode = "gifts"
                elif gifts_btn.collidepoint(mouse_pos):
                    screen_mode = "gifts"
                elif levels_btn.collidepoint(mouse_pos):
                    screen_mode = "levels"
                elif exit_btn.collidepoint(mouse_pos):
                    running = False
                elif settings_btn.collidepoint(mouse_pos):
                    message = "Collect crystals and beware the ghost in the final 25s!"
                    message_timer = 2.0

        # 2. LEVEL MAP
        elif screen_mode == "levels":
            level_rects, back_btn = draw_level_map(mouse_pos)
            if clicked:
                SOUNDS.play("click")
                if back_btn.collidepoint(mouse_pos):
                    screen_mode = "castle"
                else:
                    for i, rect in enumerate(level_rects):
                        if rect.collidepoint(mouse_pos) and i < unlocked_levels:
                            level_index = i
                            time_left = LEVEL_TIME_LIMITS[level_index]
                            time_expired = False
                            level_elapsed = 0.0
                            blackout_active = False
                            has_lantern = False
                            jumpscare_flash = 0.0
                            bob_offset = 0
                            walk_timer = 0.0
                            step_timer = 0.0
                            grid, doors, crystals, traps, exit_pos, lantern_pos, ghost = load_level(level_index)
                            dimension, health, lives, score = 0, 100, 3, gift_bonus
                            game_won = game_over = False
                            trap_cooldown = 0.0
                            reset_player()
                            has_crimson_key = False
                            # Level 3: Ghost is active from start as Dual Stalker!
                            if level_index == 2:
                                ghost.spawn(player_x, player_y)
                                message = "Level 3: The Crimson Key & The Shadow Stalker! Find the Key in the Crypt!"
                            else:
                                message = f"Level {level_index + 1}: Explore all 8 haunted rooms & collect every crystal!"
                            message_timer = 3.5
                            screen_mode = "game"

        # 3. GIFTS & BOONS
        elif screen_mode == "gifts":
            gift_rects, back_btn, cont_btn = draw_gifts(mouse_pos)
            if clicked:
                SOUNDS.play("click")
                if back_btn.collidepoint(mouse_pos):
                    screen_mode = "castle"
                elif cont_btn.collidepoint(mouse_pos):
                    screen_mode = "levels"
                else:
                    for i, rect in enumerate(gift_rects):
                        if rect.collidepoint(mouse_pos):
                            gift_chosen = True
                            if i == 0:
                                gift_name, gift_bonus, gift_shield = "HEART CHARM", 0, 0
                            elif i == 1:
                                gift_name, gift_bonus, gift_shield = "SCORE CHEST", 50, 0
                            else:
                                gift_name, gift_shield, gift_bonus = "SHIELD RUNE", 1, 0

        # 4. ENDING SEQUENCE (The Final Revelation)
        elif screen_mode == "ending":
            res = draw_ending_sequence(mouse_pos, dt, clicked)
            if res == "retry":
                level_index = 0
                time_left = LEVEL_TIME_LIMITS[0]
                time_expired = False
                level_elapsed = 0.0
                blackout_active = False
                has_lantern = False
                has_crimson_key = False
                jumpscare_flash = 0.0
                bob_offset = 0
                walk_timer = 0.0
                step_timer = 0.0
                grid, doors, crystals, traps, exit_pos, lantern_pos, ghost = load_level(0)
                dimension, health, lives, score = 0, 100, 3, gift_bonus
                total_crystals_collected = 0
                game_over = game_won = False
                reset_player()
                screen_mode = "game"
            elif res == "home":
                screen_mode = "castle"

        # 5. GAMEPLAY
        elif screen_mode == "game":
            for door in doors.values():
                door.update(dt)
                dist_p = math.hypot(player_x - (door.x + 0.5), player_y - (door.y + 0.5))
                if dist_p < 1.15 and door.target_open == 0.0:
                    door.target_open = 1.0
                    SOUNDS.play("door")

            if not game_over and not game_won:
                time_left -= dt
                level_elapsed += dt

                # LEVEL 2: 20-SECOND BLACKOUT TRIGGER
                if level_index == 1 and level_elapsed >= 20.0 and not blackout_active and not has_lantern:
                    blackout_active = True
                    SOUNDS.play("thunder")
                    message = "LIGHTS OUT! PITCH BLACKNESS FALLS! FIND THE LANTERN!"
                    message_timer = 3.5

                # LEVEL 1 & 2: GHOST SPAWNS AT FINAL 25 SECONDS!
                if time_left <= 25.0 and not ghost.active:
                    ghost.spawn(player_x, player_y)
                    message = "THE BANSHEE HAS AWOKEN! IT IS HUNTING YOU!"
                    message_timer = 3.0

                # UPDATE GHOST
                if ghost.active:
                    hit_player = ghost.update(dt, player_x, player_y, level_index + 1, dimension)
                    if hit_player:
                        if gift_shield > 0:
                            gift_shield -= 1
                            message = "Phantom shield shattered, saving your life!"
                            message_timer = 2.0
                        else:
                            health -= 35
                            jumpscare_flash = 1.0
                            message = "The Banshee struck you! -35 HP"
                            message_timer = 2.0
                        if health <= 0:
                            lives -= 1
                            if lives <= 0:
                                game_over = True
                            else:
                                health = 100
                                reset_player()
                                ghost.spawn(player_x, player_y)

                if time_left <= 0:
                    time_left = 0
                    game_over = True
                    time_expired = True

                keys = pygame.key.get_pressed()
                if keys[pygame.K_a]:
                    player_angle -= TURN_SPEED * dt
                if keys[pygame.K_d]:
                    player_angle += TURN_SPEED * dt

                forward = (1 if keys[pygame.K_w] else 0) - (1 if keys[pygame.K_s] else 0)
                strafe = (1 if keys[pygame.K_e] else 0) - (1 if keys[pygame.K_q] else 0)
                dx = (math.cos(player_angle) * forward - math.sin(player_angle) * strafe) * MOVE_SPEED * dt
                dy = (math.sin(player_angle) * forward + math.cos(player_angle) * strafe) * MOVE_SPEED * dt

                is_moving = (forward != 0 or strafe != 0)
                if is_moving:
                    walk_timer += dt * 10.0
                    step_timer += dt
                    bob_offset = int(math.sin(walk_timer) * 3)
                    if step_timer >= 0.42:
                        step_timer = 0.0
                        SOUNDS.play("step")
                else:
                    bob_offset = int(bob_offset * 0.7) if abs(bob_offset) > 0 else 0

                if can_move(player_x + dx, player_y):
                    player_x += dx
                if can_move(player_x, player_y + dy):
                    player_y += dy

                # Crystal Pickup
                for crys in crystals:
                    if crys["active"] and math.hypot(player_x - crys["x"], player_y - crys["y"]) < 0.52:
                        crys["active"] = False
                        score += 15
                        total_crystals_collected += 1
                        SOUNDS.play("crystal")
                        room_name = ROOM_INFO[crys["room_id"]]["name"]
                        active_left = sum(1 for c in crystals if c["active"])
                        if level_index == 0 and active_left == 4 and not l1_surprise_shown:
                            l1_surprise_shown = True
                            message = "“You are not alone in this castle...”"
                            message_timer = 5.0
                            SOUNDS.play("shift")
                        else:
                            message = f"{crys['name']} collected from {room_name}! +15 pts"
                            message_timer = 2.2

                # Level 2: Eternal Flame Lantern Pickup
                if level_index == 1 and not has_lantern:
                    if math.hypot(player_x - lantern_pos[0], player_y - lantern_pos[1]) < 0.6:
                        has_lantern = True
                        blackout_active = False
                        SOUNDS.play("lantern")
                        message = "Lantern acquired! Hidden script on wall: 'The castle is not evil... it is trapped like you.'"
                        message_timer = 4.5

                # Level 3: Crimson Key Pickup
                if level_index == 2 and not has_crimson_key:
                    if math.hypot(player_x - crimson_key_pos[0], player_y - crimson_key_pos[1]) < 0.6:
                        has_crimson_key = True
                        score += 30
                        SOUNDS.play("win")
                        message = "CRIMSON KEY CLAIMED! The sealed sanctuary portal unlocks!"
                        message_timer = 4.0

                # Damage Traps
                trap_cooldown = max(0.0, trap_cooldown - dt)
                if trap_cooldown <= 0.0:
                    for tx, ty in traps:
                        if math.hypot(player_x - tx, player_y - ty) < 0.45:
                            health -= 25
                            SOUNDS.play("trap")
                            message = "Glitch trap! Lost 25 HP."
                            message_timer = 2.0
                            trap_cooldown = 1.2
                            if health <= 0:
                                lives -= 1
                                if lives <= 0:
                                    game_over = True
                                else:
                                    health = 100
                                    reset_player()
                            break

                # Exit Portal
                if math.hypot(player_x - exit_pos[0], player_y - exit_pos[1]) < 0.7:
                    all_collected = all(not c["active"] for c in crystals)
                    if level_index == 2:
                        if not has_crimson_key:
                            message = "Sanctuary sealed! You must find the CRIMSON KEY in the crypt!"
                            message_timer = 2.5
                        elif not all_collected:
                            message = "Portal sealed! Find all 8 room crystals first."
                            message_timer = 2.0
                        else:
                            SOUNDS.play("win")
                            unlocked_levels = 3
                            screen_mode = "ending"
                            ending_slide = 0
                            ending_slide_timer = 0.0
                    else:
                        if all_collected:
                            SOUNDS.play("win")
                            unlocked_levels = max(unlocked_levels, min(3, level_index + 2))
                            screen_mode = "levels"
                        else:
                            message = "Portal sealed! Find all 8 room crystals first."
                            message_timer = 1.5

                message_timer = max(0.0, message_timer - dt)
                draw_world()

                # Psychological "Silent Glitch" effect or panic timer warnings
                if dimension == 1 or time_left <= 25:
                    draw_silent_glitch_overlay(intense=(time_left <= 10 or ghost.active))

            else:
                screen.fill((8, 8, 20))
                if time_expired:
                    draw_silent_glitch_overlay(intense=True)
                title = "HAUNTED CASTLE SURVIVED!" if game_won else ("REALITY COLLAPSED" if time_expired else "GAME OVER")
                subtitle = f"Time expired! Final Score: {score} | Level {level_index + 1}" if time_expired else f"Final Score: {score} | Level {level_index + 1}"
                centered(title, 205, BIG, (95, 245, 240) if game_won else (255, 75, 95))
                centered(subtitle, 270, FONT, (235, 235, 255))
                retry_btn = draw_button(pygame.Rect(335, 335, 290, 45), "PLAY AGAIN", mouse_pos, True, (255, 190, 75))
                map_btn = draw_button(pygame.Rect(335, 395, 290, 45), "LEVEL MAP", mouse_pos)
                home_btn = draw_button(pygame.Rect(335, 455, 290, 45), "CASTLE HOME", mouse_pos)

                if clicked:
                    SOUNDS.play("click")
                    if retry_btn.collidepoint(mouse_pos):
                        level_index = 0
                        time_left = LEVEL_TIME_LIMITS[0]
                        time_expired = False
                        level_elapsed = 0.0
                        blackout_active = False
                        has_lantern = False
                        jumpscare_flash = 0.0
                        bob_offset = 0
                        walk_timer = 0.0
                        step_timer = 0.0
                        grid, doors, crystals, traps, exit_pos, lantern_pos, ghost = load_level(0)
                        dimension, health, lives, score = 0, 100, 3, gift_bonus
                        has_crimson_key = False
                        total_crystals_collected = 0
                        game_over = game_won = False
                        reset_player()
                        screen_mode = "game"
                    elif map_btn.collidepoint(mouse_pos):
                        screen_mode = "levels"
                    elif home_btn.collidepoint(mouse_pos):
                        screen_mode = "castle"

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_game()
