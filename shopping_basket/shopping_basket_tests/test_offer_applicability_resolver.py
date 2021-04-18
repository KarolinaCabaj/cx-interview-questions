from unittest.mock import Mock

import pytest

from models import BasketItem, OfferFreeProducts, OfferPercentageDiscount, OffersProvider
from offer_applicability_resolver import OfferApplicabilityResolver


@pytest.fixture
def offers_provider_mock():
    provider = Mock(spec_set=OffersProvider)
    provider.get_offers_for_product.return_value = []
    return provider


@pytest.fixture
def offer_applicability_resolver(offers_provider_mock):
    return OfferApplicabilityResolver(offers_provider_mock)


@pytest.mark.parametrize('offers_for_product, expected_offers', [
    # no offers
    ([], {}),
    # single applicable offer
    (
            [
                OfferFreeProducts(
                    product_name='shampoo',
                    number_of_products_required_to_bought=3,
                    number_of_free_products=1
                )
            ],
            {
                'shampoo': [
                    OfferFreeProducts(
                        product_name='shampoo',
                        number_of_products_required_to_bought=3,
                        number_of_free_products=1
                    )
                ]
            }
    ),
    # single not applicable offer, more products required than in basket
    (
            [
                OfferFreeProducts(
                    product_name='shampoo',
                    number_of_products_required_to_bought=5,
                    number_of_free_products=2
                )
            ],
            {}
    ),
    # a few offers, some of them applicable
    (
            [
                OfferFreeProducts(
                    product_name='shampoo',
                    number_of_products_required_to_bought=5,
                    number_of_free_products=2
                ),
                OfferFreeProducts(
                    product_name='shampoo',
                    number_of_products_required_to_bought=3,
                    number_of_free_products=1
                ),
                OfferPercentageDiscount(
                    product_name='shampoo',
                    number_of_products_required_to_bought=2,
                    discount=10
                )
            ],
            {
                'shampoo': [
                    OfferFreeProducts(
                        product_name='shampoo',
                        number_of_products_required_to_bought=3,
                        number_of_free_products=1
                    ),
                    OfferPercentageDiscount(
                        product_name='shampoo',
                        number_of_products_required_to_bought=2,
                        discount=10
                    )
                ]
            }
    )
])
def test_get_offers_applicable_for_single_product(offer_applicability_resolver, offers_provider_mock,
                                                  offers_for_product, expected_offers):
    basket_items = [BasketItem(product_name='shampoo', quantity=3)]
    offers_provider_mock.get_offers_for_product.return_value = offers_for_product

    applicable_offers = offer_applicability_resolver.get_offers_applicable_for_basket_items(basket_items)

    assert applicable_offers == expected_offers


@pytest.mark.parametrize('basket_items, expected_offers', [
    # no products in basket
    ([], {}),
    # single product in basket
    (
            [BasketItem(product_name='shampoo', quantity=3)],
            {
                'shampoo': [OfferPercentageDiscount(
                    product_name='shampoo',
                    number_of_products_required_to_bought=2,
                    discount=10
                )]
            }
    ),
    # many products in basket
    (
            [
                BasketItem(product_name='shampoo', quantity=4),
                BasketItem(product_name='biscuits', quantity=3),
                BasketItem(product_name='sardines', quantity=1)
            ],
            {
                'shampoo': [OfferPercentageDiscount(
                    product_name='shampoo',
                    number_of_products_required_to_bought=2,
                    discount=10
                )],
                'biscuits': [OfferFreeProducts(
                    product_name='biscuits',
                    number_of_products_required_to_bought=3,
                    number_of_free_products=1
                )]
            }
    )
])
def test_get_offers_applicable_for_many_products(offer_applicability_resolver, offers_provider_mock, basket_items,
                                                 expected_offers):
    offers_provider_mock.get_offers_for_product.return_value = [
        OfferFreeProducts(
            product_name='shampoo',
            number_of_products_required_to_bought=5,
            number_of_free_products=2
        ),
        OfferFreeProducts(
            product_name='biscuits',
            number_of_products_required_to_bought=3,
            number_of_free_products=1
        ),
        OfferPercentageDiscount(
            product_name='shampoo',
            number_of_products_required_to_bought=2,
            discount=10
        )
    ]

    applicable_offers = offer_applicability_resolver.get_offers_applicable_for_basket_items(basket_items)

    assert applicable_offers == expected_offers


@pytest.mark.parametrize('offers, expected_combinations', [
    # one combination possible
    (
            [
                OfferFreeProducts(
                    product_name='shampoo',
                    number_of_products_required_to_bought=5,
                    number_of_free_products=2
                )
            ],
            [
                (OfferFreeProducts(
                    product_name='shampoo',
                    number_of_products_required_to_bought=5,
                    number_of_free_products=2
                ),
                )
            ]
    ),
    # multiple combinations possible
    (
            # offers
            [
                OfferFreeProducts(
                    product_name='shampoo',
                    number_of_products_required_to_bought=3,
                    number_of_free_products=1
                ),
                OfferPercentageDiscount(
                    product_name='shampoo',
                    number_of_products_required_to_bought=2,
                    discount=10
                )
            ],
            # combinations
            [
                (
                        OfferFreeProducts(
                            product_name='shampoo',
                            number_of_products_required_to_bought=3,
                            number_of_free_products=1
                        ),
                        OfferFreeProducts(
                            product_name='shampoo',
                            number_of_products_required_to_bought=3,
                            number_of_free_products=1
                        )
                ),
                (
                        OfferFreeProducts(
                            product_name='shampoo',
                            number_of_products_required_to_bought=3,
                            number_of_free_products=1
                        ),
                        OfferPercentageDiscount(
                            product_name='shampoo',
                            number_of_products_required_to_bought=2,
                            discount=10
                        )
                ),
                (
                        OfferPercentageDiscount(
                            product_name='shampoo',
                            number_of_products_required_to_bought=2,
                            discount=10
                        ),
                        OfferPercentageDiscount(
                            product_name='shampoo',
                            number_of_products_required_to_bought=2,
                            discount=10
                        ),
                        OfferPercentageDiscount(
                            product_name='shampoo',
                            number_of_products_required_to_bought=2,
                            discount=10
                        )
                )
            ]
    )
])
def test_get_item_offer_combinations(offer_applicability_resolver, offers, expected_combinations):
    basket_item = BasketItem(product_name='shampoo', quantity=6)
    combinations = offer_applicability_resolver.get_item_offer_combinations(basket_item, offers)

    assert combinations == expected_combinations
