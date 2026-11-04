import unittest
from okx.Finance import Savings
from test.config import get_api_credentials
from okx.transport import Transport


class SavingsTest(unittest.TestCase):
    def setUp(self):
        api_key, api_secret_key, passphrase, flag = get_api_credentials()
        self.StackingAPI = Savings.SavingsAPI(Transport(api_key, api_secret_key, passphrase, flag=flag))


    def test_get_saving_balance(self):
        print(self.StackingAPI.get_saving_balance(ccy='USDT'))

    def test_savings_purchase_redemption(self):
        print(self.StackingAPI.savings_purchase_redemption(ccy='USDT',amt="0.1",side="redempt",rate="1"))

    def test_set_lending_rate(self):
        print(self.StackingAPI.set_lending_rate(ccy='USDT',rate="1"))

    def test_get_lending_history(self):
        print(self.StackingAPI.get_lending_history(ccy='USDT'))

    def test_get_public_borrow_history(self):
        print(self.StackingAPI.get_public_borrow_history(ccy='USDT'))

    def test_get_public_borrow_info(self):
        print(self.StackingAPI.get_public_borrow_info(ccy='BTC'))

if __name__ == "__main__":
    unittest.main()