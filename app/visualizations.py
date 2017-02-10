from flask import g
import pandas as pd

import matplotlib as mpl
import matplotlib.cm as cmx
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import HoverTool

from connect import get_db
from utils import comp_case


def set_scatter_data():
    cursor = get_db()
    cursor.execute(
        'select E.X1, E.X2, C.sic_cd, C.name, C.id '
        'from embedded E '
        'inner join company_dets C on E.id = C.id')
    SNE_vecs = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    return pd.DataFrame(SNE_vecs, columns=colnames)


def get_scatter_data():
    if not hasattr(g, 'vecs'):
        g.vecs = set_scatter_data()
    return g.vecs


def get_scatter(target=None, sim_ids=None):
    vecs = get_scatter_data()
    theme = cmx.get_cmap('viridis')
    cNorm = mpl.colors.Normalize(vmin=0, vmax=9999)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=theme)

    colors = []

    if target is not None:
        dot_size = []
        alpha = []
        # Color based on proximity to target
        for i in vecs['id']:
            if i == target:
                colors.append("#e844d4")
                dot_size.append([9])
                alpha.append([.9])
            elif i in sim_ids:
                colors.append("#44e858")
                dot_size.append([8])
                alpha.append([.8])
            else:
                colors.append("#acacac")
                dot_size.append([7])
                alpha.append([.5])
    else:
        dot_size = 3
        alpha = .5
        # Color based on SIC code
        for s in vecs['sic_cd']:
            try:
                colorVal = scalarMap.to_rgba(int(s))
                colors.append("#%02x%02x%02x" % (
                    colorVal[0] * 255, colorVal[1] * 255, colorVal[2] * 255))
            except:
                colors.append("#d3d3d3")

    source = ColumnDataSource(
        data=dict(
            x=list(vecs['x1']),
            y=list(vecs['x2']),
            desc=list(vecs['sic_cd']),
            name=list([comp_case(v) for v in vecs['name']]),
        )
    )

    hover = HoverTool(
        tooltips=[
            ("Name", "@name"),
            ("SIC", "@desc"),
        ]
    )

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
    plot = figure(tools=[hover, TOOLS], active_scroll='wheel_zoom')
    plot.scatter(
        'x', 'y', source=source, color=colors, alpha=.5, size=dot_size)
    plot.toolbar.logo = None
    plot.axis.visible = False
    plot.grid.visible = False
    plot.sizing_mode = 'scale_width'

    # Zoom in on specified company
    if target is not None:
        zoom = 0.1
        margin = 0.05
        t_point = vecs[vecs['id'] == target].iloc[0]
        joint = sim_ids + [target]
        joint_df = vecs[vecs['id'].isin(joint)]
        x_min = joint_df['x1'].min()
        x_max = joint_df['x1'].max()
        y_min = joint_df['x2'].min()
        y_max = joint_df['x2'].max()
        max_diff = max(
            t_point['x1'] - x_min,
            x_max - t_point['x1'],
            t_point['x2'] - y_min,
            y_max - t_point['x2'],
        )
        z = max(zoom, max_diff + margin)

        plot.x_range.start = t_point['x1'] - z
        plot.x_range.end = t_point['x1'] + z
        plot.y_range.start = t_point['x2'] - z
        plot.y_range.end = t_point['x2'] + z

    return plot
