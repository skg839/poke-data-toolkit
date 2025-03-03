import struct              # Used for packing values into a binary buffer
import tkinter as tk       # Tkinter for the GUI
from tkinter import ttk, messagebox  # For themed widgets and message dialogs
import cfg                 # Import configuration dictionaries (species, items, nature, ability, attacks)

# ------------------------------------------------------------------------------
# Function: create_species_file
# ------------------------------------------------------------------------------
# This function creates a 344-byte binary file for a Pokémon (Gen 8 Stored PKM format).
# It takes an output file path and various parameters as keyword arguments.
# Default values are provided for parameters not explicitly passed.
# It uses the 'struct' module to pack values into the binary buffer.
def create_species_file(output_path, **kwargs):
    # Create a byte array of size 344 bytes (the required size for the PKM file)
    data = bytearray(344)
    
    # Define default parameters for the Pokémon data
    defaults = {
        "Species": 25,
        "HeldItem": 0,
        "TID": 12345,
        "SID": 54321,
        "EXP": 1000,
        "Ability": 0,
        "PID": 0x12345678,
        "Nature": 15,
        "Gender": 0,
        "Form": 0,
        "MetLevel": 5,
        "MetLocation": 30,
        "EggLocation": 0,
        "Ball": 4,
        "Nickname": "Pikachu",
        "OriginalTrainerName": "Ash",
        "Level": 5,
        "IVs": [31, 31, 31, 31, 31, 31],
        "EVs": [0, 0, 0, 0, 0, 0],
        "Moves": [5, 5, 5, 5],
        "Language": 5
    }
    # Merge defaults with any values provided by the user (user values override defaults)
    for key, value in defaults.items():
        kwargs.setdefault(key, value)
    
    # ------------------------------------------------------------------------------
    # Pack the basic data into the buffer using little-endian formats:
    # ------------------------------------------------------------------------------
    struct.pack_into("<I", data, 0x00, 0)               # Encryption constant (set to 0)
    struct.pack_into("<H", data, 0x04, 0)               # Sanity check placeholder (0)
    struct.pack_into("<H", data, 0x06, 0)               # Checksum placeholder (will be calculated later)
    struct.pack_into("<H", data, 0x08, kwargs["Species"])  # Species value (lookup from cfg.species)
    struct.pack_into("<H", data, 0x0A, kwargs["HeldItem"]) # Held item value (lookup from cfg.items)
    struct.pack_into("<H", data, 0x0C, kwargs["TID"])      # Trainer ID (TID)
    struct.pack_into("<H", data, 0x0E, kwargs["SID"])      # Secret ID (SID)
    struct.pack_into("<I", data, 0x10, kwargs["EXP"])      # Experience points
    struct.pack_into("<H", data, 0x14, kwargs["Ability"])  # Ability value (lookup from cfg.ability)
    struct.pack_into("<I", data, 0x1C, kwargs["PID"])      # Pokémon ID (PID)
    struct.pack_into("<H", data, 0xE2, kwargs["Language"]) # Language value
    data[0x20] = kwargs["Nature"]                         # Nature (1 byte)
    data[0x22] = (kwargs["Gender"] << 2)                  # Gender stored in shifted bits (0, 1, or 2)
    data[0x24] = kwargs["Form"]                           # Form value

    # ------------------------------------------------------------------------------
    # Pack EVs (Effort Values) for 6 stats; each stored as a single byte
    # ------------------------------------------------------------------------------
    for i, ev in enumerate(kwargs["EVs"]):
        data[0x26 + i] = ev

    # ------------------------------------------------------------------------------
    # Pack IVs (Individual Values) into a single 32-bit integer (each IV uses 5 bits)
    # ------------------------------------------------------------------------------
    iv_value = (kwargs["IVs"][0] << 0) | (kwargs["IVs"][1] << 5) | (kwargs["IVs"][2] << 10) | \
               (kwargs["IVs"][3] << 15) | (kwargs["IVs"][4] << 20) | (kwargs["IVs"][5] << 25)
    struct.pack_into("<I", data, 0x8C, iv_value)

    # ------------------------------------------------------------------------------
    # Pack Moves into 4 slots (each move is stored as an unsigned short)
    # ------------------------------------------------------------------------------
    for i, move in enumerate(kwargs["Moves"]):
        struct.pack_into("<H", data, 0x72 + i * 2, move)

    # ------------------------------------------------------------------------------
    # Pack Nickname: Encode as UTF-8, limit to 12 characters and pad with null bytes
    # ------------------------------------------------------------------------------
    encoded_nickname = kwargs["Nickname"].encode("utf-8")[:12].ljust(12, b'\x00')
    data[0x58:0x58 + 12] = encoded_nickname

    # ------------------------------------------------------------------------------
    # Pack Original Trainer Name: Similar to Nickname, use max 12 chars and pad with null bytes
    # ------------------------------------------------------------------------------
    encoded_ot_name = kwargs["OriginalTrainerName"].encode("utf-8")[:12].ljust(12, b'\x00')
    data[0xF8:0xF8 + 12] = encoded_ot_name

    # ------------------------------------------------------------------------------
    # Pack additional metadata: Egg Location, Met Location, Ball used, and Met Level
    # ------------------------------------------------------------------------------
    struct.pack_into("<H", data, 0x120, kwargs["EggLocation"])
    struct.pack_into("<H", data, 0x122, kwargs["MetLocation"])
    data[0x124] = kwargs["Ball"]
    data[0x125] = kwargs["MetLevel"]

    # ------------------------------------------------------------------------------
    # Pack Level (current level of the Pokémon)
    # ------------------------------------------------------------------------------
    data[0x148] = kwargs["Level"]

    # ------------------------------------------------------------------------------
    # Calculate checksum over a portion of the data and store it at offset 0x06.
    # ------------------------------------------------------------------------------
    checksum = sum(struct.unpack_from("<" + "H" * ((len(data) - 8) // 2), data, 8)) & 0xFFFF
    struct.pack_into("<H", data, 0x06, checksum)

    # ------------------------------------------------------------------------------
    # Write the binary data to the output file.
    # ------------------------------------------------------------------------------
    with open(output_path, "wb") as f:
        f.write(data)
    print(f"Successfully created {output_path}!")

# ------------------------------------------------------------------------------
# Function: generate_file
# ------------------------------------------------------------------------------
# This is the callback function for the GUI "Generate File" button.
# It collects data from all input fields and dropdown menus, converts them
# to the appropriate data types, and then calls create_species_file() with
# these parameters.
def generate_file():
    try:
        # Retrieve and convert GUI values:
        species_name = species_var.get()
        species_value = cfg.species[species_name]  # Look up species number

        # For held item, abilities, etc., the dropdowns display "key: value" strings.
        held_item_value = held_items_map.get(held_item_var.get(), 0)
        tid = int(tid_entry.get())
        sid = int(sid_entry.get())
        exp = int(exp_entry.get())
        ability_value = ability_map.get(ability_var.get(), 0)
        pid_str = pid_entry.get()
        pid = int(pid_str, 16) if pid_str.lower().startswith("0x") else int(pid_str)
        nature_value = nature_map.get(nature_var.get(), 15)
        gender_value = int(gender_var.get())
        form = int(form_entry.get())
        met_level = int(met_level_entry.get())
        met_location = int(met_location_entry.get())
        egg_location = int(egg_location_entry.get())
        ball_value = ball_map.get(ball_var.get(), 4)
        nickname = nickname_entry.get()
        ot_name = ot_entry.get()
        level = int(level_entry.get())
        # Expect IVs and EVs as comma-separated strings; convert them to integer lists.
        ivs = [int(x.strip()) for x in ivs_entry.get().split(',')]
        evs = [int(x.strip()) for x in evs_entry.get().split(',')]
        # For moves, retrieve the move number for each dropdown.
        move_values = [moves_map.get(var.get(), 5) for var in move_vars]
        language = int(language_entry.get())
        output_path = output_entry.get()

        # Call the file creation function with all gathered parameters.
        create_species_file(
            output_path,
            Species=species_value,
            HeldItem=held_item_value,
            TID=tid,
            SID=sid,
            EXP=exp,
            Ability=ability_value,
            PID=pid,
            Nature=nature_value,
            Gender=gender_value,
            Form=form,
            MetLevel=met_level,
            MetLocation=met_location,
            EggLocation=egg_location,
            Ball=ball_value,
            Nickname=nickname,
            OriginalTrainerName=ot_name,
            Level=level,
            IVs=ivs,
            EVs=evs,
            Moves=move_values,
            Language=language
        )
        # Inform the user of success
        messagebox.showinfo("Success", f"File created: {output_path}")
    except Exception as e:
        # Show an error message if something goes wrong
        messagebox.showerror("Error", str(e))

# ------------------------------------------------------------------------------
# Set up the Tkinter GUI
# ------------------------------------------------------------------------------
root = tk.Tk()
root.title("PKM Creator")  # Window title

# Create a frame with padding to hold all the widgets
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
row = 0  # Initialize a row counter for widget placement

# --- Output Filename ---
ttk.Label(frame, text="Output Filename:").grid(row=row, column=0, sticky=tk.W)
output_entry = ttk.Entry(frame)
output_entry.insert(0, "output")  # Default filename
output_entry.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- Species Dropdown ---
ttk.Label(frame, text="Species:").grid(row=row, column=0, sticky=tk.W)
species_var = tk.StringVar()
species_options = sorted(cfg.species.keys())
species_var.set("Pikachu")  # Default species
species_menu = ttk.OptionMenu(frame, species_var, species_var.get(), *species_options)
species_menu.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- Held Item Dropdown ---
ttk.Label(frame, text="Held Item:").grid(row=row, column=0, sticky=tk.W)
held_item_var = tk.StringVar()
held_items_map = {}   # Dictionary to map the displayed option string to the actual item key
held_item_options = []
# Populate options from cfg.items
for key, name in cfg.items.items():
    option = f"{key}: {name}"
    held_items_map[option] = key
    held_item_options.append(option)
held_item_var.set(f"0: {cfg.items[0]}")  # Default held item ("Nothing")
held_item_menu = ttk.OptionMenu(frame, held_item_var, held_item_var.get(), *sorted(held_item_options, key=lambda s: int(s.split(":")[0])))
held_item_menu.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- TID (Trainer ID) ---
ttk.Label(frame, text="TID:").grid(row=row, column=0, sticky=tk.W)
tid_entry = ttk.Entry(frame)
tid_entry.insert(0, "12345")
tid_entry.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- SID (Secret ID) ---
ttk.Label(frame, text="SID:").grid(row=row, column=0, sticky=tk.W)
sid_entry = ttk.Entry(frame)
sid_entry.insert(0, "54321")
sid_entry.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- EXP (Experience Points) ---
ttk.Label(frame, text="EXP:").grid(row=row, column=0, sticky=tk.W)
exp_entry = ttk.Entry(frame)
exp_entry.insert(0, "1000")
exp_entry.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- Ability Dropdown ---
ttk.Label(frame, text="Ability:").grid(row=row, column=0, sticky=tk.W)
ability_var = tk.StringVar()
ability_map = {}  # Maps displayed string to ability key
ability_options = []
ability_options.append("0: None")  # Include a "None" option
ability_map["0: None"] = 0
for key, name in cfg.ability.items():
    option = f"{key}: {name}"
    ability_map[option] = key
    ability_options.append(option)
ability_var.set("0: None")
ability_menu = ttk.OptionMenu(frame, ability_var, ability_var.get(), *sorted(ability_options, key=lambda s: int(s.split(":")[0])))
ability_menu.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- PID (Pokémon ID) ---
ttk.Label(frame, text="PID (hex or int):").grid(row=row, column=0, sticky=tk.W)
pid_entry = ttk.Entry(frame)
pid_entry.insert(0, "0x12345678")
pid_entry.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- Nature Dropdown ---
ttk.Label(frame, text="Nature:").grid(row=row, column=0, sticky=tk.W)
nature_var = tk.StringVar()
nature_map = {}
nature_options = []
for key, name in cfg.nature.items():
    option = f"{key}: {name}"
    nature_map[option] = key
    nature_options.append(option)
nature_var.set("15: Modest")
nature_menu = ttk.OptionMenu(frame, nature_var, nature_var.get(), *sorted(nature_options, key=lambda s: int(s.split(":")[0])))
nature_menu.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- Gender Dropdown ---
ttk.Label(frame, text="Gender (0=Male, 1=Female, 2=Genderless):").grid(row=row, column=0, sticky=tk.W)
gender_var = tk.StringVar()
gender_var.set("0")
gender_menu = ttk.OptionMenu(frame, gender_var, gender_var.get(), "0", "1", "2")
gender_menu.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- Form ---
ttk.Label(frame, text="Form:").grid(row=row, column=0, sticky=tk.W)
form_entry = ttk.Entry(frame)
form_entry.insert(0, "0")
form_entry.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- Met Level ---
ttk.Label(frame, text="Met Level:").grid(row=row, column=0, sticky=tk.W)
met_level_entry = ttk.Entry(frame)
met_level_entry.insert(0, "5")
met_level_entry.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- Met Location ---
ttk.Label(frame, text="Met Location:").grid(row=row, column=0, sticky=tk.W)
met_location_entry = ttk.Entry(frame)
met_location_entry.insert(0, "30")
met_location_entry.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- Egg Location ---
ttk.Label(frame, text="Egg Location:").grid(row=row, column=0, sticky=tk.W)
egg_location_entry = ttk.Entry(frame)
egg_location_entry.insert(0, "0")
egg_location_entry.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- Ball Dropdown (Filtered from cfg.items for items containing "Ball") ---
ttk.Label(frame, text="Ball:").grid(row=row, column=0, sticky=tk.W)
ball_var = tk.StringVar()
ball_map = {}  # Map displayed string to the ball key
ball_options = []
# Only include items with the substring "Ball"
for key, name in cfg.items.items():
    if "Ball" in name:
        option = f"{key}: {name}"
        ball_map[option] = key
        ball_options.append(option)
ball_var.set("4: Poke Ball")
ball_menu = ttk.OptionMenu(frame, ball_var, ball_var.get(), *sorted(ball_options, key=lambda s: int(s.split(":")[0])))
ball_menu.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- Nickname ---
ttk.Label(frame, text="Nickname:").grid(row=row, column=0, sticky=tk.W)
nickname_entry = ttk.Entry(frame)
nickname_entry.insert(0, "Pikachu")
nickname_entry.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- Original Trainer Name ---
ttk.Label(frame, text="Original Trainer Name:").grid(row=row, column=0, sticky=tk.W)
ot_entry = ttk.Entry(frame)
ot_entry.insert(0, "Ash")
ot_entry.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- Level ---
ttk.Label(frame, text="Level:").grid(row=row, column=0, sticky=tk.W)
level_entry = ttk.Entry(frame)
level_entry.insert(0, "5")
level_entry.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- IVs (comma-separated list for 6 stats) ---
ttk.Label(frame, text="IVs (comma-separated 6 values):").grid(row=row, column=0, sticky=tk.W)
ivs_entry = ttk.Entry(frame)
ivs_entry.insert(0, "31,31,31,31,31,31")
ivs_entry.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- EVs (comma-separated list for 6 stats) ---
ttk.Label(frame, text="EVs (comma-separated 6 values):").grid(row=row, column=0, sticky=tk.W)
evs_entry = ttk.Entry(frame)
evs_entry.insert(0, "0,0,0,0,0,0")
evs_entry.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- Moves (4 dropdown menus for moves from cfg.attacks) ---
ttk.Label(frame, text="Moves:").grid(row=row, column=0, sticky=tk.W)
move_vars = []      # List to hold the StringVar for each move dropdown
moves_map = {}      # Map displayed string to move number
move_options = []   # List of move options
# Populate move options from cfg.attacks
for key, name in cfg.attacks.items():
    option = f"{key}: {name}"
    moves_map[option] = key
    move_options.append(option)
# Create 4 move dropdowns, one per move slot
for i in range(4):
    var = tk.StringVar()
    var.set("5: Mega Punch")  # Default move (match default in create_species_file)
    move_menu = ttk.OptionMenu(frame, var, var.get(), *sorted(move_options, key=lambda s: int(s.split(":")[0])))
    move_menu.grid(row=row, column=1, sticky=(tk.W, tk.E))
    move_vars.append(var)
    row += 1

# --- Language ---
ttk.Label(frame, text="Language:").grid(row=row, column=0, sticky=tk.W)
language_entry = ttk.Entry(frame)
language_entry.insert(0, "5")
language_entry.grid(row=row, column=1, sticky=(tk.W, tk.E))
row += 1

# --- Generate File Button ---
# When clicked, this button calls the generate_file() function.
generate_button = ttk.Button(frame, text="Generate File", command=generate_file)
generate_button.grid(row=row, column=0, columnspan=2, pady=10)

# Start the Tkinter event loop
root.mainloop()
