from unittest.mock import Mock

import pytest

from basket_price_calculator import Basket, BasketPriceCalculator, PriceResult
from models import BasketItem, OfferFreeProducts, OffersProvider, Product


@pytest.fixture
def basket_mock():
    basket = Mock(spec_set=Basket)
    basket.get_items.return_value = []
    return basket


@pytest.fixture
def catalog():
    return {}


@pytest.fixture
def offers_provider_mock():
    provider = Mock(spec_set=OffersProvider)
    provider.get_offer_for_product.return_value = []
    return provider


@pytest.fixture
def basket_price_calculator(catalog, offers_provider_mock) -> BasketPriceCalculator:
    return BasketPriceCalculator(
        catalog=catalog,
        offers_provider=offers_provider_mock
    )


def test_calculate_price_for_empty_basket(basket_price_calculator, basket_mock):
    actual_price_result = basket_price_calculator.calculate_price(basket_mock)
    assert actual_price_result == PriceResult()


@pytest.mark.parametrize('basket_items, expected_result', [
    (
            [
                BasketItem(product=Product(name='shampoo', price=2.50), quantity=1)
            ],
            PriceResult(sub_total=2.50, discount=0.00, total=2.50)
    ),
    (
            [BasketItem(product=Product(name='shampoo', price=2.50), quantity=1),
             BasketItem(product=Product(name='shampoo_large', price=3.50), quantity=1)],
            PriceResult(sub_total=6.0, discount=0.00, total=6.0)
    )
])
def test_calculate_price_when_there_is_no_offers(basket_price_calculator, basket_mock, basket_items, expected_result):
    basket_mock.get_items.return_value = basket_items
    assert basket_price_calculator.calculate_price(basket_mock) == expected_result


def test_calculate_price_when_no_offer_applies(basket_price_calculator, basket_mock, offers_provider_mock):
    shampoo = Product(name='shampoo', price=2.50)
    basket_mock.get_items.return_value = [BasketItem(product=shampoo, quantity=3)]
    offers_provider_mock.get_offer_for_product.return_value = [
        OfferFreeProducts(
            product_name='shampoo',
            number_of_products_required_to_bought=5,
            number_of_free_products=2
        )
    ]

    assert basket_price_calculator.calculate_price(basket_mock) == PriceResult(sub_total=7.50, discount=0.00,
                                                                               total=7.50)


@pytest.mark.parametrize('basket_items, expected_result', [
    (
            # offer applies once, one product type in basket
            [BasketItem(product=Product(name='shampoo', price=2.50), quantity=3)],
            PriceResult(sub_total=7.50, discount=2.50, total=5.00)
    ),
    (
            # offer applies twice, one product type in basket
            [BasketItem(product=Product(name='shampoo', price=2.50), quantity=6)],
            PriceResult(sub_total=15.0, discount=5.00, total=10.0)
    ),
    (
            # offer applies twice, one product type in basket, some products not in offer
            [BasketItem(product=Product(name='shampoo', price=2.50), quantity=8)],
            PriceResult(sub_total=20.0, discount=5.00, total=15.0)
    ),
    (
            # offer applies one, two product types in basket, some products not in offer
            [
                BasketItem(product=Product(name='shampoo', price=2.50), quantity=4),
                BasketItem(product=Product(name='shampoo_large', price=3.50), quantity=3)
            ],
            PriceResult(sub_total=20.50, discount=2.50, total=18.0)
    )
])
def test_calculate_price_when_single_offer_applies(basket_price_calculator, basket_mock, offers_provider_mock, basket_items,
                                                   expected_result):
    basket_mock.get_items.return_value = basket_items
    offers_provider_mock.get_offer_for_product.return_value = [
        OfferFreeProducts(
            product_name='shampoo',
            number_of_products_required_to_bought=3,
            number_of_free_products=1
        )
    ]

    result = basket_price_calculator.calculate_price(basket_mock)

    assert result == expected_result
