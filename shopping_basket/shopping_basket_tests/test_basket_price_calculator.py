from unittest.mock import Mock

import pytest

from basket_price_calculator import Basket, BasketPriceCalculator, PriceResult
from models import Catalog, Offers


@pytest.fixture
def basket():
    return Basket()


@pytest.fixture
def catalog():
    return Mock(spec_set=Catalog)


@pytest.fixture
def offers():
    return Mock(spec_set=Offers)


@pytest.fixture
def basket_price_calculator(catalog, offers) -> BasketPriceCalculator:
    return BasketPriceCalculator(
        catalog=catalog,
        offers=offers
    )


def test_calculate_price_for_empty_basket(basket_price_calculator, basket):
    actual_price_result = basket_price_calculator.calculate_price(basket)
    assert actual_price_result == PriceResult()
