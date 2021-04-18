from abc import ABC
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Product:
    name: str
    price: float


@dataclass
class BasketItem:
    product: Product
    quantity: int


class Basket(ABC):
    def __init__(self, items: List[BasketItem] = None):
        self.items = items or []

    def get_items(self) -> List[BasketItem]:
        raise NotImplementedError()


@dataclass
class Offer(ABC):
    product_name: str
    number_of_products_required_to_bought: int


@dataclass
class OfferFreeProducts(Offer):
    number_of_free_products: int


@dataclass
class OfferPercentageDiscount(Offer):
    discount: float


# class should belong to this component, just require list of offers
class OffersProvider:
    def __init__(self, offers: List[Offer]):
        self._offers = self._init_offer_storage(offers)

    @staticmethod
    def _init_offer_storage(offers: List[Offer]):
        mapped_offers = dict()
        for offer in offers:
            mapped_offers.setdefault(offer.product_name, []).append(offer)
        return mapped_offers

    def get_offers(self) -> Dict[str, List[Offer]]:
        return self._offers

    def get_offer_for_product(self, product_name: str) -> List[Offer]:
        return self._offers[product_name]
