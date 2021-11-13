from libs.reader import BaseReader
from pydub import AudioSegment
from pydub.utils import audioop
import numpy as np
from hashlib import sha1
import os

class FileReader(BaseReader):
  def __init__(self, filename):
    super(FileReader, self).__init__(filename)
    self.filename = filename

  def process_recording(self):
    songname, extension = os.path.splitext(os.path.basename(self.filename))

    try:
      audiofile = AudioSegment.from_file(self.filename)

      data = np.fromstring(audiofile._data, np.int16)

      self.channels = []
      for chn in range(audiofile.channels):
        self.channels.append(data[chn::audiofile.channels])

      self.fs = audiofile.frame_rate

    except audioop.error:
      print('audioop.error')

    return {
      "songname": songname,
      "extension": extension,
      "channels": self.channels,
      "Fs": audiofile.frame_rate,
      "file_hash": self.parse_file_hash()
    }

  def get_recorded_data(self):
    return self.channels

  def parse_file_hash(self, blocksize=2**20):
    s = sha1()
    with open(self.filename , "rb") as f:
      while True:
        buf = f.read(blocksize)
        if not buf: break
        s.update(buf)

    return s.hexdigest().upper()
