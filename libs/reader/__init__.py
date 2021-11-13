from itertools import zip_longest
from libs.db_sqlite import SqliteDatabase
import libs.fingerprint as fingerprint

class BaseReader(object):
  def __init__(self, a):
    self.a = a
    self.db = SqliteDatabase()

  def recognize(self):
    self.process_recording()
    data = self.get_recorded_data()
    #db = SqliteDatabase()
    matches = []
    for channel in data:
        matches.extend(self.find_matches(channel))
    if len(matches) > 0:
        detection = self.align_matches(matches)            
        return detection
    else:
        return False

  def grouper(self, iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return [filter(None, values) for values in zip_longest(fillvalue=fillvalue, *args)]

  def find_matches(self, samples, Fs=fingerprint.DEFAULT_FS):
    hashes = fingerprint.fingerprint(samples, Fs=Fs)
    mapper = {}
    for hash, offset in hashes:
      mapper[hash.upper()] = offset
    values = mapper.keys()

    for split_values in self.grouper(values, 1000):
      # @todo move to db related files
      split_values = list(split_values)
      query = """
        SELECT upper(hash), song_fk, offset
        FROM fingerprints
        WHERE upper(hash) IN (%s)
      """
      query = query % ', '.join('?' * len(split_values))

      x = self.db.executeAll(query, split_values)
      matches_found = len(x)

      if matches_found > 0:
        # matches found
        pass
      else:
        # no matches found
        pass

      for hash, sid, offset in x:
        # (sid, db_offset - song_sampled_offset)
        offset = int.from_bytes(offset, 'little')
        yield (sid, offset - mapper[hash])

  def align_matches(self, matches):
    diff_counter = {}
    largest = 0
    largest_count = 0
    song_id = -1

    for tup in matches:
      sid, diff = tup

      if diff not in diff_counter:
        diff_counter[diff] = {}

      if sid not in diff_counter[diff]:
        diff_counter[diff][sid] = 0

      diff_counter[diff][sid] += 1

      if diff_counter[diff][sid] > largest_count:
        largest = diff
        largest_count = diff_counter[diff][sid]
        song_id = sid

    songM = self.db.get_song_by_id(song_id)

    nseconds = round(float(largest) / fingerprint.DEFAULT_FS *
                     fingerprint.DEFAULT_WINDOW_SIZE *
                     fingerprint.DEFAULT_OVERLAP_RATIO, 5)

    return {
        "SONG_ID" : song_id,
        "SONG_NAME" : songM[1],
        "CONFIDENCE" : largest_count,
        "OFFSET" : int(largest),
        "OFFSET_SECS" : nseconds
    }
