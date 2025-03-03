# PokéDataToolkit

PokéDataToolkit is a Python toolkit for creating, injecting, and reading Pokémon PKM data files used in Generation 8 Pokémon games. It provides a set of utilities to generate a valid PKM file from custom inputs, send binary data to a device via a network socket, and parse existing PKM files to extract meaningful Pokémon data.

## Features

- **PKM File Creation:**  
  Generate a 344-byte Pokémon data file using custom parameters (species, trainer ID, IVs, EVs, moves, etc.). The toolkit packs the data into the correct binary format and calculates necessary checksums.

- **Network Injection:**  
  Send a "poke" command over TCP to inject the generated PKM data into a target device's memory. This is useful for debugging or testing in environments where data injection is supported.

- **PKM File Parsing:**  
  Read and parse existing PKM files, extracting key information such as species, held items, experience, moves, IVs, EVs, trainer names, and battle stats.

## Files

- **create_data.py:**  
  Contains the function `create_species_file()` to generate a binary PKM file based on user-specified parameters, along with a Tkinter GUI to facilitate user input.

- **poke_data.py:**  
  Demonstrates how to send a "poke" command over a TCP socket to inject PKM data into a target device's memory.

- **read_data.py:**  
  Provides functions to read a PKM file from disk and parse its binary content into a human-readable dictionary.

- **cfg.py:**  
  Contains configuration dictionaries (e.g., species, items, nature, abilities, and attacks) used by the toolkit for both file creation and parsing.

## Requirements

- Python 3.x
- Standard Python libraries (`socket`, `struct`, `tkinter`, etc.)
