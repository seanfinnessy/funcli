import click
import requests

querystring = {"symbols": "AAPL,BTC-USD,EURUSD=X"}

# No, this should not be hardcoded. But it's fine this is just messing around.
# 100 request/day
headers = {
    'x-api-key': "YOxiimvHJY5M7IWyfKGfL3uCPlQ3e1bX9mmMA2f0"
}


@click.group()
def fancywallet():
    '''
    Fancy commands to manage your assets
    '''


@click.group(name='get')
def get_group():
    '''
    Group of commands to get something
    '''
    pass


@click.command(name='price')
@click.argument('stock')
def get_stock_price(stock):
    '''
    Gets the stock price
    '''
    result = requests.get(
        f'https://yfapi.net/v8/finance/chart/{stock}', headers=headers, params=querystring)
    result_dict = result.json()
    if result_dict['chart']['result'] == None:
        click.echo(f'Company {stock} not found!')
        exit(404)
    # echo is better than print for click terminal interface.
    click.echo(result_dict['chart']['result'][0]['meta']['regularMarketPrice'])


get_group.add_command(get_stock_price)

fancywallet.add_command(get_group)
