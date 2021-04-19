## Documentation

Library `basket-price-calculator` can be used to calculate the price based on products' catalog, offers list and basket content.
Locally you can use it by installing it in your project:
`pip install -e <path_to_lib_repo>/shopping_basket`

Access to the feature of the library is handled by `BasketPriceCalculator` class. 
Offers passed to `BasketPriceCalculator` must be instances of either `OfferFreeProducts` or `OfferPercentageDiscount`.
The catalog should be an instance of a dictionary that maps products' names to the prices.
The argument of function `calculate_price` is a basket instance of a class deriving from `Basket`.

#### Example usage:
```
from typing import List

from basket_pricer.basket_price_calculator import BasketPriceCalculator
from basket_pricer.models import Basket, BasketItem, OfferFreeProducts, OfferPercentageDiscount

baked_bean_offer = OfferFreeProducts(
    product_name='baked_beans',
    number_of_products_required_to_bought=3,
    number_of_free_products=1
)
sardines_offer = OfferPercentageDiscount(
    product_name='sardines',
    number_of_products_required_to_bought=1,
    discount=25
)

catalog = {
    'shampoo': 2.50,
    'shampoo_large': 3.50,
    'baked_beans': 0.99,
    'sardines': 1.89,
    'biscuits': 1.20
}
price_calculator = BasketPriceCalculator(
    catalog=catalog,
    offers=[baked_bean_offer, sardines_offer]
)


class MyBasket(Basket):
    def get_items(self) -> List[BasketItem]:
        return self._items


basket = MyBasket([BasketItem(product_name='baked_beans', quantity=4),
                   BasketItem(product_name='biscuits', quantity=1)])
price_result = price_calculator.calculate_price(basket)
```