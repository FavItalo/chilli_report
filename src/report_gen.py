import pandas as pd
import matplotlib as mpl

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from PIL import Image, ImageDraw, ImageFont

def importResults(path:str = "inputs/results.csv") -> pd.DataFrame:
    df = pd.read_csv(path, index_col=0, header=0)
    df.index = pd.to_datetime(df.index*10**9)
    df.sort_index(inplace=True)
    df.index = df.index + pd.DateOffset(hours=-3)

    return df

def relatorioInfo(dataframe:pd.Series, data:str|pd.Timestamp, tipo:str = "fds") -> dict:
    if type(data) == str:
        data = pd.to_datetime(data)

    initialDate = pd.Timestamp(data.year, data.month, data.day, 12) - pd.DateOffset(days=1)
    endDate = initialDate + pd.DateOffset(days=1)

    if tipo == "fds":
        subsetDataframe = dataframe[(dataframe.index >= initialDate) & (dataframe.index <= endDate)]

    movimentoPico = subsetDataframe.max(0)
    horaPico = subsetDataframe.idxmax(0)
    marcaFesta = movimentoPico - 2*subsetDataframe.std()
    subsetFesta = subsetDataframe[subsetDataframe>=marcaFesta]
    duracao_festa_timedelta = (subsetFesta.index[-1] - subsetFesta.index[0])

    infoDict = {"data": data,
                "subset": subsetDataframe,
                "movimento": movimentoPico,
                "hr_pico": horaPico,
                "inicio_festa": subsetFesta.index[0],
                "duracao_festa": f"{duracao_festa_timedelta.components[1]} Horas e {duracao_festa_timedelta.components[2]} Minutos",
                "marca_festa": marcaFesta}

    return infoDict

def plot_chilli(data:pd.DataFrame, lineMark:float) -> None:
    fig, ax = plt.subplots(figsize=(15,6), dpi=100)

    ax.plot(data.index, data.values, 'o-')
    ax.hlines(lineMark,xmin=data.index[0], xmax=data.index[-1], linestyles="dashed", color="#040404")
    ax.spines[['right', 'top']].set_visible(False)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    
    fig.autofmt_xdate()

    plt.savefig("utils/images/report_day_transparent.png", transparent=True)
    plt.savefig("utils/images/report_day.png", transparent=False)

    return None

def create_relatorio(graph_path:str, logo_path:str, info_display:dict, dpi = 90) -> None:
    width = int((42.0/2.54)*dpi)
    height = int((29.7/2.54)*dpi)

    canvas = Image.new('RGBA', (width,height), color=(255,255,255))
    draw = ImageDraw.Draw(canvas)

    draw.rectangle((0,0,width,height/8), fill=(241,19,43))
    
    logo = Image.open(logo_path)
    graph = Image.open(graph_path)

    logo_resize = logo.resize((int(1.25*logo.size[0]),int(1.25*logo.size[1])), Image.Resampling.LANCZOS)

    canvas.paste(logo_resize, box=(int((width-logo_resize.size[0])/2),0), mask=logo_resize)
    canvas.paste(graph, box=(int((width-graph.size[0])/10),int(height/3)), mask = graph)

    
    font_h1 = ImageFont.truetype("FreeMono.ttf", 36)
    font_normal = ImageFont.truetype("FreeMono.ttf", 30)
    draw.text((int(width/10),int(height/6)), f"Data de referência: {info_display['data'].date()}", font=font_h1, fill=(0,0,0))
    draw.text((int(width/10),int(height/4.5)), f"Movimentação máxima: {info_display['movimento']}\nHorário de Pico: {info_display['hr_pico'].time()}", font=font_normal, fill=(0,0,0))
    draw.text((int(width/10), int(height*13/15)), f"Início da festa: {info_display['inicio_festa'].time()}\nDuração da festa: {info_display['duracao_festa']}", font=font_normal, fill=(0,0,0))

    canvas.save("utils/images/report_filled.png")

    return None

def main():

    df = importResults()

    infoDict = relatorioInfo(df.iloc[:,0], data = pd.to_datetime("today"), tipo="fds")
    
    plot_chilli(infoDict["subset"], lineMark=infoDict["marca_festa"])

    create_relatorio("utils/images/report_day_transparent.png", "utils/logo/Logo transparente.webp", info_display=infoDict)

    return None

if __name__=="__main__":

    mpl.rc('xtick', labelsize=16)
    mpl.rc('ytick', labelsize=16)

    mpl.rcParams['lines.linewidth'] = 1.5
    mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=["#f1132b",
                                                        "#040404"])
    plt.rcParams.update({"text.usetex": False,
    "font.family": "Fira Sans"})

    main()

