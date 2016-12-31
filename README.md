# Simple Stock App - combining Bokeh, Flask, and Heroku

For this project, I create a simple app to display stock price.

## Functionality 
- At front page, one could input a company stock `ticker`, and choose what one wants to look at. Once submit the answer, site will direct to 2 plots showing time series of the stock price. 
- These two plots are linked using `linked panning` in Bokeh
- One could then further look at the scatter plots of stock from 2 companies. One is what you chased at the front page. For the other one, one could `select` some companies from the drop-down option. 
- This interactive `select` function is implemented using `CustomJS`, a customized Javascript callback function in Bokeh.
- Note: at front page, if you don't input a valid `ticker` or the `ticker` does not exist in the Quandtl database, you will be directed to the `Error Page`. You can choose to come back to the front page from there :)

## Data 
- data is acquired from Quandtl using `requests` library 
- Using `simplejson`, data in JSON formate are then transformed into dataframe in `pandas`
- Data manipulation has been performed in `pandas`

## App creation and deployment  
- Using `Flask`, a dynamic website is created.
- The app is then deployed to Heroku

