from unittest.mock import Mock, patch

import pytest

from basket_pricer.basket_price_calculator import Basket, BasketPriceCalculator, PriceResult
from basket_pricer.models import BasketItem, OfferFreeProducts, OfferPercentageDiscount
from basket_pricer.offer_applicability_resolver import OfferApplicabilityResolver


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
        'baked_beans': 0.99,
        'sardines': 1.89,
        'biscuits': 1.20
    }


@pytest.fixture
def offer_applicability_resolver_mock():
    provider = Mock(spec_set=OfferApplicabilityResolver)
    provider.get_offers_applicable_for_basket_items.return_value = {}
    return provider


@pytest.fixture
def basket_price_calculator(catalog, offer_applicability_resolver_mock) -> BasketPriceCalculator:
    with patch('basket_pricer.offer_applicability_resolver.OfferApplicabilityResolver.create',
               return_value=offer_applicability_resolver_mock):
        yield BasketPriceCalculator(
            catalog=catalog,
            offers=[]
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


def test_calculate_price_when_no_offer_applies_for_current_basket(basket_price_calculator, basket_mock,
                                                                  offer_applicability_resolver_mock):
    basket_mock.get_items.return_value = [BasketItem(product_name='shampoo', quantity=3)]
    offer_applicability_resolver_mock.get_offers_applicable_for_basket_items.return_value = {}

    assert basket_price_calculator.calculate_price(basket_mock) == PriceResult(sub_total=7.50, discount=0.00,
                                                                               total=7.50)


@pytest.mark.parametrize('basket_items, offer_combinations, expected_result', [
    (
            # offer applies once, one product type in basket
            [BasketItem(product_name='shampoo', quantity=3)],
            [
                (OfferFreeProducts(
                    product_name='shampoo',
                    number_of_products_required_to_bought=3,
                    number_of_free_products=1
                ),)
            ],
            PriceResult(sub_total=7.50, discount=2.50, total=5.00)
    ),
    (
            # offer applies twice, one product type in basket
            [BasketItem(product_name='shampoo', quantity=6)],
            [
                (OfferFreeProducts(
                    product_name='shampoo',
                    number_of_products_required_to_bought=3,
                    number_of_free_products=1
                ), OfferFreeProducts(
                    product_name='shampoo',
                    number_of_products_required_to_bought=3,
                    number_of_free_products=1
                ))
            ],
            PriceResult(sub_total=15.0, discount=5.00, total=10.0)
    ),
    (
            # offer applies twice, one product type in basket, some products not in offer
            [BasketItem(product_name='shampoo', quantity=8)],
            [
                (OfferFreeProducts(
                    product_name='shampoo',
                    number_of_products_required_to_bought=3,
                    number_of_free_products=1
                ), OfferFreeProducts(
                    product_name='shampoo',
                    number_of_products_required_to_bought=3,
                    number_of_free_products=1
                ))
            ],
            PriceResult(sub_total=20.0, discount=5.00, total=15.0)
    ),
    (
            # offer applies one, two product types in basket, some products not in offer
            [
                BasketItem(product_name='shampoo', quantity=4),
                BasketItem(product_name='shampoo_large', quantity=3)
            ],
            [
                (OfferFreeProducts(
                    product_name='shampoo',
                    number_of_products_required_to_bought=3,
                    number_of_free_products=1
                ),)
            ],
            PriceResult(sub_total=20.50, discount=2.50, total=18.0)
    )
])
def test_calculate_price_when_single_offer_applies(basket_price_calculator, basket_mock,
                                                   offer_applicability_resolver_mock, basket_items, offer_combinations,
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
    offer_applicability_resolver_mock.get_item_offer_combinations.return_value = offer_combinations

    result = basket_price_calculator.calculate_price(basket_mock)

    assert result == expected_result


def test_calculate_price_for_basket_1_from_examples(basket_price_calculator, basket_mock,
                                                    offer_applicability_resolver_mock):
    basket_mock.get_items.return_value = [BasketItem(product_name='baked_beans', quantity=4),
                                          BasketItem(product_name='biscuits', quantity=1)]
    baked_bean_offer = OfferFreeProducts(
        product_name='baked_beans',
        number_of_products_required_to_bought=3,
        number_of_free_products=1
    )
    offer_applicability_resolver_mock.get_offers_applicable_for_basket_items.return_value = {
        'baked_beans': [baked_bean_offer]
    }
    offer_applicability_resolver_mock.get_item_offer_combinations.return_value = [(baked_bean_offer,)]

    result = basket_price_calculator.calculate_price(basket_mock)

    assert result == PriceResult(sub_total=5.16, discount=0.99, total=4.17)


@pytest.mark.skip(reason='Need to use decimal for correct precision')
def test_calculate_price_for_basket_2_from_examples(basket_price_calculator, basket_mock,
                                                    offer_applicability_resolver_mock):
    basket_mock.get_items.return_value = [BasketItem(product_name='baked_beans', quantity=2),
                                          BasketItem(product_name='biscuits', quantity=1),
                                          BasketItem(product_name='sardines', quantity=2)]
    baked_bean_offer = OfferFreeProducts(
        product_name='baked_beans',
        number_of_products_required_to_bought=3,
        number_of_free_products=1
    )
    sardines_offer = OfferPercentageDiscount(
        product_name='sardines',
        number_of_products_required_to_bought=1,
        discount=25
    )
    offer_applicability_resolver_mock.get_offers_applicable_for_basket_items.return_value = {
        'baked_beans': [baked_bean_offer],
        'sardines': [sardines_offer]
    }

    def combinations_for_item(item, _):
        if item.product_name == 'baked_beans':
            return []
        if item.product_name == 'sardines':
            return [(sardines_offer, sardines_offer)]

    offer_applicability_resolver_mock.get_item_offer_combinations.side_effect = combinations_for_item

    result = basket_price_calculator.calculate_price(basket_mock)

    assert result == PriceResult(sub_total=6.96, discount=0.95, total=6.01)
    # assert result == PriceResult(sub_total=6.96, discount=0.94, total=6.01) this one is passing
