# No More Genre Radio Show Builder

Leverage ffmpeg to compile a bunch of audio files into an entire radio show. 

## Software Status / Version

Currently a proof of concept. It works well enough to get done what I need done, but could be improved, tested, possibly refactored.

## Table of Contents

- [Background](#background)
- [Usage](#usage)
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

After months of using Ableton to edit together our radio shows, I (DJ Nate Da Great) decided to automate the process and save myself some time.

This software maintains a library of mixes and a show format. It allows me to choose mixes from our library of mixes to compile the show. it uses the ffmpeg library to combine all the necessary IDs and mixes into a complete show.

## Usage

More details to follow

```sh
$ python buildshow.py [show date]
```

## Maintainers

[@djnatedagreat](https://github.com/djnatedagreat).


## License

[MIT](LICENSE) © DJ Nate Da Great