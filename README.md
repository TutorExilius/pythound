# PyThound

An async sound library for python.

Created in a twitch live session https://twitch.tv/TutorExilius

## Used FFPLAY version:

``` 
ffplay version 4.3.1-2021-01-26-essentials_build-www.gyan.dev Copyright (c) 2003-2021 the FFmpeg developers
  built with gcc 10.2.0 (Rev6, Built by MSYS2 project)
  configuration: --enable-gpl --enable-version3 --enable-static --disable-w32threads --disable-autodetect --enable-fontconfig --enable-iconv --enable-gnutls --enable-libxml2 --enable-gmp --enable-lzma --enable-zlib --enable-libsrt --en
able-libssh --enable-libzmq --enable-avisynth --enable-sdl2 --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxvid --enable-libaom --enable-libopenjpeg --enable-libvpx --enable-libass --enable-libfreetype --enable-libfribi
di --enable-libvidstab --enable-libvmaf --enable-libzimg --enable-amf --enable-cuda-llvm --enable-cuvid --enable-ffnvcodec --enable-nvdec --enable-nvenc --enable-d3d11va --enable-dxva2 --enable-libmfx --enable-libgme --enable-libopenmp
t --enable-libopencore-amrwb --enable-libmp3lame --enable-libtheora --enable-libvo-amrwbenc --enable-libgsm --enable-libopencore-amrnb --enable-libopus --enable-libspeex --enable-libvorbis --enable-librubberband
  libavutil      56. 51.100 / 56. 51.100
  libavcodec     58. 91.100 / 58. 91.100
  libavformat    58. 45.100 / 58. 45.100
  libavdevice    58. 10.100 / 58. 10.100
  libavfilter     7. 85.100 /  7. 85.100
  libswscale      5.  7.100 /  5.  7.100
  libswresample   3.  7.100 /  3.  7.100
  libpostproc    55.  7.100 / 55.  7.100
```

## Installation:
### 1. Install ffmpeg:

#### Windows:
1. Download https://ffmpeg.org/download.html#build-windows
2. Add ffmpeg-binaries in SYSPATH, if not done


#### Linux:
1. sudo apt install ffmpeg (Debian)
2. Add ffmpeg-binaries in SYSPATH, if not done

### 2. Python Dependencies:

#### via poetry
1. pip install poetry
2. in project path: ```poetry install```

#### OR via manual way:
1. pip install psutil


Enjoy! :)



