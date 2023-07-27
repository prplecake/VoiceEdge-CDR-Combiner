# VoiceEdge CDR Combiner

Compiles CDR CSVs into a SQLite database.

## Usage

Run `extract_and_compine.py`, this will:

* Create the SQLite database and table(s),
* Extract the CSV files from ZIP archives in the current directory,
* Reads CSV files and inserts records into database,
* Moves extracted-from ZIPs and processed CSVs to `processed/` dir.
