from os.path import dirname, join

import numpy as np
# import sqlite3 as sql

from bokeh.plotting import figure, show, save
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, Div
from bokeh.models.widgets import Slider, Select, TextInput
from bokeh.palettes import Blues6 as palette
from bokeh.models import HoverTool, LinearColorMapper, LogColorMapper
from bokeh.io import curdoc, output_file
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html

# conn = sql.connect(movie_path)
# query = open(join(dirname(__file__), 'query.sql')).read()
# guilddata = psql.read_sql(query, conn)

guilddata = pandas.read_csv('byguilddata.csv')

palette.reverse()
color_mapper = LogColorMapper(palette)

guilddata['size'] = guilddata['members'] / 5

# palettesize = len(palette)
# guilddata['elocolor'] = guilddata['elo']
# minElo = min(guilddata['elo'])
# maxElo = max(guilddata['elocolor'])
# guilddata['elocolor'].fillna(minElo, inplace=True)
# guilddata['elocolor'] = ((guilddata['elocolor'] - minElo) / (maxElo - minElo) * palettesize).astype(int)
# guilddata.loc[guilddata['elocolor'] == palettesize, 'elocolor'] = palettesize - 1

# guilddata['color'] = [palette[i] for i in guilddata['elocolor']]

axis_map = {
    "Members": "members",
    "Elo": "elo",
    "Activity": "activity",
    "Sessions": "sessioncount",
    "Days Played": 'sessiondaycount',
    "Rev (Past Week)": 'revweekpast',
    "Rev (Total Past)": "revtotalpast",
    "Ruby Balance": 'ruby',    
    "Level": "level",
    "Cohortday (Median)": 'median_cohortday',
    'Guild Chat Count (Week)': 'guildchatcount',
    'Total Chats': 'numchatspast',
    'Attacks': 'attacks',
    'Defenses': 'defenses',
    'Attack Follow Rate': 'atkfollowrate_weighted',
    'Defense Assist Rate': 'defassistrate_weighted',
    'Attack Accept Rate': 'atkacceptrate_weighted',
    'Defense Accept Rate': 'dfacceptrate_weighted',
    'Breeder Tasks Completed': 'breedertaskcompleted',
    'Dragons Upgraded': 'dragonupgraded',
    'Towers Upgraded': 'towerupgraded',
    'Gifts Received': 'numgiftrec',
    'Gifts Sent': 'numgiftsent',
    'Session ID': 'session_id',
    'Sessions per Day': 'sessions_per_day',
    'Days since Played': 'dayssinceplayed',
    'Num Crashes': 'numcrasheswindow',
    'Crash Rate/Session': 'crashrate',
    'Average Startup': 'avgstartup',
    'Language Similarity': 'lang_match',
    'Food Balance': 'food',
    'Wood Balance': 'piercing',
    'Breeding Token Balance': 'breedingtoken',
    'Daily Tokens Collected': 'dailytokenscollected',
    'Total Number of Purchases': 'revcounttotalpast',
    'Rev (Past 2 Weeks)': 'revwindowpast',
    'League Chats': 'numleaguechats',
    'Custom Chats': 'numcustomchats',
}

desc = Div(text=open(join(dirname(__file__), "description.html")).read(), width=800)

# Create Input controls
members = Slider(title="Minimum number of members", start=0, end=50, value=5, step=1)
eloMin = Slider(title="Minimum Elo", start=800, end=2500, value=1000, step=50)
eloMax = Slider(title="Max Elo", start=800, end=2500, value=2500, step=50)
activityMin = Slider(title="Minimum Activity", start=0, end=100, value=0, step=1)
activityMax = Slider(title="Max Activity", start=0, end=100, value=100, step=1)
tier = Select(title="Tier", value="All",
               options=open(join(dirname(__file__), 'tiers.txt')).read().split())
guild_lang = Select(title="Guild Language", value="All",
               options=open(join(dirname(__file__), 'guild_lang.txt')).read().split())
country = Select(title="Country (Mode)", value="All",
               options=open(join(dirname(__file__), 'countries.txt')).read().split())
guild_name = TextInput(title="Guild name contains")
x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="Attack Follow Rate")
y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="Sessions")
color_var = Select(title="Color", options=sorted(axis_map.keys()), value="Elo")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], name=[], tier=[], elo=[], country=[], members=[], size=[], color=[]))

hover = HoverTool(tooltips=[
    ("Name", "@name"),
    ("Tier", "@tier"),
    ("Elo", "@elo"),
    ("Country", "@country"),
    ("Members", "@members"),
    ('x', "@x"),
    ('y', "@y"),
    ('color', "@color"),
])

# TOOLS="pan,wheel_zoom,box_zoom,reset,hover,save"
p = figure(plot_height=700, plot_width=1000, title="", toolbar_location=None, tools=[hover])
p.circle(x="x", y="y", source=source,
    size='size',
    color={'field': 'color', 'transform': color_mapper},
    # color='color',
    line_color=None)



def select_guilds():
    tier_val = tier.value
    guild_lang_val = guild_lang.value
    country_val = country.value
    name_val = guild_name.value.strip()
    selected = guilddata[
        (guilddata.members >= members.value) &
        (guilddata.elo >= eloMin.value) &
        (guilddata.elo <= eloMax.value) &
        (guilddata.activity >= activityMin.value) &
        (guilddata.activity <= activityMax.value)
    ]
    if (tier_val != "All"):
        selected = selected[selected.tier.str.contains(tier_val) == True]
    if (country_val != "All"):
        selected = selected[selected.mode_country.str.contains(country_val) == True]
    if (guild_lang_val != "All"):
        selected = selected[selected.guild_lang.str.contains(guild_lang_val) == True]
    if (name_val != ""):
        selected = selected[selected.guild_name.str.contains(name_val) == True]
    return selected


def update():
    df = select_guilds()
    x_name = axis_map[x_axis.value]
    y_name = axis_map[y_axis.value]
    color_name = axis_map[color_var.value]

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = "%d guilds selected" % len(df)
    source.data = dict(
        x=df[x_name],
        y=df[y_name],
        name=df["guild_name"],
        tier=df["tier"],
        elo=df["elo"],
        country=df['mode_country'],
        members=df['members'],
        size=df['size'],
        color=df[color_name]
    )

    hover = HoverTool(tooltips=[
        ("Name", "@name"),
        ("Tier", "@tier"),
        ("Elo", "@elo"),
        ("Country", "@country"),
        ("Members", "@members"),
        (x_axis.value, "@x"),
        (y_axis.value, "@y"),
        (color_var.value, "@color"),
    ])

controls = [members, eloMin, eloMax, activityMin, activityMax, tier, guild_lang, country, guild_name, x_axis, y_axis, color_var]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example

inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([
    [desc],
    [inputs, p],
], sizing_mode=sizing_mode)

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "guilddata"

# guilds_html = file_html(p, CDN, title='guilds plot')
# import ipdb; ipdb.set_trace()

# output_file("guilds_output.html", title="Guilds Data Explorer")
# save(p)




