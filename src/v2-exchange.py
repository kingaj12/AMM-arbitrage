# Define forward and backward swap calculators
from typing import Union
from dataclasses import dataclass
import numpy as np

FEE_HAIRCUT:float = 0.997


def forward_swap(x: Union[float, np.ndarray], haircut: float = FEE_HAIRCUT) -> Union[float, np.ndarray]:
    if isinstance(x, float):
        assert x >= 0
    elif isinstance(x, np.ndarray):
        assert np.all(x) >= 0
    assert haircut > 0
    return haircut * x / (1 + haircut * x)


def d_forward_swap(x: Union[float, np.ndarray], haircut: float = FEE_HAIRCUT) -> Union[float, np.ndarray]:
    if isinstance(x, float):
        assert x >= 0
    elif isinstance(x, np.ndarray):
        assert np.all(x) >= 0
    assert haircut > 0
    return haircut / np.square(1 + haircut * x)


def backward_swap(y: Union[float, np.ndarray], haircut: float = FEE_HAIRCUT) -> Union[float, np.ndarray]:
    if isinstance(y, float):
        assert y >= 0.0
        assert y < 1.0
    elif isinstance(y, np.ndarray):
        assert np.all(y) >= 0
        assert np.all(y < 1.0)
    assert haircut > 0
    return y / (haircut - haircut * y)


@dataclass
class Reserve:
    token: int
    balance: float

@dataclass
class Swap:
    amount0_in: Union[float, np.ndarray]
    amount1_in: Union[float, np.ndarray]
    amount0_out: Union[float, np.ndarray]
    amount1_out: Union[float, np.ndarray]
    is_float: bool

class V2exchange:

    def __init__(self, reserves:tuple[Reserve, Reserve], haircut:float=FEE_HAIRCUT) -> None:
        """
        Initializes a class instance to manage reserves with specific ordering
        based on token values and applies a haircut value for operations.

        The constructor ensures that the reserves are correctly sorted in terms
        of their token values, assigning `reserve_0` to the reserve with the
        lower token value and `reserve_1` to the reserve with the higher token
        value. If both reserves have equal token values, an exception is raised.

        :param reserves: A tuple containing two Reserve objects. The reserves
            represent liquidity pools or assets, and they should not have equal
            token values.
        :param haircut: A float representing the discount or transaction fee
            applied to operations. Defaults to `FEE_HAIRCUT`.

        :raises ValueError: If the token values of the two reserves in the
            tuple are equal.
        """
        self.haircut = haircut

        if reserves[0].token > reserves[1].token:
            self.reserve_1 = reserves[0]
            self.reserve_0 = reserves[1]
        elif reserves[0].token < reserves[1].token:
            self.reserve_0 = reserves[0]
            self.reserve_1 = reserves[1]
        else:
            raise ValueError('Reserve tokens must not be equal')


    def token0(self):
        return self.reserve_0.token

    def token1(self):
        return self.reserve_1.token

    def swap(self, swap:Swap ):
        if swap.is_float:
            amount_out, balance_out, balance_in = self._swap_float(swap)
        else:
            amount_out, balance_out, balance_in = self._swap_ndarray(swap)


        return balance_in * backward_swap(amount_out/balance_out, haircut=self.haircut)

    def _swap_float(self, swap:Swap):
        if swap.amount0_out > 0 and swap.amount1_out == 0.0:
            return swap.amount0_out, self.reserve_0.balance, self.reserve_1.balance,
        elif swap.amount1_out > 0 and swap.amount0_out == 0.0:
            return swap.amount1_out, self.reserve_1.balance, self.reserve_0.balance
        else:
            raise ValueError('Must specify either amount0_out or amount1_out non-zero')

        return balance_in * backward_swap(amount_out / balance_out, haircut=self.haircut)

            balance0 = self.reserve_0.balance
            if not balance0 > swap.amount0_out:
                raise ValueError('Requested amount token0 is greater than reserve')
            balance1 = self.reserve_1.balance
            swap.amount1_in = balance1 * backward_swap(swap.amount0_out/balance0, haircut=self.haircut)



    def _swap_ndarray(self, swap:Swap):
        pass
