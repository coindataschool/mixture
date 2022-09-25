# Authors: Coin Data School <coindataschool@gmail.com>
# License: MIT License
import requests
import datetime as dt
import pandas as pd

TVL_BASE_URL = "https://api.llama.fi"
COINS_BASE_URL = "https://coins.llama.fi"
STABLECOINS_BASE_URL = "https://stablecoins.llama.fi"
YIELDS_BASE_URL = "https://yields.llama.fi"
ABI_DECODER_BASE_URL = "https://abi-decoder.llama.fi"

class DefiLlama:
    """ 
    Implements functions for calling DeFi Llama's API and tidying up responses. 
    """

    def __init__(self):
        self.session = requests.Session()

    def _tidy_frame_tvl(self, df):
        """Set `date` of input data frame as index and shorten TVL column name.
        
        Parameters
        ----------
        df : data frame 
            Must contains two columns: `date` and 'totalLiquidityUSD'.
        Returns 
        -------
        data frame
        """
        df['date'] = df.date.apply(lambda x: dt.datetime.utcfromtimestamp(int(x)))
        df = df.set_index('date').rename(columns={'totalLiquidityUSD': 'tvl'})
        return df

    def _get(self, api_name, endpoint, params=None):
        """Send 'GET' request.

        Parameters
        ----------
        api_name : string
            Which API to call. Possible values are 'TVL', 'COINS', 'STABLECOINS',
            'YIELDS', and 'ABI_DECODER'. Each type has a different base url.
        endpoint : string 
            Endpoint to be added to base URL.
        params : dictionary
            HTTP request parameters.
        
        Returns
        -------
        JSON response
        """
        if api_name == 'TVL':
            url = TVL_BASE_URL + endpoint
        elif api_name == 'COINS':
            url = COINS_BASE_URL + endpoint  
        elif api_name == 'STABLECOINS':    
            url = STABLECOINS_BASE_URL + endpoint
        elif api_name == 'YIELDS':
            url = YIELDS_BASE_URL + endpoint 
        else: 
            url = ABI_DECODER_BASE_URL + endpoint
        return self.session.request('GET', url, params=params, timeout=30).json()

    def get_protocol_curr_tvl(self, protocol):
        """Get current TVL of a protocol.

        Parameters
        ----------
        protocol : string
            Protocol name.
        
        Returns 
        -------
        float
        """
        return self._get('TVL', f'/tvl/{protocol}')

    def get_chains_curr_tvl(self):
        """Get current TVL of all chains.
        
        Returns 
        -------
        data frame
        """
        resp = self._get('TVL', f'/chains/')
        df = pd.DataFrame(resp).loc[:, ['name', 'tokenSymbol', 'tvl']]
        df = df.rename(columns={'name':'chain', 'tokenSymbol':'token'})
        return df

    def get_defi_hist_tvl(self):
        """Get historical TVL of DeFi on all chains.

        Returns 
        -------
        data frame
        """
        resp = self._get('TVL', '/charts')
        df = pd.DataFrame(resp)
        return self._tidy_frame_tvl(df)

    def get_chain_hist_tvl(self, chain):
        """Get historical TVL of a chain.

        Parameters
        ----------
        chain : string
            Chain name.
        
        Returns 
        -------
        data frame
        """
        resp = self._get('TVL', f'/charts/{chain}')
        df = pd.DataFrame(resp)
        return self._tidy_frame_tvl(df)
        
    def get_protocols(self):
        """Get detailed information on all protocols. 
        
        Returns 
        -------
        data frame
        """
        return pd.DataFrame(self._get('TVL', '/protocols'))

    def get_protocols_fundamentals(self):
        """Get current TVL, MCap, FDV, 1d and 7d TVL % change on all protocols.
        
        Parameters
        ----------
        protocol : string
            Protocol name.
        
        Returns 
        -------
        data frame
        """
        df = pd.DataFrame(self._get('TVL', '/protocols'))
        cols = ['name', 'symbol', 'chain', 'category', 'chains', 
                'tvl', 'change_1d', 'change_7d', 
                'fdv', 'mcap', 'forkedFrom']
        df = df.loc[:, cols].rename(columns={'forkedFrom':'forked_from'})
        return df

    def get_protocol(self, protocol):
        """Get detailed info on a protocol and breakdowns by token and chain.
        
        Parameters
        ----------
        protocol : string
            Protocol name.
        
        Returns 
        -------
        dictionary
        """
        return self._get('TVL', f'/protocol/{protocol}')

    def get_protocol_curr_tvl_by_chain(self, protocol):
        """Get current TVL of a protocol.

        Parameters
        ----------
        protocol : string
            Protocol name.
        
        Returns 
        -------
        data frame
        """
        dd = self.get_protocol(protocol)['currentChainTvls']
        if 'staking' in dd:
            dd.pop('staking')
        ss = pd.Series(dd)
        ss.name='tvl'
        return ss.to_frame()
    
    def get_protocol_hist_tvl_by_chain(self, protocol):
        """Get historical TVL of a protocol by chain.

        Parameters
        ----------
        protocol : string
            Protocol name.
        
        Returns 
        -------
        dict of data frames
        """
        dd = self.get_protocol(protocol)
        d1 = dd['currentChainTvls']
        if 'staking' in d1:
            d1.pop('staking')
        chains = list(d1.keys())
        return {chain: self._tidy_frame(pd.DataFrame(dd['chainTvls'][chain]['tvl'])) for chain in chains}

    def _tidy_frame_price(self, resp):
        # convert json response to data frame
        ha = pd.DataFrame([item.split(':') for item in resp['coins'].keys()])
        ha.columns = ['chain', 'token_address']
        df = ha.join(pd.DataFrame([v for k, v in resp['coins'].items()]))
        # convert epoch timestamp to human-readable datetime
        df['timestamp'] = df.timestamp.apply(
            lambda x: dt.datetime.utcfromtimestamp(int(x)))
        return df

    def get_tokens_curr_prices(self, token_addrs_n_chains):
        """Get current prices of tokens by contract address.

        Parameters
        ----------
        token_addrs_n_chains : dictionary
            Each key is a token address; each value is a chain where the token 
            address resides. If getting price from coingecko, use token name as 
            key and 'coingecko' as value. For example, 
            {'0xdF574c24545E5FfEcb9a659c229253D4111d87e1':'ethereum',
             'ethereum':'coingecko'}

        Returns 
        -------
        data frame
        """
        ss = ','.join([v + ':' +k for k, v in token_addrs_n_chains.items()])
        resp = self._get('COINS', f'/prices/current/{ss}')
        df = self._tidy_frame_price(resp)
        return df.loc[:, ['timestamp', 'symbol', 'price', 'confidence', 
                          'chain', 'token_address', 'decimals']]

    def get_tokens_hist_snapshot_prices(self, token_addrs_n_chains, timestamp):
        """Get historical snapshot prices of tokens by contract address.

        Parameters
        ----------
        token_addrs_n_chains : dictionary
            Each key is a token address; each value is a chain where the token 
            address resides. If getting price from coingecko, use token name as 
            key and 'coingecko' as value. For example, 
            {'0xdF574c24545E5FfEcb9a659c229253D4111d87e1':'ethereum',
             'ethereum':'coingecko'}
        timestamp : string
            Human-readable timestamp, for example, '2021-09-25 00:27:53'

        Returns 
        -------
        data frame
        """
        ss = ','.join([v + ':' +k for k, v in token_addrs_n_chains.items()])
        unix_ts = pd.to_datetime(timestamp).value / 1e9
        resp = self._get('COINS', f'/prices/historical/{unix_ts}/{ss}')
        df = self._tidy_frame_price(resp)
        return df.loc[:, ['timestamp', 'symbol', 'price', 'chain', 'token_address', 'decimals']]

    def get_closest_block(self, chain, timestamp):
        """Get the closest block to a timestamp.

        Parameters
        ----------
        chain : string
            Name of the chain.
        timestamp : string
            Human-readable timestamp, for example, '2021-09-25 00:27:53'.

        Returns 
        -------
        data frame
        """
        unix_ts = pd.to_datetime(timestamp).value / 1e9
        resp = self._get('COINS', f'/block/{chain}/{unix_ts}')
        df = pd.DataFrame(resp, index=range(1))
        df['timestamp'] = df.timestamp.apply(
            lambda x: dt.datetime.utcfromtimestamp(int(x)))
        return df