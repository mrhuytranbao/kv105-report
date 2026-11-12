"""Cập nhật daily.html (KV105) — dữ liệu nằm sẵn trong daily.html giữa 2 marker /*D0*/ ... /*D1*/.
Dùng:
  python3 update_daily.py show            # in JSON ngày cuối (làm mẫu cho ngày mới) + base (codes, names, mt...)
  python3 update_daily.py add day.json    # thêm/ghi đè 1 ngày (theo 'date'), ghi lại daily.html
  python3 update_daily.py base base.json  # sang tháng mới: thay mon/ndays/dk/mt/t1x..., xoá các ngày cũ
  python3 update_daily.py check day.json  # đối chiếu tổng PGD với tổng KV trong file ngày
Chạy trong thư mục gốc repo (cạnh daily.html)."""
import json, sys, re
F = 'daily.html'
def load():
    s = open(F, encoding='utf-8').read()
    a, b = s.index('/*D0*/') + 6, s.index('/*D1*/')
    return s, a, b, json.loads(s[a:b])
def save(s, a, b, d):
    s = s[:a] + json.dumps(d, ensure_ascii=False, separators=(',', ':')) + s[b:]
    open(F, 'w', encoding='utf-8').write(s)
cmd = sys.argv[1]
s, a, b, d = load()
if cmd == 'show':
    base = {k: v for k, v in d.items() if k != 'days'}
    print('BASE', json.dumps({k: base[k] for k in ('mon', 'ndays', 'codes', 'short')}, ensure_ascii=False))
    print('DAYS', [x['date'] for x in d['days']])
    print('LAST', json.dumps(d['days'][-1], ensure_ascii=False))
elif cmd == 'add':
    day = json.load(open(sys.argv[2], encoding='utf-8'))
    assert day['date'][:7] == d['mon'], 'Ngày không thuộc tháng hiện hành của daily.html -> chạy base trước'
    for g in ('net', 'gnn', 'khm'):
        assert len(day[g]['th']) == len(d['codes']), f'{g}.th phải có {len(d["codes"])} PGD theo thứ tự codes'
    d['days'] = sorted([x for x in d['days'] if x['date'] != day['date']] + [day], key=lambda x: x['date'])
    save(s, a, b, d); print('OK days =', [x['date'] for x in d['days']])
elif cmd == 'base':
    nb = json.load(open(sys.argv[2], encoding='utf-8'))
    nb['days'] = [x for x in d['days'] if x['date'][:7] == nb['mon']]
    save(s, a, b, nb); print('OK base', nb['mon'])
elif cmd == 'check':
    day = json.load(open(sys.argv[2], encoding='utf-8'))
    for g, f in [('net', 'th'), ('gnn', 'th'), ('khm', 'th'), ('khmsl', 'th')]:
        print(g, f, 'sum PGD =', round(sum(v or 0 for v in day[g][f]), 1))
    print('rfw amt_th sum =', sum(v or 0 for v in day['rfw']['amt_th']), '| KV', day['rfw']['kv'].get('amt_th'))
