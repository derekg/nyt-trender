#
# Yeah so I know this is some horrible code - but it is from demo purposes only. So just fork it.
#
from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext.webapp.util import run_wsgi_app
from pygooglechart import SimpleLineChart
from pygooglechart import GroupedVerticalBarChart
from pygooglechart import Axis
import urllib,calendar

HTML_TEMPLATE="""<html>
<style>
BODY { 
        color: #142A3B;
        background: #aaa;
        font-family: Verdana, Geneva, Arial, Helvetica, sans-serif;
	text-align: center;
	align: center;

}
a:link {
  color: #111;
}

a:visited {
  color: #111;
}

input {
        font-family: 'Lucida Grande', 'Lucida Sans Unicode', Verdana, Geneva, Lucida, Arial, Helvetica, sans-serif;
        border-top: 1px solid #666;
        border-right: 1px solid #999;
        border-bottom: 1px solid #999;
        border-left: 1px solid #666;
        padding: 4px;
        margin: 4px;
        background-color: #eef;
	font-size: 16pt;
}

div {
        -moz-border-radius: 10px;
        background-color: #fafafa;
        border: 2px solid #EEEAE4;
        margin: 0px 0px 8px 2%%;
        padding: 0px;
        float: left;
}

#container { 
	width: 940px;
}

img {
        -moz-border-radius: 10px;
        background-color: #fafafa;
        border: 2px solid #EEEAE4;
        margin: 0px 0px 8px 2%%;
        padding: 0px;
}

#graph {  
	float: left;
	width: 630px;
}
#img { 
	width: 120px;
        border: 2px solid #aaaaaa;
}

</style>
<title>NYT Trender</title>
<body>
<div id="container">
<form>
<input type="textfield" name="query1" value="%(query1)s" size=15>
<strong>VS</strong>
<input type="textfield" name="query2" value="%(query2)s" size=15>
<input type="submit" name="Trend" value="Trend"></form></div>
"""

api_key ="INSERT YOUR NYTIMES.COM ARTICLE SEARCH API KEY - http://developer.nytimes.com"

search = lambda q: eval(urlfetch.fetch('http://api.nytimes.com/svc/search/v1/article?api-key=%s&query=%s&fields=url,title,small_image_url&facets=publication_month&format=json&rank=closest' % (api_key, urllib.quote(q.replace('"','"'))) ).content.replace('\\/','/'))

def extract(rdata):
	data = []
	if 'facets' in rdata and 'publication_month' in rdata['facets']:
		lookup = dict([(x['term'],x['count']) for x in rdata['facets']['publication_month']])
		for i in [ '%02d' % x for x in range(1,13) ] :
			if i not in lookup: 
				data.append(0)
			else:
				data.append(int(lookup[i]))
	else:
		data = [0] * 12
	return data

class MainPage(webapp.RequestHandler):
	def get(self):
		query1 = self.request.get('query1');
		query2 = self.request.get('query2');
		if query2 == '':
			 query2 = query1;
		self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
		self.response.out.write(HTML_TEMPLATE % {'query1' : query1.replace('"','&quot;'), 'query2' : query2.replace('"','&quot;')})
		if query1 != None and query2 != None:
			year_07 = '%s publication_year:[2008]' %  query1
			year_08 = '%s publication_year:[2008]' %  query2
			results7 = search(year_07)
			results8 = search(year_08)
			data7 = extract(results7)
			data8 = extract(results8)
			if sum(data8) == 0:
				data8 = [1] * 12
			big = max(data7 + data8)
			small = min(data7 + data8)
			chart = SimpleLineChart(600,400,y_range=[ small, big])
			chart.add_data(data7)
			chart.add_data(data8)
			chart.set_colours(['207000','0077A0'])
			chart.set_axis_labels(Axis.LEFT,range(small,big,((big-small+1)/ 12)+1)) 
			chart.set_axis_labels(Axis.BOTTOM,[ x[:3] for x in calendar.month_name ][1:])
			chart.set_line_style(0,thickness=6)
			chart.set_line_style(1,thickness=6)
			self.response.out.write('<div id="container">') 
			self.response.out.write('<div id="graph">') 
			self.response.out.write('<h2>Trend <font color="207000">%s</font> vs. <font color="0077A0">%s</font> for 2008</h2>' % (query1,query2))
			self.response.out.write('<img src="%s">' % chart.get_url() )
			self.response.out.write('<strong>Total: <font color="207000">%s</font> %d</strong> &nbsp; ' %(query1,results7['total']))
			self.response.out.write('<strong><font color="0077A0">%s</font> %d</strong>' % (query2,results8['total']))
			self.response.out.write('<br>As mentioned in articles from <a href="http://www.nytimes.com">The New York Times</a>')
			self.response.out.write('</div')
			self.response.out.write('<div id="img"><center>')
			self.response.out.write('<h2><font color="207000">%s</font></h2>'% (query1))
			for i in results7['results']:
				if 'small_image_url' in i: 
					self.response.out.write('<a href="%s"><img src="%s"></a>' % (i['url'],i['small_image_url']))
			self.response.out.write('</center></div>')
			self.response.out.write('<div id="img"><center>')
			self.response.out.write('<h2><font color="0077A0">%s</font></h2>'% (query2))
			for i in results8['results']:
				if 'small_image_url' in i: 
					self.response.out.write('<a href="%s"><img src="%s"></a>' % (i['url'],i['small_image_url']))
			self.response.out.write('</center></div>')
			self.response.out.write('</div>')
		self.response.out.write('<div id="container">brought to you via the search api of <a href="http://developer.nytimes.com">nytimes.com</a> and <a href="http://twitter.com/derekg">derekg</a></div>')
		self.response.out.write('</center></body></html>')

application = webapp.WSGIApplication( [('/', MainPage)], debug=True)

def main():
	run_wsgi_app(application)
if __name__ == "__main__":
	main()
