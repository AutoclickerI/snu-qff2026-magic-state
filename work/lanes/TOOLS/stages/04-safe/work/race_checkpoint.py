"""Atomic, locked per-variant snapshots. Only complete chunks are durable.

Each save fsyncs a new file, atomically replaces the old snapshot, then fsyncs
the directory. A killed write leaves the previous complete snapshot usable.
"""
import fcntl
import json
import os
from pathlib import Path
import tempfile
from race_identity import digest


class Journal:
    def __init__(self, path, header):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.lock = open(str(self.path)+'.lock','a')
        fcntl.flock(self.lock,fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.obj = dict(header=header,chunks=[],state='active',prior=dict(totals=[],kepts=[]))
        if self.path.exists():
            obj = self.read(self.path)
            if obj['header'] != header:
                self.close()
                raise ValueError('checkpoint identity mismatch')
            self.obj = obj
        self.write_seconds = 0.0

    @staticmethod
    def read(path):
        obj = json.loads(Path(path).read_text())
        checksum = obj.pop('sha256')
        if digest(obj) != checksum:
            raise ValueError('checkpoint checksum mismatch')
        for i, row in enumerate(obj['chunks']):
            if row['index'] != i or row['seed'] != i:
                raise ValueError('non-contiguous chunk sequence or seed mismatch')
        return obj

    def save(self):
        import time
        start = time.perf_counter()
        payload = dict(self.obj,sha256=digest(self.obj))
        fd, name = tempfile.mkstemp(prefix=self.path.name+'.',suffix='.tmp',dir=self.path.parent)
        try:
            with os.fdopen(fd,'w') as f:
                json.dump(payload,f,separators=(',',':'))
                f.write('\n'); f.flush(); os.fsync(f.fileno())
            os.replace(name,self.path)
            fd = os.open(self.path.parent,os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
        finally:
            if os.path.exists(name):
                os.unlink(name)
        self.write_seconds += time.perf_counter()-start

    def append(self, values, totals, kepts):
        i = len(self.obj['chunks'])
        a,b,s,s2 = values
        self.obj['chunks'].append(dict(index=i,seed=i,kept=int(a),corrected=int(b),
                                      loss=float(s).hex(),loss_sq=float(s2).hex()))
        self.obj['prior'] = dict(totals=[float(t).hex() for t in totals[-1024:]],kepts=kepts[-1024:])
        self.save()

    def state(self, value):
        self.obj['state'] = value
        self.save()

    def values(self):
        return [(r['kept'],r['corrected'],float.fromhex(r['loss']),float.fromhex(r['loss_sq']))
                for r in self.obj['chunks']]

    def close(self):
        self.lock.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def replay(values):
    kept = corrected = 0
    total = total_sq = 0.0
    for a,b,s,s2 in values:  # the judge's sequential accumulation, never sum(partial sums)
        kept += a; corrected += b; total += s; total_sq += s2
    return kept,corrected,total,total_sq
