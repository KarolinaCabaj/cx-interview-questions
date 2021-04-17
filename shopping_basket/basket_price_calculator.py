from dataclasses import dataclass

from models import Basket, Catalog, Offers


@dataclass
class PriceResult:
    sub_total: float = 0.00
    discount: float = 0.00
    total: float = 0.00


class BasketPriceCalculator:
    def __init__(self, catalog: Catalog, offers: Offers):
        self._catalog = catalog
        self._offers = offers

    def calculate_price(self, basket: Basket) -> PriceResult:
        return PriceResult(
            sub_total=sum(p.price for p in basket.get_products()),
            discount=0,
            total=sum(p.price for p in basket.get_products())
        )
