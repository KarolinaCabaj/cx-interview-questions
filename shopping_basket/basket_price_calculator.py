from dataclasses import dataclass
from typing import Dict, List

from models import Basket, BasketItem, Offer, OfferFreeProducts, OfferPercentageDiscount, OffersProvider


@dataclass
class PriceResult:
    sub_total: float = 0.00
    discount: float = 0.00
    total: float = 0.00


class BasketPriceCalculator:
    def __init__(self, catalog: Dict[str, float], offers_provider: OffersProvider):
        self._catalog = catalog
        self._offers_provider = offers_provider

    def calculate_price(self, basket: Basket) -> PriceResult:
        applicable_offers = self._applicable_offers(basket.get_items())

        items_price_results = []
        for item in basket.get_items():

            sub_total = item.product.price * item.quantity
            discount = 0

            offers_for_item = applicable_offers.get(item.product.name)
            if offers_for_item:
                # assume just one possible offer for product
                offer_for_item = offers_for_item[0]
                times_it_can_be_applied = item.quantity // offer_for_item.number_of_products_required_to_bought
                discount = self._get_single_offer_discount(item, offer_for_item) * times_it_can_be_applied

            item_price_result = PriceResult(
                sub_total=sub_total,
                discount=discount,
                total=sub_total - discount

            )
            items_price_results.append(item_price_result)

        return self._calculate_final_price(items_price_results)

    def _applicable_offers(self, basket_items: List[BasketItem]) -> Dict[str, List[Offer]]:
        offers = dict()
        for item in basket_items:
            for offer in self._offers_provider.get_offer_for_product(item.product.name):
                if self._is_offer_applicable(item, offer):
                    offers.setdefault(offer.product_name, []).append(offer)
        return offers

    def _is_offer_applicable(self, item: BasketItem, offer: Offer):
        return self._offer_about_product(item, offer) and self._enough_item_in_basket(item, offer)

    @staticmethod
    def _offer_about_product(item, offer):
        return item.product.name == offer.product_name

    @staticmethod
    def _enough_item_in_basket(item, offer):
        return item.quantity // offer.number_of_products_required_to_bought > 0

    @staticmethod
    def _get_single_offer_discount(item, offer) -> float:
        # get prices based on catalog, remove price from basket
        if isinstance(offer, OfferFreeProducts):
            return offer.number_of_free_products * item.product.price
        if isinstance(offer, OfferPercentageDiscount):
            return offer.discount * item.product.price / 100

    @staticmethod
    def _calculate_final_price(items_price_results):
        sub_total = sum(r.sub_total for r in items_price_results)
        discount = sum(r.discount for r in items_price_results)
        return PriceResult(
            sub_total=sub_total,
            discount=discount,
            total=sub_total - discount
        )
