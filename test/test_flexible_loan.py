import unittest
from okx.Finance import FlexibleLoan
from test.config import get_api_credentials
from okx.transport import Transport


class FlexibleLoanTest(unittest.TestCase):
    def setUp(self):
        api_key, api_secret_key, passphrase, flag = get_api_credentials()
        self.FlexibleLoanAPI = FlexibleLoan.FlexibleLoanAPI(Transport(api_key, api_secret_key, passphrase, flag=flag))

    def test_borrow_currencies(self):
        print(self.FlexibleLoanAPI.borrow_currencies())

    def test_collateral_assets(self):
        print(self.FlexibleLoanAPI.collateral_assets())

    def test_max_loan(self):
        print(self.FlexibleLoanAPI.max_loan(borrowCcy='USDT'))

    def test_max_collateral_redeem_amount(self):
        print(self.FlexibleLoanAPI.max_collateral_redeem_amount(ccy='USDT'))

    def test_adjust_collateral(self):
        print(self.FlexibleLoanAPI.adjust_collateral(type="add", collateralCcy="USDT", collateralAmt="1"))

    def test_loan_info(self):
        print(self.FlexibleLoanAPI.loan_info())

    def test_loan_history(self):
        print(self.FlexibleLoanAPI.loan_history())

    def test_interest_accrued(self):
        print(self.FlexibleLoanAPI.interest_accrued())

if __name__ == "__main__":
    unittest.main()