import pytest

from basket_pricer.models import OfferFreeProducts, OfferPercentageDiscount, OffersProvider


@pytest.fixture
def free_biscuits_offer():
    return OfferFreeProducts(product_name='biscuits', number_of_products_required_to_bought=3,
                             number_of_free_products=1)


@pytest.fixture
def sardines_discount_offer():
    return OfferPercentageDiscount(product_name='sardines', number_of_products_required_to_bought=3,
                                   discount=20)


@pytest.fixture
def offer_provider(free_biscuits_offer, sardines_discount_offer) -> OffersProvider:
    return OffersProvider(offers=[free_biscuits_offer, sardines_discount_offer])


def test_get_offers(offer_provider, free_biscuits_offer, sardines_discount_offer):
    result = offer_provider.get_offers()
    assert result == {free_biscuits_offer.product_name: [free_biscuits_offer],
                      sardines_discount_offer.product_name: [sardines_discount_offer]}


def test_get_offers_for_product(offer_provider, free_biscuits_offer):
    result = offer_provider.get_offers_for_product(free_biscuits_offer.product_name)
    assert result == [free_biscuits_offer]


def test_get_offers_for_product_when_there_is_no_offer(offer_provider):
    result = offer_provider.get_offers_for_product('product_without_offer')
    assert result == []
