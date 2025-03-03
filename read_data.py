import struct

# Reads the entire binary file and returns its content.
def read_species_file(file_path):
    with open(file_path, "rb") as f:
        return f.read()

# Parses a 344-byte Pokémon data file into a dictionary.
def parse_species(data):
    parsed_data = {}
    
    # Basic identifiers and trainer IDs.
    parsed_data["EncryptionConstant"] = struct.unpack_from("<I", data, 0x00)[0]
    parsed_data["Sanity"] = struct.unpack_from("<H", data, 0x04)[0]
    parsed_data["Checksum"] = struct.unpack_from("<H", data, 0x06)[0]
    parsed_data["Species"] = struct.unpack_from("<H", data, 0x08)[0]
    parsed_data["HeldItem"] = struct.unpack_from("<H", data, 0x0A)[0]
    parsed_data["TID"] = struct.unpack_from("<H", data, 0x0C)[0]
    parsed_data["SID"] = struct.unpack_from("<H", data, 0x0E)[0]
    parsed_data["ID32"] = struct.unpack_from("<I", data, 0x0C)[0]
    
    # Experience and ability data.
    parsed_data["EXP"] = struct.unpack_from("<I", data, 0x10)[0]
    parsed_data["Ability"] = struct.unpack_from("<H", data, 0x14)[0]
    parsed_data["AbilityNumber"] = data[0x16] & 7
    parsed_data["CanGigantamax"] = (data[0x16] & 16) != 0

    # PID, nature, gender, and form.
    parsed_data["PID"] = struct.unpack_from("<I", data, 0x1C)[0]
    parsed_data["Nature"] = data[0x20]
    parsed_data["StatNature"] = data[0x21]
    parsed_data["Gender"] = (data[0x22] >> 2) & 0x3
    parsed_data["Form"] = data[0x24]

    # Effort Values (EVs) for six stats.
    for offset, key in zip([0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B],
                             ["EV_HP", "EV_ATK", "EV_DEF", "EV_SPE", "EV_SPA", "EV_SPD"]):
        parsed_data[key] = data[offset]

    # Individual Values (IVs) packed in a 32-bit integer.
    iv32 = struct.unpack_from("<I", data, 0x8C)[0]
    parsed_data["IV_HP"] = (iv32 >> 0) & 0x1F
    parsed_data["IV_ATK"] = (iv32 >> 5) & 0x1F
    parsed_data["IV_DEF"] = (iv32 >> 10) & 0x1F
    parsed_data["IV_SPE"] = (iv32 >> 15) & 0x1F
    parsed_data["IV_SPA"] = (iv32 >> 20) & 0x1F
    parsed_data["IV_SPD"] = (iv32 >> 25) & 0x1F
    parsed_data["IsEgg"] = (iv32 >> 30) & 1
    parsed_data["IsNicknamed"] = (iv32 >> 31) & 1

    # Moves (4 slots) and their PP values.
    for offset, key in zip([0x72, 0x74, 0x76, 0x78],
                             ["Move1", "Move2", "Move3", "Move4"]):
        parsed_data[key] = struct.unpack_from("<H", data, offset)[0]
    for offset, key in zip([0x7A, 0x7B, 0x7C, 0x7D],
                             ["Move1_PP", "Move2_PP", "Move3_PP", "Move4_PP"]):
        parsed_data[key] = data[offset]

    # Trainer names (12-byte UTF-8 strings, null-padded).
    parsed_data["Nickname"] = data[0x58:0x58+12].decode("utf-8", errors="ignore").strip("\x00")
    parsed_data["OriginalTrainerName"] = data[0xF8:0xF8+12].decode("utf-8", errors="ignore").strip("\x00")
    parsed_data["HandlingTrainerName"] = data[0xA8:0xA8+12].decode("utf-8", errors="ignore").strip("\x00")

    # Additional trainer info.
    parsed_data["OriginalTrainerGender"] = (data[0x125] >> 7)
    parsed_data["MetLevel"] = data[0x125] & ~0x80
    parsed_data["EggLocation"] = struct.unpack_from("<H", data, 0x120)[0]
    parsed_data["MetLocation"] = struct.unpack_from("<H", data, 0x122)[0]
    parsed_data["Ball"] = data[0x124]

    # Battle stats.
    parsed_data["Level"] = data[0x148]
    parsed_data["Stat_HPMax"] = struct.unpack_from("<H", data, 0x14A)[0]
    parsed_data["Stat_ATK"] = struct.unpack_from("<H", data, 0x14C)[0]
    parsed_data["Stat_DEF"] = struct.unpack_from("<H", data, 0x14E)[0]
    parsed_data["Stat_SPE"] = struct.unpack_from("<H", data, 0x150)[0]
    parsed_data["Stat_SPA"] = struct.unpack_from("<H", data, 0x152)[0]
    parsed_data["Stat_SPD"] = struct.unpack_from("<H", data, 0x154)[0]

    return parsed_data

# Read binary data from "input" and parse it.
file_path = "input"
species_data = read_species_file(file_path)
parsed_species = parse_species(species_data)

# Print all parsed fields.
for key, value in parsed_species.items():
    print(f"{key}: {value}")