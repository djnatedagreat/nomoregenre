# No More Genre Radio Show Builder

CLI for managing audio assets and compiling these assets into full radio shows with ffmpeg.

## Software Status / Version

Alpha Status. Works great for my personal needs. Could use some work on streamlining the installation process.

## Table of Contents

- [Background](#background)
- [Concepts](#concepts)
- [Installation](#installation)
- [Usage](#usage)
- [Road Map](#roadmap)
- [Maintainers](#maintainers)
- [License](#license)

## Background

The No More Genre radio show airs weekly on Sanctuary Radio (https://www.mediasanctuary.org/initiatives/sanctuary-radio/), which is managed by The Sanctuary for Independent Media in Troy, New York.

The No More Genre Show features DJ mixes composed by the No More Genre DJs:

* BAX
* DJ Nate Da Great
* Poetik Selektions
* Jonesy
* DJ Ayo
* Intel Hayesfield
* and guests

After months of using Ableton to edit together our weekly 3-hour radio shows, I (DJ Nate Da Great) decided to automate the process and save some time.

This software allows me to manage a library of audio assets such as mixes and radio IDs and fully compiled shows. It allows me to define the format of a radio show and fill it in with audio clips from the library. It uses ffmpeg choose mixes from our library to compile the show. it uses the ffmpeg to compile all of the selected clips into a show.

## Concepts

### Creator

A Creator is someone who creates content. In the case of No More Genre, most creators are DJs who submit curated DJ mixes.

### Audio Assets

An Audio Asset is simply an audio file. We mostly use mp3 formatted audio files. These files might be DJ mixes, songs, full shows, other recordings, Station and Show IDs, etc... See Asset Types

### Asset Types

A classification for types of audio assets. This could be a mix or a song or a station identification.

### Audio Clips

An audio clip is a segment of an audio asset as defined in seconds. All clips have a start and end time that are defined in seconds from the beginning of the clip. All audio assets will have a clip representing the entire duration of the asset. But, it's also possible to create a clip that is only part of an audio asset. For example, You might have a DJ mix that is 60 Minutes long, but you can also specifify a secondary clip of that mix that is just 30 Minutes long.

### Program

A program defines the format of a show. It defines the show segments, the length of each segment and if that segment is prefilled with particular clips. For example, the No More Genre radio show is 3 hours long. Each hour of music is preceeded by a station ID. All shows must have a program associated with them. This provides the necessary timing parameters for filling the show with music and mixes. See nomoregenre_program.json as an example.

TODO: document program file structure.

### Shows

A show represents the full radio show. A Show is a combination of audio assets that are "strung together" to fill the show. For example, you might have an hour long show, and to fill that hour, you might string together a bunch of songs, IDS, bumpers and sweepers to fill that time. 

## Installation / Getting Started

More detail to be added. There are some database migration scripts, but could use a rewrite and some documentation. In short:

1. Get your Python virtual env in order
2. Install the pip requirements (I'm new to python and might need to include some file that defines those requirements. Like in javascript there's a package.json. I don't know if there's an equivalent in python. This is a "TODO")
3. Run the database migration scripts
4. create a directory to store your audio assets
5. set variables in .env file

Next...

6. add some creators and define your asset types
7. start adding audio assets and defining clips
8. define a show format / program in a .json file (See... nomoregenre_program.json)
9. start creating some shows

## CLI Usage

### Manage Creators

#### Add Creator

`$ python nmg.py c add creator_name`

#### Remove Creator

`$ python nmg.py c rm creator_name`

#### Rename Creator

`$ python nmg.py c rename old_name new_name`

#### List All Creators

`$ python nmg.py c list`

### Manage Asset Types

#### Add Asset Type

`$ python nmg.py at add asset_type_name`

#### Remove Asset Type

`$ python nmg.py at rm asset_type_name`

#### List Asset Types

`$ python nmg.py at list`


### Manage Audio Assets

#### Add Audio Asset

`$ python nmg.py a add --file path_to_audio_file.mp3 --name="Unique Asset name" --by="creator_name" --when=2025-04-11`

Note that the argument "a" can be substituted for any asset type, eg. mix, id, song, etc... and the asset type will be set appropriately

`$ python nmg.py mix add --file path_to_audio_file.mp3 --name="Unique Asset name" --by="creator_name" --when=2025-04-11`

#### List Audio Assets

`$ python nmg.py a list [--by="creator_name"]`

Replace a with an asset type, eg. mix, etc... and only that asset type will be listed

`$ python nmg.py mix list [--by="creator_name"]`

#### Preview Audio Asset

`$ python nmg.py a preview asset_id`

Replacing "a" with asset type is allowed, but it doesn't change the behavior

`$ python nmg.py mix preview asset_id`

#### View/Show Audio Asset

`$ python nmg.py a show asset_id`

Replacing "a" with asset type is allowed, but it doesn't change the behavior

`$ python nmg.py mix show asset_id`

#### Tag an Audio Asset

`$ python nmg.py a tag asset_id tag_name`

Tags are freeform strings and will be created automatically if they don't exist. Use any asset type alias in place of "a".

`$ python nmg.py mix tag asset_id early`

To remove a tag:

`$ python nmg.py mix tag asset_id tag_name --remove`

### Manage Audio Clips

#### Add Audio Clip

$ python nmg.py mix clip asset_id start end`

start and end are formatted as hh:mm:ss.000

#### List Audio Clip

`$ python audio_clip.py list`

#### Replace Audio Clip

`$ python audio_clip.py replace`

### Manage Shows

#### Add a New Show

`$ python nmg.py show add air_date --program program_file.json`

#### List All Shows

`$ python nmg.py show list`

#### View a Show's Details

`$ python nmg.py show show show_id`

#### Fill a Show Interactively

`$ python nmg.py show fill show_id`

#### List Candidates for the Next Unfilled Segment

`$ python nmg.py show fill show_id --candidates`

Prints a table of available clips for the next unfilled segment, including type, creator, duration, submission date, last air date, use count, and tags. Useful for non-interactively reviewing options before pushing clips.

#### Push a Clip to a Show

`$ python nmg.py show push show_id clip_id`

Appends a clip to the next unfilled segment. Raises an error if the clip is too long to fit within the segment's remaining max duration.

#### Pop the Last Clip from a Show

`$ python nmg.py show pop show_id`

Removes the most recently added clip from a show. Useful for undoing a push.

#### Build a Show (Compile to MP3)

`$ python nmg.py show build show_id`

#### Clear All Clips from a Show

`$ python nmg.py show clear show_id`

## Road Map / TO DO

* options for fading between clips.
* smarter ways of choosing clips


## Maintainers

[@djnatedagreat](https://github.com/djnatedagreat).


## License

[MIT](LICENSE) © DJ Nate Da Great