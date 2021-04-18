from unittest.mock import Mock

import pytest

from basket_price_calculator import Basket, BasketPriceCalculator, PriceResult
from models import BasketItem, OfferFreeProducts
from offer_applicability_resolver import OfferApplicabilityResolver


@pytest.fixture
def basket_mock():
    basket = Mock(spec_set=Basket)
    basket.get_items.return_value = []
    return basket


@pytest.fixture
def catalog():
    return {
        'shampoo': 2.50,
        'shampoo_large': 3.50,

    }


@pytest.fixture
def offer_applicability_resolver_mock():
    provider = Mock(spec_set=OfferApplicabilityResolver)
    provider.get_offers_applicable_for_basket_items.return_value = {}
    return provider


@pytest.fixture
def basket_price_calculator(catalog, offer_applicability_resolver_mock) -> BasketPriceCalculator:
    return BasketPriceCalculator(
        catalog=catalog,
        offer_applicability_resolver=offer_applicability_resolver_mock
    )


def test_calculate_price_for_empty_basket(basket_price_calculator, basket_mock):
    actual_price_result = basket_price_calculator.calculate_price(basket_mock)
    assert actual_price_result == PriceResult()


@pytest.mark.parametrize('basket_items, expected_result', [
    (
            [
                BasketItem(product_name='shampoo', quantity=1)
            ],
            PriceResult(sub_total=2.50, discount=0.00, total=2.50)
    ),
    (
            [BasketItem(product_name='shampoo', quantity=1),
             BasketItem(product_name='shampoo_large', quantity=1)],
            PriceResult(sub_total=6.0, discount=0.00, total=6.0)
    )
])
def test_calculate_price_when_there_is_no_offers(basket_price_calculator, basket_mock, basket_items, expected_result):
    basket_mock.get_items.return_value = basket_items
    assert basket_price_calculator.calculate_price(basket_mock) == expected_result


def test_calculate_price_when_no_offer_applies(basket_price_calculator, basket_mock, offer_applicability_resolver_mock):
    basket_mock.get_items.return_value = [BasketItem(product_name='shampoo', quantity=3)]
    offer_applicability_resolver_mock.get_offers_applicable_for_basket_items.return_value = {
        'shampoo': [OfferFreeProducts(
            product_name='shampoo',
            number_of_products_required_to_bought=5,
            number_of_free_products=2
        )]
    }

    assert basket_price_calculator.calculate_price(basket_mock) == PriceResult(sub_total=7.50, discount=0.00,
                                                                               total=7.50)


@pytest.mark.parametrize('basket_items, expected_result', [
    (
            # offer applies once, one product type in basket
            [BasketItem(product_name='shampoo', quantity=3)],
            PriceResult(sub_total=7.50, discount=2.50, total=5.00)
    ),
    (
            # offer applies twice, one product type in basket
            [BasketItem(product_name='shampoo', quantity=6)],
            PriceResult(sub_total=15.0, discount=5.00, total=10.0)
    ),
    (
            # offer applies twice, one product type in basket, some products not in offer
            [BasketItem(product_name='shampoo', quantity=8)],
            PriceResult(sub_total=20.0, discount=5.00, total=15.0)
    ),
    (
            # offer applies one, two product types in basket, some products not in offer
            [
                BasketItem(product_name='shampoo', quantity=4),
                BasketItem(product_name='shampoo_large', quantity=3)
            ],
            PriceResult(sub_total=20.50, discount=2.50, total=18.0)
    )
])
def test_calculate_price_when_single_offer_applies(basket_price_calculator, basket_mock,
                                                   offer_applicability_resolver_mock,
                                                   basket_items,
                                                   expected_result):
    basket_mock.get_items.return_value = basket_items
    offer_applicability_resolver_mock.get_offers_applicable_for_basket_items.return_value = {
        'shampoo': [
            OfferFreeProducts(
                product_name='shampoo',
                number_of_products_required_to_bought=3,
                number_of_free_products=1
            )]
    }

    result = basket_price_calculator.calculate_price(basket_mock)

    assert result == expected_result
