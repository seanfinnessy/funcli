from click.testing import CliRunner
import unittest
from fancywallet import fancywallet


class FancyWalletGetPriceTests(unittest.TestCase):
    def test_get_price_tsla_lower(self):
        runner = CliRunner()
        result = runner.invoke(fancywallet, ['get', 'price', 'tsla'])
        self.assertEqual(result.exit_code, 0)

    def test_get_price_tsla_upper(self):
        runner = CliRunner()
        result = runner.invoke(fancywallet, ['get', 'price', 'TSLA'])
        self.assertEqual(result.exit_code, 0)

    def test_get_price_unknown(self):
        company = 'unknown'
        runner = CliRunner()
        result = runner.invoke(fancywallet, ['get', 'price', company])
        self.assertEqual(result.output, f'Company {company} not found!\n')


# wires everything up and converts this to an actual test file for us to run.
if __name__ == '__main__':
    unittest.main()
