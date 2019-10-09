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
                          label='{} {}'.format(j, sen[1]))
            lines.append(lx)


#  Setup de comparação #
ucd = 'pmxl-1'
date_span = ["05/08/2019 00:00:00", "06/08/2019 12:00:00"]
#  Base controle 'PROD' ou 'DESV' (Base antiga)
bd = 'PROD'
#  Parâmetro Meteorologico "ATMS", "RELH", "DRYT", "WSPD" ou "WDIR"
par = 'RELH'
############################################################
 
#  Acessos
db = pyocnp.PROD_DBACCESS if bd == 'PROD' else pyocnp.DESV_DBACCESS
ucdid = pyocnp.ucdid_byname_ocndb(ucd, str_dbaccess=db)[0]
iloc = ocpy.id_local_byname(ucd)  # id local

ilocin = ocpy.id_local_install_byid_local(iloc)  # id local install
ilocinsen = ocpy.id_local_install_sensor_byid_local_install(ilocin)  #
# id local install sensor

# limpeza de variaveis
Data_ctrl, Data_teste = None, None

# Base antiga
Data_ctrl = pyocnp.meteo_ocndbqry(ucdid, date_span, [par], 1, db)

# Nova base
fun_par = {'ATMS': 'meteo_ATMS', 'RELH': 'meteo_RELH',
           'DRYT': 'meteo_DRYT', 'WSPD': 'meteo_WIND',
           'WDIR': 'meteo_WIND'}

Data_teste = getattr(ocpy, fun_par[par])(ilocinsen, date_span)
if Data_ctrl is None or Data_teste is None:
    raise
elif Data_teste.empty:
    raise

# PLOT
plt.close('all')
fig = plt.figure(facecolor=(1.0, 1.0, 1.0), figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1)
ax.grid('on')
lines = []
lucd = Data_ctrl['tag'].split('@')[0]
name = (' '.join(x for x in lucd.split()[1:]) if 'FP' in lucd else lucd)
lb1 = '{} @ {}'.format(name, bd)
l0, = ax.plot(Data_ctrl['t'], Data_ctrl['data0'], '.-g',
              visible=False, label=lb1)
ax.set_ylabel(Data_ctrl['data0quant'] + " (" +
              Data_ctrl['data0unit'] + u")", fontsize=12)
lines.append(l0)

sensor = ocpy.get_idxval(Data_teste)
idx = ocpy.idx_prod(Data_teste)

for i in sensor:
    plot_df(ax, Data_teste, i, par, idx, lines)

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
