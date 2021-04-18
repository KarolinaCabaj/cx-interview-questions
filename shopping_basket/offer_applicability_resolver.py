from typing import Dict, List

from models import BasketItem, Offer, OffersProvider


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

    def _is_offer_applicable(self, item: BasketItem, offer: Offer):
        return self._offer_regarding_product(offer, item) and self._enough_item_in_basket(item, offer)

    @staticmethod
    def _offer_regarding_product(offer, item):
        return item.product_name == offer.product_name

    @staticmethod
    def _enough_item_in_basket(item, offer):
        return item.quantity // offer.number_of_products_required_to_bought > 0
