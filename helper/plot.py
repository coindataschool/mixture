import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np

plot_params = dict(
    color="0.75",
    style=".-",
    markeredgecolor="0.25",
    markerfacecolor="0.25",
    legend=False,
)

def human_format_dollar_or_num(dollar=False, decimals=0):
    """ 
    Return a function for formatting matplot axis numbers human friendly. 

    Parameters
    ----------
    dollar: logical
        If True, will add $ in front of the numbers.
    decimals: int
        Number of decimals to display.
    """

    base_fmt = '%.{}f%s'.format(decimals)
    if dollar:
        base_fmt = '$' + base_fmt

    def human_format(num, pos): # pos is necessary as it'll be used by matplotlib
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return base_fmt % (num, ['', 'K', 'M', 'B', 'T', 'P'][magnitude])
    return human_format


def heatmap(values, xlabel, ylabel, xticklabels, yticklabels, cmap=None,
            vmin=None, vmax=None, ax=None, fmt="%0.2f", text_size=10):    
    if ax is None:
        ax = plt.gca()
    img = ax.pcolor(values, cmap=cmap, vmin=vmin, vmax=vmax)
    img.update_scalarmappable()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticks(np.arange(len(xticklabels)) + .5)
    ax.set_yticks(np.arange(len(yticklabels)) + .5)
    ax.set_xticklabels(xticklabels, fontsize=text_size)
    ax.set_yticklabels(yticklabels, fontsize=text_size)
    ax.set_aspect(1)

    for p, color, value in zip(img.get_paths(), img.get_facecolors(),
                               img.get_array()):
        x, y = p.vertices[:-2, :].mean(0)
        if np.mean(color[:3]) > 0.5:
            c = 'k'
        else:
            c = 'w'
        ax.text(x, y, fmt % value, color=c, ha="center", va="center", 
                fontsize=text_size)
    return img


def plot_timeseries_with_trendline(ytru, yhat, title=None, xlabel=None, 
                                   ylabel=None, ytru_legend=None, 
                                   yhat_legend=None):
    """
    Plot timeseries data and linear trend forecast.
    Although this function also works for forecast obtained using any method 
    (not limited to linear trend), it's designed primarily for plotting a 
    timeseries with a trend line to gain quick understandings about the data.

    Parameters
    ----------
    ytru: Series
        Observed outcome.
    yhat: Series 
        Predicted outcome.
    title: str 
        Figure title.
    xlabel: str 
    ylabel: str
    ytru_legend: str 
        Legend label for observed outcome.
    yhat_legend: str 
        Legend label for predicted outcome.
    """
    if xlabel is None:
        xlabel = ytru.index.name
    if ylabel is None:
        ylabel = ytru.name
    if ytru_legend is None:
        ytru_legend = ytru.name

    ax = ytru.plot(**plot_params, label=ytru_legend)
    ax = yhat.plot(ax=ax, linewidth=2, label=yhat_legend, color='C0')
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    ax.legend()
    return ax


def plot_pred_singlestep(ytru, yhat_train, yhat_test, 
                         title=None, xlabel=None, ylabel=None, 
                         ytru_legend=None):
    """
    Plot timeseries data and 1-step forecasts.

    Parameters
    ----------
    ytru: Series
        Observed outcome. 
    yhat_train: Series 
        Predicted outcome on training set.
    yhat_test: Series 
        Predicted outcome on testing set.
    title: str 
        Figure title.
    xlabel: str 
    ylabel: str
    ytru_legend: str 
        Legend label for observed outcome.
    """
    if xlabel is None:
        xlabel = ytru.index.name
    if ylabel is None:
        ylabel = ytru.name
    if ytru_legend is None:
        ytru_legend = ytru.name
        
    ax = ytru.plot(**plot_params, alpha=0.5, label=ytru_legend)
    ax = yhat_train.plot(ax=ax, linewidth=2, label="(Training) Forecast", color='C0')
    ax = yhat_test.plot(ax=ax, linewidth=2, label="(Testing) Forecast", color='C3')
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    ax.legend()
    return ax


def mk_barplot(x, y, title=None, xlabel=None, ylabel=None,
               show_y_as_pct=True, y_pct_decimals=0):
    """
    Plot bar chart where bars below 0 are colored red and above are colored green.

    Parameters
    ----------
    x: Series
        Values on x-axis. 
    y: Series 
        Values on y-axis.
    title, xlabel, ylabel: str 
        Figure title, x-label and y-label.
    show_y_as_pct: logical (default = True)
        Format y-tick labels as %.
    y_pct_decimals: int
        How many decimal points to show when formatting y as %.
    """
    if xlabel is None:
        xlabel = x.name
    if ylabel is None:
        ylabel = y.name
    
    _, ax = plt.subplots(constrained_layout=True) 
    ax.bar(x, y, color=(y > 0).map({True:'#008000', False:'#b22222'}), edgecolor='k')
    # ax.axhline(0, color='k', linestyle = 'dashed')
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    if show_y_as_pct:
        ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=y_pct_decimals))
        nticks = 8 
        steps  = (max(y) - min(y)) / nticks
        plt.yticks(np.arange(min(y), max(y)+steps, steps))
    return ax


def mk_barploth(x, y, title=None, xlabel=None, ylabel=None,
                show_x_as_pct=True, x_pct_decimals=0):
    """
    Plot horizontal bar chart where bars below 0 are colored red and above are colored green.

    Parameters
    ----------
    x: Series
        Values on x-axis. 
    y: Series 
        Values on y-axis.
    title, xlabel, ylabel: str 
        Figure title, x-label and y-label.
    show_x_as_pct: logical (default = True)
        Format x-tick labels as %.
    x_pct_decimals: int
        How many decimal points to show when formatting x as %.
    """
    if xlabel is None:
        xlabel = x.name
    if ylabel is None:
        ylabel = y.name
    
    _, ax = plt.subplots(constrained_layout=True) 
    ax.barh(y, x, color=(x > 0).map({True:'#008000', False:'#b22222'}), edgecolor='k')
    # ax.axhline(0, color='k', linestyle = 'dashed')
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    if show_x_as_pct:
        ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=x_pct_decimals))
        nticks = 8 
        steps  = (max(x) - min(x)) / nticks
        plt.xticks(np.arange(min(x), max(x)+steps, steps))
    return ax    