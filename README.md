# No More Genre Radio Show Builder

CLI for managing audio assets and compiling these assets into full radio shows with ffmpeg.

## Software Status / Version

Currently a proof of concept. It works well enough to get done what I need done, but could be improved, tested, possibly refactored.

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

*BAX
*DJ Nate Da Great
*Poetik Selektions
*Jonesy
*DJ Ayo
*Intel Hayesfield
*and guests

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

An audio clip is a segment of an audio asset as defined in seconds. All clips have a start and end time that are defined in seconds from the beginning of the clip. Most audio assets will have a clip representing the entire duration of the asset. But, it's also possible to create a clip that is only part of an audio asset. For example, You might have a DJ mix that is 60 Minutes long, but you can also specifify a secondary clip of that mix that is just 30 Minutes long.

### Program

A program defines the format of a show. It defines the show segments, the length of each segment and if that segment is prefilled with particular clips. For example, the No More Genre radio show is 3 hours long. Each hour of music is preceeded by a station ID. All shows must have a program associated with them. This provides the necessary timing parameters for filling the show with music and mixes. See nomoregenre_program.json as an example.

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

## Usage

### Manage Creators

#### Add Creator

`$ python creator.py add`

#### Remove Creator

`$ python creator.py rm`

#### Rename Creator

`$ python creator.py rename`

#### List All Creators

`$ python creator.py list`

### Manage Asset Types

#### Add Asset Type

`$ python asset_type.py add`

#### Remove Asset Type

`$ python asset_type.py rm`

#### List Asset Types

`$ python asset_type.py list`

### Manage Audio Assets

#### Add Audio Asset

`$ python audio_asset.py add`

#### List AUdio Assets

`$ python audio_asset.py list`

### Manage Audio Clips

#### Add Audio Asset

`$ python audio_clip.py add`

#### List Audio Assets

`$ python audio_clip.py list`

#### Replace Audio Clip

`$ python audio_clip.py replace`

### Manage Shows

#### Add a New Show

`$ python show.py add`

#### View (Show) a Show's Details

`$ python show.py show --id=[show_id]`

#### Fill a show with Audio Clips

`$ python show.py fill --id=[show_id]`

#### Build the show .... Compile it into a single mp3 file

`$ python show.py build --id=[show_id]`

#### List all Shows

`$ python show.py list`

```sh
$ python show.py [show date]
```

## Road Map / TO DO

* Add Description fields to Audio Assets
* options for fading between clips.
* smarter ways of choosing clips


## Maintainers

[@djnatedagreat](https://github.com/djnatedagreat).


## License

[MIT](LICENSE) © DJ Nate Da Great