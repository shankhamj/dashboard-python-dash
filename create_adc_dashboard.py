import pandas as pd
import plotly.express as px
import dash
from dash import html
from dash import dcc
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash.dependencies import  Input,Output
from datetime import date
import plotly.io as pio
import time
import os
print(os.getcwd())
daterange = pd.date_range(start='1/1/2022',end='5/1/2022',freq='M')

def unixTimeMillis(dt):
    return int(time.mktime(dt.timetuple()))
def unixtoDateTime(unix):
    return pd.to_datetime(unix,unit='s')
def TimeStamptoWeekYear(tstamp):
    return tstamp.strftime('%m%y')
def getMarks(start,end):
    result = {}
    for i,date in enumerate(daterange):
        result[unixTimeMillis(date)] = str(date.strftime('%m%Y'))
    return result

marks = getMarks(daterange.min(),daterange.max())



# adc_data = pd.read_csv('../adc_data_prem.csv',index_col=0)
adc_data = pd.read_csv('C:/Users/smajumde/PycharmProjects/Risk/adc_data_prem.csv',index_col=0)
adc_data['MonthYear'] = adc_data.apply(lambda x: f"{x['month_week'].split()[0]}22",axis=1)
sorted_list = sorted(adc_data['MonthYear'].unique())
list_of_al_types = adc_data['source_app_id'].tolist()

list_of_al_types = list(set(list_of_al_types))

list_of_al_types_main = adc_data['al_type'].tolist()

list_of_al_types_main = list(set(list_of_al_types_main))

adc_data['manager_flag'] = adc_data['manager_flag'].astype(str)
adc_data['proxy_flag'] = adc_data['proxy_flag'].astype(str)
adc_data_managers = adc_data[adc_data['manager_flag'] == 'True']



app = dash.Dash('__name__')

grouping_of_activity_code = adc_data.groupby('activity_code').size().reset_index()
grouping_of_activity_code.rename(columns={0:'count'},inplace=True)
fig = px.bar(adc_data.groupby('activity_code').size().reset_index(),x='activity_code',y=0,barmode='group',template = 'plotly_dark', title='Count of Activity by Type All Time')

fig.update_layout(autosize=False,width=650,height=300,yaxis_title='count')

grouping_of_activity_code_managers = adc_data_managers.groupby('activity_code').size().reset_index()
grouping_of_activity_code_managers.rename(columns={0:'count'},inplace=True)

fig2 = px.bar(adc_data[~(adc_data['menu_item'].isnull())].groupby('menu_item').size().reset_index(),x='menu_item',y=0,barmode='group',template = 'plotly_dark', title='Count of Menu Item Actions')

fig2.update_layout(autosize=False,width=1330,height=600,xaxis_title='Menu Item', yaxis_title='Count')
grouping_on_week = adc_data.groupby(['month_week','activity_code']).size().reset_index()
grouping_on_week.rename(columns={0:'count'},inplace=True)
activity_type_w_o_w = px.scatter(adc_data.groupby(['month_week','activity_code']).size().reset_index(),x='month_week',y=0,size=0,color='activity_code',title='Activity Type Week on Week',template='plotly_dark')

activity_type_w_o_w.update_layout(autosize=False,width=1330,height=400,yaxis_title='Count')

# dcc.Dropdown(id='week-filter',options=[{'label':week,'value':week} for week in adc_data['month_week'].unique()],value='',clearable=True),

app.layout = html.Div(children=[

    html.Div(id='container',children=[html.H2('ADC Demo Dashboard',style={'fontFamily':'Roboto'}),html.H4('Charts Visuals depicting AL Usage',style={'fontFamily':'Roboto'}), \
                                      html.Hr(),html.H4('Pick Date Range'),
                                      dcc.RangeSlider(id='month_slider',min=unixTimeMillis(daterange.min()),max=unixTimeMillis(daterange.max()),\
                                      value = [unixTimeMillis(daterange.min()),unixTimeMillis(daterange.max())],marks=marks),
                                      html.H4('Select Source App'),
                                      html.Div(className='div-for-dropdown',children = [dcc.Dropdown(id='altype-dropdown',options=[{"label":i,"value":i} for i in list_of_al_types],value=list_of_al_types,multi=True,placeholder='Select or start typing..' )]),
                                      html.H4('Select AL Type'),
                                      html.Div(className='div-for-altype-dropdown', children=[dcc.Dropdown(id='altype-bottom-dropdown',options=[{"label": i, "value": i} for i in list_of_al_types_main],value=list_of_al_types_main, multi=True,placeholder='Select or start typing..')]),
                                      html.Div(id='Flag-component',children=[html.H4('Manager Flag'),html.H4('Proxy Flag')]),
                                      html.Div(id='Switch-container',children = [daq.BooleanSwitch(id='manager-flag',on=False,color='green'),daq.BooleanSwitch(id='proxy-flag',on=False,color='green')])


                                      ]),
                                      # dcc.RangeSlider(id='date-range',min_date_allowed=date(2021,1,1),max_date_allowed=date(2022,5,16),initial_visible_month = date(2021,1,1))]).
                                      #dcc.RangeSlider(id='slider',min=2021,max=2022.6,step=0.1,value=[2021,2022],tooltip={'always_visible':True,'placement':'bottom'})])



    html.Div(id='graph-container',children=[dcc.Graph(id='graph1',figure=fig),dcc.Graph(id='graph2',figure=fig)]),
    html.Div(children=[dcc.Graph(id='graph3',figure=activity_type_w_o_w)]),
    html.Div(id='second-graph-container',children=[dcc.Graph(id='graph5',figure=fig2)])
])


@app.callback(
    Output('graph1','figure'),
    Output('graph2','figure'),
    Output('graph3','figure'),
    Output('graph5','figure'),
    Input('month_slider','value'),
    Input('altype-dropdown','value'),
    Input('manager-flag','on'),
    Input('proxy-flag','on'))


def update_graphs(months_list,al_type_values,manager_flag,proxy_flag):
    months_list = [unixtoDateTime(x) for x in months_list]
    months_list = [TimeStamptoWeekYear(x) for x in months_list]
    print(f'input list is {months_list}')
    initial_pos = sorted_list.index(months_list[0])
    final_pos = sorted_list.index(months_list[1])+1

    final_list = sorted_list[initial_pos:final_pos]
    print(f'final list is {final_list}')
    manager_flag_val = f'{manager_flag}'
    proxy_flag_val = f'{proxy_flag}'


    if(manager_flag_val == "True"):
        adc_data_filtered = adc_data[adc_data['manager_flag'] =='True']

    else:
        adc_data_filtered = adc_data

    if (proxy_flag_val == 'True'):
        adc_data_filtered = adc_data_filtered[adc_data_filtered['proxy_flag'] == 'True']

    adc_data_filtered = adc_data_filtered[adc_data_filtered['source_app_id'].isin(al_type_values)]
    adc_data_filtered = adc_data_filtered[adc_data_filtered['MonthYear'].isin(final_list)]
    fig_first_second = px.bar(adc_data_filtered.groupby('activity_code').size().reset_index(), x='activity_code', y=0, barmode='group',template='plotly_dark', title='Count of Activity by Type All Time')
    fig_first_second.update_layout(autosize=False, width=650, height=300, yaxis_title='count')
    activity_type_w_o_w_out = px.scatter(adc_data_filtered.groupby(['month_week', 'activity_code']).size().reset_index(),x='month_week', y=0, size=0, color='activity_code',title='Activity Type Week on Week', template='plotly_dark')
    activity_type_w_o_w_out.update_layout(autosize=False, width=1320, height=400, yaxis_title='Count')

    fig2_out = px.bar(adc_data_filtered[~(adc_data_filtered['menu_item'].isnull())].groupby('menu_item').size().reset_index(), x='menu_item',y=0, barmode='group', template='plotly_dark', title='Count of Menu Item Actions')

    fig2_out.update_layout(autosize=False, width=1320, height=600, xaxis_title='Menu Item', yaxis_title='Count')

    return fig_first_second,fig_first_second,activity_type_w_o_w_out,fig2_out
if __name__ == '__main__':
    app.run_server(debug=True)
