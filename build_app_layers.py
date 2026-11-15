import json, re, sys
import numpy as np, rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling, transform_bounds
from PIL import Image
SRC, OUT = sys.argv[1], sys.argv[2]

def warp(path, resampling, scale=1.0, dst_nodata=np.nan, dtype='float32'):
    with rasterio.open(path) as r:
        t, w, h = calculate_default_transform(r.crs, 'EPSG:3857', r.width, r.height, *r.bounds)
        if scale != 1.0:
            w2, h2 = int(w * scale), int(h * scale)
            t = t * t.scale(w / w2, h / h2); w, h = w2, h2
        dst = np.full((h, w), dst_nodata, dtype=dtype)
        reproject(r.read(1), dst, src_transform=r.transform, src_crs=r.crs, src_nodata=r.nodata,
                  dst_transform=t, dst_crs='EPSG:3857', dst_nodata=dst_nodata, resampling=resampling)
        b3857 = rasterio.transform.array_bounds(h, w, t)
        b = transform_bounds('EPSG:3857', 'EPSG:4326', *b3857)
    return dst, b

import os
def change_png(tif, png):
    d, b = warp(tif, Resampling.bilinear)
    rgba = np.zeros(d.shape + (4,), dtype=np.uint8)
    mag = np.clip((np.abs(d) - 2.0) / 4.0, 0, 1)            # 2 dB -> faint, 6 dB -> solid
    up, dn = (d >= 2.0), (d <= -2.0)
    rgba[up] = (30, 160, 230, 0); rgba[dn] = (220, 45, 45, 0)
    a = (110 + 145 * mag).astype(np.uint8); rgba[..., 3] = np.where(up | dn, a, 0)
    Image.fromarray(rgba).save(OUT + '/data/' + png, optimize=True)
    return b

import csv
# dates and per-date areas come from the notebook CSVs, so the app always matches the run
ev = list(csv.DictReader(open(SRC + '/cambio_por_fecha.csv', encoding='utf-8-sig')))
dk = {r['fecha']: float(r['area_muy_oscura_km2']) for r in csv.DictReader(open(SRC + '/area_muy_oscura_por_fecha_PROVISORIO.csv', encoding='utf-8-sig'))}
dates = [r['fecha'] for r in ev]
series = [{'date': r['fecha'], 'up': float(r['se_aclaro_km2']), 'down': float(r['se_oscurecio_km2']), 'dark': dk.get(r['fecha'], 0.0)} for r in ev]
# change raster of each date against the first one (exported by the notebook as cambio_HH_dB_YYYY-MM-DD.tif).
# If a date is missing, only the last date is available (cambio_HH_dB.tif = last vs first).
b = change_png(SRC + '/cambio_HH_dB.tif', 'change_jun_oct.png')
change_files = {dates[-1]: 'change_jun_oct.png'}
for dt in dates[1:]:
    f = SRC + '/cambio_HH_dB_%s.tif' % dt
    if os.path.exists(f):
        change_png(f, 'change_%s.png' % dt); change_files[dt] = 'change_%s.png' % dt
bounds = [[b[1], b[0]], [b[3], b[2]]]

# persistent change: 1 = signal up, 2 = signal down, in the same direction in at least 3 of the 4 later dates (> 1.5 dB)
has_persistent = os.path.exists(SRC + '/cambio_persistente.tif')
if has_persistent:
    p, _ = warp(SRC + '/cambio_persistente.tif', Resampling.nearest, dst_nodata=0, dtype='uint8')
    im = np.zeros(p.shape + (4,), dtype=np.uint8); im[p == 1] = (30, 160, 230, 235); im[p == 2] = (220, 45, 45, 235)
    Image.fromarray(im).save(OUT + '/data/persistent.png', optimize=True)
for dt in dates:
    m, _ = warp(SRC + '/muy_oscuro_PROVISORIO_%s.tif' % dt, Resampling.nearest, dst_nodata=255, dtype='uint8')
    im = np.zeros(m.shape + (4,), dtype=np.uint8); im[m == 1] = (255, 200, 0, 235)
    Image.fromarray(im).save(OUT + '/data/verydark_%s.png' % dt, optimize=True)

comp = {'N': 'N', 'S': 'S', 'E': 'E', 'O': 'W'}
def loc(s):
    m = re.match(r'([\d.]+) km al (\w+) del centro del salar', s)
    return '%s km %s of the salar centre' % (m.group(1), ''.join(comp[c] for c in m.group(2))) if m else s
PONDS = {11, 27, 32, 41}
g = json.load(open(SRC + '/zonas_de_cambio.geojson', encoding='utf-8'))
for f in g['features']:
    p = f['properties']
    f['properties'] = {'id': p['zona'], 'dir': 'brightened' if 'acl' in p['tipo'] else 'darkened', 'area': p['area_km2'],
                       'db': p['cambio_medio_dB'], 'loc': loc(p['ubicacion']),
                       'cls': 'Evaporation ponds (checked with Sentinel-2)' if p['zona'] in PONDS else 'Not classified'}
    f['geometry']['coordinates'] = [[[round(x, 5), round(y, 5)] for x, y in ring] for ring in f['geometry']['coordinates']]
sites = [{'name': 'Evaporation pond sector', 'lat': -25.427, 'lon': -66.883, 'note': 'Step change between 4 July and 21 August 2026. Sentinel-2 shows the ponds already existed in June.'},
         {'name': 'Los Patos wetland (vega)', 'lat': -25.343, 'lon': -66.954, 'note': 'Almost no persistent change (0.3 km²).'},
         {'name': 'Wetland, southwest sector', 'lat': -25.473, 'lon': -67.082, 'note': '2.4 km² with a persistent decrease nearby. Cause not determined by radar alone.'}]
open(OUT + '/data/data.js', 'w', encoding='utf-8').write(
    'window.SALAR=' + json.dumps({'bounds': bounds, 'dates': dates, 'series': series, 'sites': sites, 'zones': g, 'change': change_files, 'persistent': has_persistent}, ensure_ascii=False, separators=(',', ':')) + ';')
print(bounds, len(g['features']), 'change dates:', sorted(change_files), 'persistent:', has_persistent)
