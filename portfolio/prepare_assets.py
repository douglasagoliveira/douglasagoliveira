import pymupdf
from PIL import Image
doc = pymupdf.open('../Portfolio Douglas de Oliveira.pdf')
names = {
 54:'cover_portrait', 39:'bg_screens', 130:'rtt_mosaic',
 137:'vovo_1', 140:'vovo_2', 143:'vovo_3', 149:'vovo_logo',
 167:'amb_1', 170:'amb_2', 173:'amb_3', 179:'amb_logo',
 185:'qtm_1', 188:'qtm_2', 191:'qtm_3', 197:'quantum_logo',
 206:'id_vovo', 212:'id_florenza', 218:'id_carolina', 224:'id_ambiental', 230:'id_cleaning', 236:'id_wes',
 253:'web_1', 259:'web_2', 262:'web_3', 265:'web_4',

}
smasks = {54:52,22:20,149:147,179:177,197:195,206:204,212:210,218:216,224:222,230:228,236:234,253:251,259:257}
for xref, name in names.items():
    pix = pymupdf.Pixmap(doc, xref)
    if pix.colorspace is None or pix.n not in (3,4):
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    if pix.alpha: pix = pymupdf.Pixmap(pix, 0)  # drop alpha to RGB
    if xref in smasks:
        m = pymupdf.Pixmap(doc, smasks[xref])
        pix = pymupdf.Pixmap(pix, m)
        out = f'assets/{name}.png'
    else:
        out = f'assets/{name}.jpg' if pix.n == 3 else f'assets/{name}.png'
    if out.endswith('.jpg'):
        pix.save(out, jpg_quality=92)
    else:
        pix.save(out)
    print(name, pix.width, pix.height, pix.n, pix.alpha, out)
