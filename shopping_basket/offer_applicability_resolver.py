import itertools
from typing import Dict, List, Tuple

from models import BasketItem, Offer, OffersProvider


# rename?
class OfferApplicabilityResolver:
    def __init__(self, offers_provider: OffersProvider):
        self._offers_provider = offers_provider

    def get_offers_applicable_for_basket_items(self, basket_items: List[BasketItem]) -> Dict[str, List[Offer]]:
        offers = dict()
        for item in basket_items:
            for offer in self._offers_provider.get_offers_for_product(item.product_name):
                if self._is_offer_applicable(item, offer):
                    offers.setdefault(offer.product_name, []).append(offer)
        return offers

    @staticmethod
    def get_item_offer_combinations(item: BasketItem, offers_for_item: List[Offer]) -> List[Tuple[Offer]]:
        # get possible combinations of offers, there can be from 1 to number of product offers applied at a time
        # each combination gather offers that cover all instances of given product or less
        # combination must be made of offers such that no more can be added
        offers_min_cover = min(offer.number_of_products_required_to_bought for offer in offers_for_item)
        item_offer_combinations = []

        for number_of_offers_to_apply in range(1, item.quantity + 1):
            for combination in itertools.combinations_with_replacement(offers_for_item, number_of_offers_to_apply):
                covered_quantity = sum(offer.number_of_products_required_to_bought for offer in combination)
                if covered_quantity <= item.quantity and item.quantity - covered_quantity < offers_min_cover:
                    item_offer_combinations.append(combination)

        return item_offer_combinations

    def _is_offer_applicable(self, item: BasketItem, offer: Offer):
        return self._offer_regarding_product(offer, item) and self._enough_item_in_basket(item, offer)

    @staticmethod
    def _offer_regarding_product(offer, item):
        return item.product_name == offer.product_name

    @staticmethod
    def _enough_item_in_basket(item, offer):
        return item.quantity // offer.number_of_products_required_to_bought > 0
