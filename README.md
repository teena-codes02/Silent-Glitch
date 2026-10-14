# 🌌 SILENT GLITCH: THE SHADOW IS YOU
### *Haunted Castle Edition — Narrative & Psychological Horror Update*

A retro pseudo-3D raycaster survival-horror game built with Pygame. Explore eight haunted gothic chambers, shift between the Real World and the Silent Glitch dimension, collect crystals, survive the castle's threats, and uncover the mystery of the shadow.

## 📖 Story: The Shadow Is You

You awaken inside an ancient, fractured Gothic castle haunted by a stalking silhouette. As you explore its rooms and gather lost crystals, the castle's reality begins to unravel—and the connection between you and the shadow becomes clearer.

## 🏚️ Levels and Key Events

### Level 1: Something Is Watching You
- Collect crystals and explore the castle.
- Collecting four crystals triggers a warning that you are not alone.
- Shift into the Silent Glitch dimension with **SPACE** or **SHIFT** to reveal a shadow silhouette and discover a clue.

### Level 2: The Castle Is Changing
- A sudden blackout begins after 20 seconds of level time if the lantern has not been found.
- Low remaining time makes the situation more urgent.
- Find the **Eternal Flame Lantern** to illuminate the castle and reveal its ancient message.

### Level 3: The Crimson Key and the Shadow
- The stalker can be seen in the Silent Glitch dimension.
- Find the **Crimson Key** hidden in the crypt to unlock the exit.
- Gather the crystals and escape to trigger the final revelation.

## 🎬 Final Revelation

After escaping Level 3, the game presents a narrative ending about the shadow, the castle's lost magic, and the joining of the Real World and the Glitch Realm. A final purple glitch appears before the achievement screen.

## 🏆 Achievements

- **CASTLE SURVIVOR** — Complete all three levels.
- **CRYSTAL GUARDIAN** — Collect all 24 crystals across the levels.
- **MASTER OF TWO WORLDS** — Finish with a score of at least 200 points and lives remaining.

## 🎮 Controls

| Key | Action |
|---|---|
| **W / S** | Move forward / backward |
| **A / D** | Turn left / right |
| **Q / E** | Strafe left / right |
| **E** | Open / close a nearby Gothic door |
| **SPACE / SHIFT** | Switch between the Real World and Glitch dimension |
| **ESC** | Return to the castle menu / pause |

**Note:** The game uses **E** for both right strafing and nearby-door interaction. When you are close to a door, pressing **E** may activate the door interaction.

## 🚀 How to Run

### Option 1: Windows batch file

Double-click `run_game.bat`.

### Option 2: Command line

From the project folder, run:

```cmd
py -3.13 main.py
```

If that command is not available, try:

```cmd
python main.py
```

Install the required packages first:

```cmd
pip install -r requirements.txt
```

## 📁 Project Files

- `main.py` — main Pygame game implementation.
- `main.py.bak` — backup copy of the main script, if included.
- `castle_menu.png` — castle menu image asset.
- `requirements.txt` — Python package requirements.
- `run_game.bat` — Windows launch helper.
- `README.md` — project story, controls, and run instructions.

## 🤝 Team Contribution Note

Team members should commit their own changes to their assigned Git branches and open a pull request for the team leader to review. Coordinate before editing the same file, especially `main.py`, to reduce merge conflicts.
