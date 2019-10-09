import pyocnp
import pandas as pd
import ocnpylib as ocpy
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
from matplotlib.dates import DateFormatter
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


def func(label):
    index = labels.index(label)
    lines[index].set_visible(not lines[index].get_visible())
    plt.draw()


def plot_df(ax, df, sen, par, idx, lines):
    for i, j in enumerate(['OK', 'NOK']):
        idx = [idx, ~idx][i]
        vl = df.loc[sen, par][idx.loc[sen, '{}_PROD'.format(par)]]
        if not vl.empty:
            lx, = ax.plot(vl.index, vl, marker=['.', 'd'][i], linestyle='None',
                          label='{} {} {}'.format(j, sen[0], sen[1]))
            lines.append(lx)


#  Setup de comparação #
ucd = 'P-40'
date_span = ["25/06/2019 00:00:00", "01/07/2019 12:00:00"]
#  Base controle 'PROD' ou 'DESV' (Base antiga)
bd = 'PROD'
#  Parâmetro Oceanograficos Correntes "HCSP", "HCDT".
par = 'HCDT'
############################################################

#  Acessos
db = pyocnp.PROD_DBACCESS if bd == 'PROD' else pyocnp.DESV_DBACCESS
ucdid = pyocnp.ucdid_byname_ocndb(ucd, str_dbaccess=db)[0]
iloc = ocpy.id_local_byname(ucd)  # id local
ilocin = ocpy.id_local_install_byid_local(iloc)  # id local install
ilocinsen = ocpy.id_local_install_sensor_byid_local_install(ilocin)  #
# id local install sensor

# Base antiga
data0, data1, data2, data3, data4 = None, None, None, None, None

try:
    data0 = pyocnp.adcp_ocndbqry(ucdid, [0, 0], date_span, [par], 2, db)
except Exception:
    pass
try:
    data1 = pyocnp.adcp_ocndbqry(ucdid, [0, 0], date_span, [par], 15, db)
except Exception:
    pass
try:
    data2 = pyocnp.ocea2d_ocndbqry(ucdid, date_span, [par], 3, db)
except Exception:
    pass
try:
    data3 = pyocnp.ocea3d_ocndbqry(ucdid, date_span, [par], 4, db)
except Exception:
    pass
try:
    data4 = pyocnp.miros_ocndbqry(ucdid, date_span, [par], 5, db)
except Exception:
    pass

# Nova base
data5, data6 = None, None
data5 = ocpy.ocean_CURR(ilocinsen, date_span)
data6 = ocpy.ocean_CURR_PROFILE(ilocinsen, date_span, [0])

# PLOT
plt.close('all')
fig = plt.figure(facecolor=(1.0, 1.0, 1.0), figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1)
ax.grid('on')
lines = []
for i in [data0, data1, data2, data3, data4]:
    if i is not None:
        lucd = i['tag'].split('@')[0]
        sucd = i['tag'].split()[3]
        name = (' '.join(x for x in lucd.split()[1:]) if 'FP' in lucd else lucd)
        lb1 = '{} {} @ {}'.format(name, sucd, bd)
        l0, = ax.plot(i['t'], i['data0'], '.-',
                      visible=False, label=lb1)
        ax.set_ylabel(i['data0quant'] + " (" +
                      i['data0unit'] + u")", fontsize=12)
        lines.append(l0)    

for i in [data5, data6]:
    if not i.empty:
        sensor = ocpy.get_idxval(i)
        idx = ocpy.idx_prod(i)
        for j in sensor:
            plot_df(ax, i, j, par, idx, lines)

rax = plt.axes([0.70, 0.831, 0.3, 0.15])  # (x0, y0, x1, y1)
labels = [str(line.get_label()) for line in lines]
visibility = [line.get_visible() for line in lines]
check = CheckButtons(rax, labels, visibility)

[check.labels[i].set_color(j.get_color()) for i, j in enumerate(lines)]
check.on_clicked(func)
bb_adj = (95 - max([len(line.get_label()) for line in lines])) / 100
plt.subplots_adjust(top=0.981, bottom=0.1, left=0.07, right=bb_adj)
rax.set_position([bb_adj, 0.831, 0.2, 0.15])
ax.fmt_xdata = DateFormatter('%d/%m/%y %H:%M')
ax.xaxis.set_major_formatter(DateFormatter('%d/%m/%y\n%H:%M'))
[l.set_rotation(45) for l in ax.xaxis.get_majorticklabels()]
