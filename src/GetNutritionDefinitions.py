import client

YOUR_API_ID = '1cdcf1a9'
YOUR_API_KEY = 'aa6f2e82587a6f95d0d155640537c26c'

# default option values
TIMEOUT = 5.0
RETRIES = 0

cl = client.Client(api_id=YOUR_API_ID, api_key=YOUR_API_KEY, timeout=TIMEOUT, retries=RETRIES)

r = cl.recipe('Pumpkin-Pie-Smoothie-Bowl-1873360')

pass

