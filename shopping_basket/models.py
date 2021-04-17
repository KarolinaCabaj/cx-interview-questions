from abc import ABC
from dataclasses import dataclass, field
from typing import List


@dataclass
class Product:
    name: str
    price: float


class Basket(ABC):
    def __init__(self, products: List[Product] = None):
        self._products = products or []

    def get_products(self) -> List[Product]:
        raise NotImplementedError()


class Catalog(ABC):
    def __init__(self, products: List[Product]):
        self._products = products

    def get_products(self) -> List[Product]:
        raise NotImplementedError()


@dataclass
class Offer(ABC):
    product: Product


@dataclass
class OfferFreeProducts(Offer):
    number_of_products: int
    number_of_free_products: int


@dataclass
class OfferPercentageDiscount(Offer):
    number_of_products: int
    discount: float


class Offers(ABC):
    def __init__(self, offers: List[Offer]):
        self._offers = offers

    def get_offers(self) -> List[Offer]:
        raise NotImplementedError()
