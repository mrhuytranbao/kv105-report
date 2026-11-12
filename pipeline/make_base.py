"""Sang tháng mới: tạo base.json cho daily.html từ file Tracking (sheet MM.YYYY) + DN đầu kỳ BI.
Dùng: python3 make_base.py Tracking.xlsx 2026-12 dk.json > base.json
  dk.json = {"BTE20001": 10640, ...}  (DN đầu kỳ tháng mới theo BI, triệu đồng)
  KHM 2W/4W tháng trước lấy từ data.html (Data thô năm, cột GNN_KHM_2W/4W) nếu có; thiếu thì để null.
Layout sheet Tracking (giữ như T11): B5:B19 tên PGD; F Net MT; L GNN MT; Q KHM SL MT; X %RFW dự báo; AD Rút T-1 (tr);
 AG %Rút T-1; AH %Rút dự báo; dòng 26-40: C GN KHM MT, G KHM2, K KHM4, O VL2, S VL4, W TU2, AA TU4."""
import sys, json, calendar, warnings, openpyxl
warnings.filterwarnings('ignore')
TR, MON, DKF = sys.argv[1], sys.argv[2], sys.argv[3]
y, m = int(MON[:4]), int(MON[5:])
ws = openpyxl.load_workbook(TR, data_only=True)[f'{m:02d}.{y}']
col = lambda c, r0, r1: [ws[f'{c}{r}'].value for r in range(r0, r1 + 1)]
num = lambda v: float(v) if isinstance(v, (int, float)) else None
names = [n for n in col('B', 5, 25) if n and '.' in str(n) and str(n)[:3] in ('BTE', 'VLG')]
n = len(names); codes = [x.split('.')[0] for x in names]
SH = {'BTE20001': '363A', 'BTE21004': '17A1', 'BTE22008': 'TTCL', 'VLG20001': 'N3CV', 'VLG20002': '64/6', 'VLG20003': '148 TNV',
      'VLG21004': 'TCDB', 'VLG21005': '8D DTH', 'VLG22006': 'TTTB', 'VLG22007': 'VXTA', 'VLG24008': 'KCNHP', 'VLG25009': 'N4LH',
      'VLG26010': 'TTVL', 'VLG26011': 'PTQ', 'VLG26012': 'TTMC', 'VLG26013': 'TTCN'}
e1, e2 = 4 + n, 25 + n
MT = dict(net=[num(v) for v in col('F', 5, e1)], gnn=[num(v) for v in col('L', 5, e1)], khm_sl=[num(v) for v in col('Q', 5, e1)],
          rfw_db=[num(v) for v in col('X', 5, e1)], rut_t1=[num(v) for v in col('AD', 5, e1)], rutp_t1=[num(v) for v in col('AG', 5, e1)],
          rut_db=[num(v) for v in col('AH', 5, e1)], khm=[num(v) for v in col('C', 26, e2)], khm2=[num(v) for v in col('G', 26, e2)],
          khm4=[num(v) for v in col('K', 26, e2)], vl2=[num(v) for v in col('O', 26, e2)], vl4=[num(v) for v in col('S', 26, e2)],
          tu2=[num(v) for v in col('W', 26, e2)], tu4=[num(v) for v in col('AA', 26, e2)])
dk = json.load(open(DKF))
pm = f'{y}-{m-1:02d}' if m > 1 else f'{y-1}-12'
t1 = {}
try:
    s = open('data.html', encoding='utf-8').read(); i = s.index('const D=') + 8
    D = json.JSONDecoder().raw_decode(s[i:])[0]; ks = [c['k'] for c in D['cols']]
    for r in D['rows']:
        if r[0] == pm: t1[r[1]] = (r[ks.index('GNN_KHM_2W')], r[ks.index('GNN_KHM_4W')])
except Exception as ex: print('warn t1x', ex, file=sys.stderr)
out = dict(mon=MON, ndays=calendar.monthrange(y, m)[1], codes=codes, names=names, short=[SH.get(c, c) for c in codes],
           dk=[dk.get(c) for c in codes], mt=MT, t1x=dict(khm2=[t1.get(c, (None, None))[0] for c in codes], khm4=[t1.get(c, (None, None))[1] for c in codes]))
print(json.dumps(out, ensure_ascii=False))
