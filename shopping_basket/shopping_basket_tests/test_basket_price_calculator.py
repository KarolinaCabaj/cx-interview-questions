from unittest.mock import Mock

import pytest

from basket_price_calculator import Basket, BasketPriceCalculator, PriceResult
from models import Catalog, Offers, Product


@pytest.fixture
def basket_mock():
    basket = Mock(spec_set=Basket)
    basket.get_products.return_value = []
    return basket


@pytest.fixture
def catalog_mock():
    return Mock(spec_set=Catalog)


@pytest.fixture
def offers_mock():
    return Mock(spec_set=Offers)


@pytest.fixture
def basket_price_calculator(catalog_mock, offers_mock) -> BasketPriceCalculator:
    return BasketPriceCalculator(
        catalog=catalog_mock,
        offers=offers_mock
    )


def test_calculate_price_for_empty_basket(basket_price_calculator, basket_mock):
    actual_price_result = basket_price_calculator.calculate_price(basket_mock)
    assert actual_price_result == PriceResult()


@pytest.mark.parametrize('basket_products, expected_result', [
    (
            [Product(name='shampoo', price=2.50)],
            PriceResult(sub_total=2.50, discount=0.00, total=2.50)
    ),
    (
            [Product(name='shampoo', price=2.50), Product(name='shampoo_large', price=3.50)],
            PriceResult(sub_total=6.0, discount=0.00, total=6.0))
])
def test_calculate_price_when_no_offer_applies(basket_price_calculator, basket_mock, basket_products, expected_result):
    basket_mock.get_products.return_value = basket_products
    assert basket_price_calculator.calculate_price(basket_mock) == expected_result
