"""parquet (.nakama-0) -> web/data/<Map>.json + web/minimaps/<Map>.jpg
Usage: python pipeline/build_data.py <player_data_dir>
Uses pyarrow if installed, else the bundled miniparquet reader."""
import json, os, re, sys
from collections import defaultdict
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))

# map_id: (scale, origin_x, origin_z) -- from the dataset README
CFG = {'AmbroseValley': (900, -370, -473), 'GrandRift': (581, -290, -290), 'Lockdown': (1000, -500, -500)}
CODE = {'Kill': 'K', 'Killed': 'D', 'BotKill': 'BK', 'BotKilled': 'BD', 'KilledByStorm': 'S', 'Loot': 'L'}
MOVE = {'Position', 'BotPosition'}

def read(path):
    try:
        import pyarrow.parquet as pq
        t = pq.read_table(path).to_pydict()
    except ImportError:
        import miniparquet; t = miniparquet.read(path)
    dec = lambda v: v.decode() if isinstance(v, bytes) else v
    return {k: [dec(x) for x in v] for k, v in t.items()}

def to_px(map_id, x, z):
    s, ox, oz = CFG[map_id]                      # world (x,z) -> UV -> pixel; y (elevation) ignored
    return round((x - ox) / s * 1024, 1), round((1 - (z - oz) / s) * 1024, 1)

def main(root):
    maps = {m: defaultdict(lambda: {'players': []}) for m in CFG}
    for day in sorted(d for d in os.listdir(root) if d.startswith('February_')):
        for f in os.listdir(os.path.join(root, day)):
            if f.startswith('.'): continue
            try: c = read(os.path.join(root, day, f))
            except Exception as e: print('skip', day, f, e); continue
            if not c.get('ts'): continue
            uid, mid, mp = c['user_id'][0], c['match_id'][0].replace('.nakama-0', ''), c['map_id'][0]
            rows = sorted(zip(c['ts'], c['x'], c['z'], c['event']))
            m = maps[mp][mid]; m['day'] = int(day.split('_')[1])
            m.setdefault('t0', rows[0][0]); m['t0'] = min(m['t0'], rows[0][0])
            p = {'u': uid, 'b': bool(re.fullmatch(r'\d+', uid)), 'raw': rows}   # bot = numeric id (README)
            m['players'].append(p)
    for mp, ms in maps.items():
        out = []
        for mid, m in ms.items():
            t0 = m['t0']; players = []
            for p in m['players']:
                path, ev = [], []
                for ts, x, z, e in p['raw']:
                    px, py = to_px(mp, x, z); t = int(ts - t0)   # ts is epoch *seconds* despite README saying ms
                    if e in MOVE: path.append([t, px, py])
                    elif e in CODE: ev.append([t, px, py, CODE[e]])
                players.append({'u': p['u'][:8], 'b': p['b'], 'p': path, 'e': ev})
            dur = max((r[0] for p in players for r in p['p'] + p['e']), default=0)
            out.append({'id': mid[:8], 'day': m['day'], 'dur': dur, 'players': players})
        out.sort(key=lambda m: (m['day'], m['id']))
        json.dump({'map': mp, 'matches': out}, open(f'web/data/{mp}.json', 'w'), separators=(',', ':'))
        print(mp, len(out), 'matches', os.path.getsize(f'web/data/{mp}.json') // 1024, 'KB')
    for mp in CFG:                                   # 1024px JPEGs keep the page light (Lockdown source is 11 MB)
        src = [f for f in os.listdir(os.path.join(root, 'minimaps')) if f.startswith(mp)][0]
        Image.open(os.path.join(root, 'minimaps', src)).convert('RGB').resize((1024, 1024)).save(f'web/minimaps/{mp}.jpg', quality=85)

if __name__ == '__main__': main(sys.argv[1])
