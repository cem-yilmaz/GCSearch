This is the core of the project where all the programs and data necessary for GCSearch to work are stored. The backend server runs a Flask server which calls functions from this directory.

# Directories
## General
### `export/`
This is where **you place your exported data** from the GC platforms. We currently support Instagram, WhatsApp, WeChat, and LINE. Each platform has its own subdirectory in `export/` where you should place the exported data.
### `export_parsers/`
This is where the export->data parsers are stored; each platform has its own parser.
### `out/`
This is where the export data is stored after it has been parsed. The data is split into `info/` and `chatlogs/` subdirectories, containing a `.info.csv` and `.chatlog.csv` file respectively for each chat.
### `piis/`
This is where the Positional Inverted Indexes (PIIs) for each chat are stored. These are all stored within the same subdirectory to allow searching across multiple chats.
### `tokenisers/`
This is where the tokenising functions for each language are stored. We currently support English, Chinese (Simplified), and Chinese (Traditional). (*Todo: Efe add the Turkish tokeniser here*)
## Platform Specific
### `raw_messages/`
(*Instagram only*) This is where we store the raw message data from Instagram. This can be deleted if images are not being stored as is (either deleted or OCR'd into text), but is mandatory if you wish to view the images.
