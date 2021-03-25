import time

from brownie import (MockToken, Multicall, PureChef, PureMaker, PureSwapERC20,
                     PureSwapFactory, PureSwapRouter, PureToken, SingleChef,
                     accounts, network)
from brownie.network.state import Chain

mnemonic = ''

network_name = network.show_active()
print(network_name)
chain = Chain()
if (network_name == "development"):
    accs = accounts.from_mnemonic(mnemonic, count=10)
    acc = accs[0]
    accounts.default = acc
    wht = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
elif (network_name == "heco-test"):
    accs = accounts.from_mnemonic(mnemonic, count=10)
    acc = accs[0]
    accounts.default = acc
    int_code_hash = 'e9ec638a7c00adfcf6a084b7c668bbcbb534e5945dc30b189617b8fb96e39347'
    # todo
    mx_address = ''
    wht = '0x7af326b6351c8a9b8fb8cd205cbe11d4ac5fa836'
    # husd = '0x8Dd66eefEF4B503EB556b1f50880Cc04416B916B'
    # husdt = '0x04F535663110A392A6504839BEeD34E019FdB4E0'
    # hbtc = '0x1D8684e6CdD65383AfFd3D5CF8263fCdA5001F13'
    mx = ''

    # wbtc = '0x84C6Ae2888f954Ea041fc541408d302F163f8194'
    # link = '0x3E24e9d2c824B0ac2C82edc931B67252099B8e79'
    # snx = '0x087Ed0d3CA0Ed342AD4Ad3439F8174b41e2Ba47D'
    # usdc = '0xd459Dad367788893c17c09e17cFBF0bf25c62833'
    # dai = '0x60d64Ef311a4F0E288120543A14e7f90E76304c6'
    # heth = '0xfeB76Ae65c11B363Bd452afb4A7eC59925848656'
    pure_chef_address = '0xd5307B0922A80f852e3AEE38c1885a8040eea7BB'
    factory_address = '0x50804ca026A0E9e4bF28ce4e360C06E03cBfC57C'
elif (network_name == "bsc-test"):
    accs = accounts.from_mnemonic(mnemonic, count=10)
    acc = accs[0]
    print(acc)
    # exit(0)
    accounts.default = acc
    wht = "0xae13d989dac2f0debff460ac112a837c89baa7cd"
elif (network_name == "bsc-mainnet"):
    wht = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"

    

def main():
    # factory
    factory = fac()
    # router
    router = PureSwapRouter.deploy(factory.address, wht)
    # token
    pureToken = token()
    mxToken = mx()
    
    # PureMaker
    makerPure = maker(factory, pureToken)
    makerMx = maker(factory, pureToken)
    factory.setFeeTo(makerPure.address, makerMx.address)
    pureChef = pure_chef(pureToken, 3*10**18, chain.height+20)
    singleChef = single_chef(pureToken, 0.6*10**18, chain.height+20)
    add_liqui(router, pureToken.address)
    add_lpfarm(factory, pureChef)
    add_singleFarm(singleChef, [pureToken.address, mxToken.address])
    approve(pureToken, pureChef, 0.51)
    approve(pureToken, singleChef, 0.1)
    # add_liqui_local()

def fac():
    factory = PureSwapFactory.deploy(acc)
    hash = factory.pairCodeHash()
    print(hash)
    return factory

def token():
    return PureToken.deploy(acc)

def mx():
    return MockToken.deploy("MX", "MX", 18)

def maker(fac, token):
    return PureMaker.deploy(fac.address, token.address, wht)

def add_liqui(router, pure_address):
    if (network_name == 'development'):
        add_liqui_local()
    else:
        busd = MockToken.deploy("BUSD", "BUSD", 18).address
        usdt = MockToken.deploy("USDT", "USDT", 6).address
        btcb = MockToken.deploy("BTCB", "BTCB", 18).address
        print("Pure: {}\n BTCB: {}\n BUSD: {}\n USDT: {}".format(pure_address, btcb, busd, usdt))
        token0s = [pure_address, pure_address, pure_address, pure_address, busd]
        token1s = [btcb, busd, usdt, wht, wht]
        for i in range(len(token0s)):
            if (token1s[i] == busd):
                _add_liqui(router, token0s[i], token1s[i], 100000, 10000)
            elif (token1s[i] == usdt):
                _add_liqui(router, token0s[i], token1s[i], 100000, 10000, 6)
            elif (token1s[i] == btcb):
                _add_liqui(router, token0s[i], token1s[i], 100000, 10000/54000)
            elif (token1s[i] == wht):
                if (token0s[i] == pure_address):
                    add_bnb_pure_liqui(router, token0s[i], 1000, 0.5)
                else:
                    add_bnb_pure_liqui(router, token0s[i], 100, 0.5)


def _add_liqui(router, token0Address, token1Address, amount0, amount1, decimal=18):
    print(token0Address, token1Address)
    token0 = PureToken.at(token0Address)
    token1 = MockToken.at(token1Address)
    token0.approve(router.address, 1000000*10**18)
    token1.approve(router.address, 1000000*10**decimal)
    router.addLiquidity(token0Address, token1Address, int(amount0*10**18), int(amount1*10**decimal), int(amount0/2*10**18), int(amount1/2*10**decimal), accs[0], int(time.time())+100, {'allow_revert': True, 'gas_limit': 6954088}) 

def add_bnb_pure_liqui(router, tokenAddr, amount0, bnb_amount):
    # router = PureSwapRouter.at('0x6721A6cdf88E279F95032132077a78899514B347')
    router.addLiquidityETH(tokenAddr, amount0*10**18, amount0*10**18, bnb_amount**10**18, acc, int(time.time())+100, {'amount': bnb_amount*10**18, 'allow_revert': True, 'gas_limit': 6954088})
    # router.addLiquidityETH(token1Addr, amount0*10**18, 1000*10**18, 0.5**10**18, acc, int(time.time())+100, {'amount': 0.5*10**18})

def add_liqui_local():
    usdc = MockToken.deploy("USDC", "USDC", 6)
    dai = MockToken.deploy("DAI", "DAI", 18)
    usdc.approve(PureSwapRouter[0].address, 100*10**18)
    dai.approve(PureSwapRouter[0].address, 100*10**18)
    print(int(time.time())+1000)
    tx = PureSwapRouter[0].addLiquidity(usdc.address, dai.address, 10*10**6, 10*10**18, 5*10**6, 5*10**18, accs[1], int(time.time())+1000)
    # print(tx.call_trace())

def pure_chef(pureToken, purePerBlock, startBlock):
    return PureChef.deploy(pureToken.address, purePerBlock, startBlock)

def single_chef(pureToken, purePerBlock, startBlock):
    return SingleChef.deploy(pureToken.address, purePerBlock, startBlock)

def add_lpfarm(factory, chef):
    # ht
    for i in range(5):
        pair = factory.allPairs(i)
        print("Pair address:", pair)
        chef.add(100, pair, True, {'allow_revert': True, 'gas_limit': 6954088})

def add_singleFarm(chef, tokens):
    for t in tokens:
        chef.add(100, t, True)

def approve(token, chef, ratio):
    token.approve(chef.address, 125000000*ratio*10**18)

def multicall():
    mc = Multicall.deploy()

def transfer_lp():
    factory = PureSwapFactory[0]
    for i in range(3):
        pair = factory.allPairs(i)
        print("Pair address:", pair)
        _transfer_lp(PureSwapERC20.at(pair), '0x5D874e9b82A2c4984e3E520C927c8D19E8F70398', 0.3)

def _transfer_lp(token, to, ratio):
    bal = token.balanceOf(accs[1])
    print(bal)
    if (bal != 0):
        token.transfer(to, int(bal*ratio), {'from': accs[1]})
    else:
        raise Exception("not enought lp")

def transfer_token():
    # users = ['0x9ce864ad7d1c19746a1438F3803D306fEd158275', '0x5D874e9b82A2c4984e3E520C927c8D19E8F70398']
    users = ['0xdA7849f86A8E3b75EAe83562C577B058F094Bb05', '0xa3C5A5f5bcD29aE08Ba2D62c43D8eA742Dd6edd9', '0x9ce864ad7d1c19746a1438F3803D306fEd158275', '0x5D874e9b82A2c4984e3E520C927c8D19E8F70398']
    mock_tokens = [
      "0x89fE8DdD4aD3d72a99d6f0F4141D73E64d3Af75a",
      "0x7de426D027f33FD8FA59adfD733A99f974781bf4",
      "0xB2e59F7bA3Be8E72a2324Dc39D4f4896daa42365",
      "0x920084a10f03DA45Cfd98fd2a388575c934DaEeA",
      "0x9CB09Ee4bCD56d1C622F93297FFEf9c976651263"
    ]
    for u in users:
        for t in mock_tokens:
            if (t == "0x9CB09Ee4bCD56d1C622F93297FFEf9c976651263"):
                token = PureToken.at(t)
            else:
                token = MockToken.at(t)
            if (t == "0x7de426D027f33FD8FA59adfD733A99f974781bf4"):
                deci = 6
            else:
                deci = 18
            token.transfer(u, 1000000 * 10**deci)

def add_pool():
    factory = PureSwapFactory.at(factory_address)
    pc = PureChef.at(pure_chef_address)
    amountPair = factory.allPairsLength()
    print(amountPair)
    assert amountPair == 7
    lp_address = factory.allPairs(6)
    print(lp_address)
    pc.add(400, lp_address, True)
