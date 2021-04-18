from dataclasses import dataclass
from typing import Dict

from models import Basket, OfferFreeProducts, OfferPercentageDiscount
from offer_applicability_resolver import OfferApplicabilityResolver


@dataclass
class PriceResult:
    sub_total: float = 0.00
    discount: float = 0.00
    total: float = 0.00


class BasketPriceCalculator:
    def __init__(self, catalog: Dict[str, float], offer_applicability_resolver: OfferApplicabilityResolver):
        self._catalog = catalog
        self._offer_applicability_resolver = offer_applicability_resolver

    def calculate_price(self, basket: Basket) -> PriceResult:
        applicable_offers = self._offer_applicability_resolver.get_offers_applicable_for_basket_items(basket.get_items())

        items_price_results = []
        for item in basket.get_items():

            # assume that if product is in basket it must be in catalog
            sub_total = self._catalog[item.product_name] * item.quantity
            discount = 0

            offers_for_item = applicable_offers.get(item.product_name)
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

    def _get_single_offer_discount(self, item, offer) -> float:
        product_price = self._catalog[item.product_name]
        if isinstance(offer, OfferFreeProducts):
            return offer.number_of_free_products * product_price
        if isinstance(offer, OfferPercentageDiscount):
            return offer.discount * product_price / 100

    @staticmethod
    def _calculate_final_price(items_price_results):
        sub_total = sum(r.sub_total for r in items_price_results)
        discount = sum(r.discount for r in items_price_results)
        return PriceResult(
            sub_total=sub_total,
            discount=discount,
            total=sub_total - discount
        )
