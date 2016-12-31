import requests
import simplejson as json
import pandas as pd 
from bokeh.plotting import *
from bokeh import embed 
from bokeh.layouts import row, column, widgetbox
from bokeh.models import CustomJS, ColumnDataSource 
from bokeh.models.widgets import Select
from flask import Flask, render_template, request, redirect
app = Flask(__name__)


def acquireDate(s1,s2):	 # s1: companies_target, s2: target-item
	companies_target = s1
	targetItem = s2
	companies_ref = ['GOOG','AMZN','FB','MSFT','WMT','TSLA','BA','INTC']
	API_key = 'THIS-IS-YOUR-QUANDL-API-KEY'   # use a valid API_KEY here 
	companies = [] + companies_ref
	if companies_target not in companies_ref:
		companies.append(companies_target)
	companies = ','.join(companies)
	url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?date.gte=20120101&date.lt=20161201&ticker=' + companies + '&api_key=' + API_key

	r = requests.get(url)   # request response object
	r_str = r.text
	dataDict = json.loads(r_str)   # change json string into python dictionary
	dataList = [ item for item in dataDict['datatable']['data'] ]
	labelList = [ dataDict['datatable']['columns'][i]['name'] for i in xrange(0,len(dataDict['datatable']['columns'])) ]
	df = pd.DataFrame.from_records( dataList, columns=labelList )
	df['date'] = pd.to_datetime(df['date'])

	if len(dataDict['datatable']['data']) == 0:  # if no data in database
		return False
	else:
		return df


def plot_timeseries(s1, s2):	# s1: companies_target, s2: target-item		
	companies_target = s1
	targetItem = s2
	companies_ref = ['GOOG','AMZN','FB','MSFT','WMT','TSLA','BA','INTC']
	df = acquireDate(s1,s2)

	TOOLS = "pan,wheel_zoom,reset,save"
	color_opt = ['#BD1550','#F8CA00','green','red','blue','black','cyan','magenta']
	plot_properties = dict(tools=TOOLS, x_axis_label='time', 
		    y_axis_label=targetItem+' price', x_axis_type="datetime", background_fill_color="#E8DDCB")

	p1 = figure(title = companies_target+' Stock', **plot_properties)
	p1.plot_width = 500
	p1.plot_height = 500
	p1.axis.axis_label_standoff = 10
	p1.axis.axis_label_text_font_size = '20pt'
	p1.title.text_font_size = '16pt'
	df_sub = df[ df['ticker']==companies_target ]
	p1.line( df_sub['date'].values, df_sub[targetItem].values, color='#E97F02', line_width=4 )

	p2 = figure(title = companies_target+' stock compared to other companies', 
		          x_range=p1.x_range, y_range=p1.y_range, **plot_properties)
	p2.plot_width = 500
	p2.plot_height = 500
	p2.axis.axis_label_standoff = 10
	p2.axis.axis_label_text_font_size = '20pt'
	p2.title.text_font_size = '16pt'
	if companies_target in companies_ref:
	    companies_ref.remove(companies_target)
	    color_opt.pop()
	for i, item in enumerate(companies_ref):  # plot lines for those reference companies
	    df_sub = df[ df['ticker']==item ]
	    p2.line( df_sub['date'].values, df_sub[targetItem].values, line_width=1, color=color_opt[i], 
	            legend=item )
	df_sub = df[ df['ticker']==companies_target ]  # plot line for the target company
	p2.line( df_sub['date'].values, df_sub[targetItem].values, line_width=4, color='#E97F02', 
	        legend=companies_target )
	p2.legend.background_fill_alpha = 0
	p2.legend.location = "top_left"

	return row(p1, p2)


# this function make an interactive plot where user can select companies
# use callback from Bokeh
def make_interactive_plot(s1, s2):  
	companies_target = s1
	targetItem = s2

	companies_ref = ['GOOG','AMZN','FB','MSFT','WMT','TSLA','BA','INTC']
	y_ref = {}    # dictionary: storing data for all these companies
	if companies_target not in companies_ref:
		list_in = companies_ref + [companies_target]
	else:
		list_in = companies_ref
	for item in list_in:
		df = acquireDate(companies_target, targetItem)
		df_sub = df[ df['ticker']==item ][-600:]
		y_ref[item] = df_sub[targetItem].tolist()  # attach the selected stock to that company

	source = ColumnDataSource(data=dict(x=y_ref['AMZN'], y=y_ref[companies_target], y_GOOG=y_ref['GOOG'], y_AMZN=y_ref['AMZN'],
		y_FB=y_ref['FB'], y_MSFT=y_ref['MSFT'], y_WMT=y_ref['WMT'], y_TSLA=y_ref['TSLA'], y_BA=y_ref['BA'], y_INTC=y_ref['INTC'] ))

	TOOLS = "pan,wheel_zoom,reset,save"
	color_opt = ['#BD1550','#F8CA00','green','red','blue','black','cyan','magenta']
	plot_properties = dict(tools=TOOLS, x_axis_label=targetItem+' price from selected companies', 
	y_axis_label=companies_target+' '+targetItem+' price', background_fill_color="#E8DDCB")

	p = figure(title = 'Scatter plot of stock', **plot_properties)
	p.plot_width = 400
	p.plot_height = 400

	p.scatter( 'x', 'y', source=source, marker='o', size=8, line_color="navy", fill_color="orange", alpha=0.8)
	callback = CustomJS(args=dict(source=source), code="""
		var data = source.get('data');
	    var f = cb_obj.get('value')
	    if (f == 'AMZN') { data['x'] = data['y_AMZN']; source.trigger('change'); }
	    if (f == 'GOOG') { data['x'] = data['y_GOOG']; source.trigger('change'); }
	    if (f == 'FB') { data['x'] = data['y_FB']; source.trigger('change'); }
	    if (f == 'MSFT') { data['x'] = data['y_MSFT']; source.trigger('change'); }
	    if (f == 'WMT') { data['x'] = data['y_WMT']; source.trigger('change'); }
	    if (f == 'TSLA') { data['x'] = data['y_TSLA']; source.trigger('change'); }
	    if (f == 'BA') { data['x'] = data['y_BA']; source.trigger('change'); }
	    if (f == 'INTC') { data['x'] = data['y_INTC']; source.trigger('change'); }
	    """)

	select = Select(title="Option:", value="AMZN", options=companies_ref, callback=callback)

	return( column( select, p ) )
	


app.vars = {}  # create a dictionary to store input


@app.route('/')  # this is for Heroku where the first page just "https://....com/"
def main():
  return redirect('/index')


@app.route('/index', methods=['GET','POST'])
def index():
	if request.method == 'GET':
		return render_template('front_page.html')
	else:
		if len(request.form['company_name'])==0:
			return render_template('error_page.html')
		else:
			app.vars['name'] = request.form['company_name'] 
			app.vars['value'] = request.form['choosenOption']
			return redirect('/plot')


@app.route('/plot', methods=['GET','POST'])
def plotResult():
	if request.method == 'GET':
		plot = plot_timeseries( app.vars['name'], app.vars['value'] )
		if plot == False:  # i.e. no data in the database
			return render_template('error_page.html')
		else:
			script, div = embed.components( plot )
			return render_template( 'bokeh_plot.html', script=script, div=div )
	else:
		return render_template('front_page.html')


@app.route('/plot_inter', methods=['GET','POST'])
def plotResult_interactive():
	if request.method == 'GET':
		plot_inter = make_interactive_plot( app.vars['name'], app.vars['value'] )
		script, div = embed.components( plot_inter )
		return render_template( 'bokeh_plot_interactive.html', script=script, div=div )
	else:
		return render_template('front_page.html')


if __name__ == "__main__":
	app.run( debug=True )	










