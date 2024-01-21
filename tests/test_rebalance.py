import pytest
from pyfinance.rebalance import Asset, RebalanceAssets

def test_current_percentage():
    asset = Asset('Asset1', 20, 1000)
    assert asset.current_percentage(5000) == 20

def test_send_to():
    asset1 = Asset('Asset1', 20, 1000, rebalanced_value=900)
    asset2 = Asset('Asset2', 30, 1500, rebalanced_value=1600)
    asset1.send_to(asset2, 100)
    assert asset1.sending_to[asset2] == 100
    assert asset2.reciving_from[asset1] == 100
    assert asset1.how_much_send() == 0
    assert asset1.how_much_recive() <= 0
    assert asset2.how_much_recive() == 0
    assert asset2.how_much_send() <= 0

@pytest.fixture
def rebalance_assets():
    assets = [Asset('Asset1', 20, 1000), Asset('Asset2', 30, 1500)]
    return RebalanceAssets(assets, 10)

def test_rebalance():
    # Call the _rebalance method
    asset1 = Asset('Asset1', 50, 1000)
    asset2 = Asset('Asset2', 50, 1500)
    assets = [asset1, asset2]
    rebalance = RebalanceAssets(assets, 9)  # 9% threshold because 10% is the asset1, asset2 threeshold
    assert rebalance.has_to_be_rebalanced == True
    # They give and recive all
    assert asset1.how_much_recive() == 0
    assert asset2.how_much_send() == 0
    # They never send or recive if they do not can initally
    assert asset1.how_much_send() <= 0
    assert asset2.how_much_recive() <= 0
    # They are rebalanced
    assert asset1.rebalanced_value == 1250
    assert asset2.rebalanced_value == 1250
    # They send and recive the same amount
    assert asset1.reciving_from[asset2] == 250
    assert len(asset1.reciving_from) == 1
    assert len(asset1.sending_to) == 0
    assert asset2.sending_to[asset1] == 250
    assert len(asset2.sending_to) == 1
    assert len(asset2.reciving_from) == 0

def test_no_rebalance():
    # Call the _rebalance method
    asset1 = Asset('Asset1', 50, 1000)
    asset2 = Asset('Asset2', 50, 1500)
    assets = [asset1, asset2]
    rebalance = RebalanceAssets(assets, 10)  # 9% threshold because 10% is the asset1, asset2 threeshold
    assert rebalance.has_to_be_rebalanced == False


def test_rebalance_investopedia_example():
    """ Test the rebalance method with the example from Investopedia.
    
    Here's a simple example. Bob has $100,000 to invest. He decides to invest 50% in a bond fund, 10% in a Treasury fund, and 40% in an equity fund.

    At the end of the year, Bob's $40,000 investment in the equity fund has grown to $55,000; an increase of 37%. Conversely, the bond fund suffered,
    realizing a loss of 5%, but the Treasury fund realized a modest increase of 4%.
    """
    goal = [50, 10, 40]
    current = [42, 9, 49]
    total = 100000
    total_current = 112900
    current_value = [total_current * percentage / 100 for percentage in current]
    asset1 = Asset('Bond fund', 50, current_value[0])
    asset2 = Asset('Treasury fund', 10, current_value[1])
    asset3 = Asset('Equity fund', 40, current_value[2])
    assets = [asset1, asset2, asset3]
    rebalance = RebalanceAssets(assets, 5)
    assert rebalance.has_to_be_rebalanced == True
    # Which recive and which send?
    assert asset1.how_much_recive() == 0
    assert asset2.how_much_recive() == 0
    assert asset3.how_much_recive() <= 0
    assert asset1.how_much_send() <= 0
    assert asset2.how_much_send() <= 0
    assert asset3.how_much_send() == 0
    # They are rebalanced
    rebalanced = [ total_current * i / 100 for i in goal ] # [56450.0, 11290.0, 45160.0]
    assert asset1.rebalanced_value == 56450.0
    assert asset2.rebalanced_value == 11290.0
    assert asset3.rebalanced_value == 45160.0
    # They send and recive the same amount
    assert asset1.reciving_from[asset3] == asset1.rebalanced_value - asset1.value
    assert len(asset1.reciving_from) == 1
    assert len(asset1.sending_to) == 0
    assert asset2.reciving_from[asset3] == asset2.rebalanced_value - asset2.value
    assert len(asset2.reciving_from) == 1
    assert len(asset2.sending_to) == 0
    assert asset3.sending_to[asset1] == asset1.rebalanced_value - asset1.value
    assert asset3.sending_to[asset2] == asset2.rebalanced_value - asset2.value
    assert len(asset3.sending_to) == 2
    assert len(asset3.reciving_from) == 0
    
