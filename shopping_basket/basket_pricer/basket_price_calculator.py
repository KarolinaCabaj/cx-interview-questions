from dataclasses import dataclass
from typing import Dict, List, Tuple

from basket_pricer.models import Basket, Offer, OfferFreeProducts, OfferPercentageDiscount, OffersProvider
from basket_pricer.offer_applicability_resolver import OfferApplicabilityResolver


@dataclass
class PriceResult:
    sub_total: float = 0.00
    discount: float = 0.00
    total: float = 0.00


class BasketPriceCalculator:
    def __init__(self, catalog: Dict[str, float], offers: List[Offer]):
        self._catalog = catalog
        self._offer_resolver = OfferApplicabilityResolver.create(offers)

    def calculate_price(self, basket: Basket) -> PriceResult:
        applicable_offers = self._offer_resolver.get_offers_applicable_for_basket_items(basket.get_items())

        items_price_results = []
        for item in basket.get_items():
            item_price_result = self._calculate_price_for_item(applicable_offers, item)
            items_price_results.append(item_price_result)

        return self._calculate_final_price(items_price_results)

    def _calculate_price_for_item(self, applicable_offers, item):
        offers_for_item = applicable_offers.get(item.product_name)
        discount = self._get_max_discount_for_item(offers_for_item, item) if offers_for_item else 0
        # assume that if product is in basket it must be in catalog
        sub_total = self._catalog[item.product_name] * item.quantity
        item_price_result = PriceResult(
            sub_total=sub_total,
            discount=discount,
            total=sub_total - discount
        )
        return item_price_result

    def _get_max_discount_for_item(self, offers_for_item: List[Offer], item) -> float:
        offer_combinations = self._offer_resolver.get_item_offer_combinations(item, offers_for_item)
        discounts_for_combinations = self._calculate_discounts_for_offers_combination(offer_combinations)
        max_discount_for_item = max(discounts_for_combinations) if discounts_for_combinations else 0
        return max_discount_for_item

    @staticmethod
    def _calculate_final_price(items_price_results):
        sub_total = sum(r.sub_total for r in items_price_results)
        discount = sum(r.discount for r in items_price_results)
        return PriceResult(
            sub_total=round(sub_total, 2),
            discount=round(discount, 2),
            total=round(sub_total - discount, 2)
        )

    def _calculate_discounts_for_offers_combination(self, offer_combinations: List[Tuple[Offer]]) -> List[float]:
        return [self._calculate_discount_for_offer_combination(combination) for combination in offer_combinations]

    def _calculate_discount_for_offer_combination(self, offer_combination: Tuple[Offer]) -> float:
        return sum(self._get_single_offer_discount(offer.product_name, offer) for offer in offer_combination)

    def _get_single_offer_discount(self, product_name, offer) -> float:
        product_price = self._catalog[product_name]
        if isinstance(offer, OfferFreeProducts):
            return offer.number_of_free_products * product_price
        if isinstance(offer, OfferPercentageDiscount):
            return offer.discount * product_price / 100
