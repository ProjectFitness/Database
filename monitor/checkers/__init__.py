from .pokemoncenter import PokemonCenterChecker
from .target import TargetChecker
from .walmart import WalmartChecker

REGISTRY = {
    c.retailer: c
    for c in (TargetChecker, WalmartChecker, PokemonCenterChecker)
}
