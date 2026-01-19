from pyfinance import asset as pfasset

def test_load_assets():
    pfasset.load_assets()
    assert len(pfasset.assets) == 4
    # First asset: US Equity,30,VANGUARD US 500 STOCK EUR INS,IE0032126645,VANUIEUR,0.1
    assert pfasset.assets[0].asset_type == 'US Equity'
    assert pfasset.assets[0].percentage == 30
    assert pfasset.assets[0].product == 'VANGUARD US 500 STOCK EUR INS'
    assert pfasset.assets[0].isin == 'IE0032126645'
    assert pfasset.assets[0].ticker == 'VANUIEUR'
    assert pfasset.assets[0].expenses == 0.1
    # Fourth asset: Japan Equity,10,Vanguard Japan Stock Index Fund EUR Acc,IE0007286036,VANSTEUR,0.16
    assert pfasset.assets[3].asset_type == 'Japan Equity'
    assert pfasset.assets[3].percentage == 10
    assert pfasset.assets[3].product == 'Vanguard Japan Stock Index Fund EUR Acc'
    assert pfasset.assets[3].isin == 'IE0007286036'
    assert pfasset.assets[3].ticker == 'VANSTEUR'
    assert pfasset.assets[3].expenses == 0.16
