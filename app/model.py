from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional


class OutOfStock(Exception): 
    pass


@dataclass(frozen=True)
class OrderLine: 
    order_reference: str
    sku: str
    quantity: int


class Batch: 
    def __init__(self, reference: str, sku: str, quantity: str, eta: Optional[date]): 
        self.reference = reference
        self.sku = sku 
        self.eta = eta
        self._purchased_quantity = quantity
        self._allocations = set() 

    def can_allocate(self, line: OrderLine) -> bool: 
        return self.sku == line.sku and self.available_quantity >= line.quantity

    def allocate(self, line: OrderLine): 
        assert isinstance(line, OrderLine)
        if self.can_allocate(line): 
            self._allocations.add(line)

    def deallocate(self, line: OrderLine): 
        if line in self._allocations: 
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int: 
        return sum(line.quantity for line in self._allocations)

    @property
    def available_quantity(self) -> int: 
        return self._purchased_quantity - self.allocated_quantity 

    def __eq__(self, other): 
        if not isinstance(other, Batch): 
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other): 
        if self.eta is None: 
            return False 
        if other.eta is None: 
            return True
        return self.eta > other.eta


def allocate(line: OrderLine, batches: list[Batch]) -> str: 
    """
    Allocates line to best batch and returns batch reference. 
    """
    best_batch = None
    for batch in batches: 
        if not batch.can_allocate(line): 
            continue
        if batch.eta == None:
            batch.allocate(line)
            return batch.reference
        if best_batch == None: 
            best_batch = batch
        elif batch.eta < best_batch.eta: 
            best_batch = batch

    if best_batch == None: 
        raise OutOfStock(f"Out fo stock for SKU {line.sku}")
        
    best_batch.allocate(line)
    return best_batch.reference

