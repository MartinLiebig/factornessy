import numpy as np


class AssetAllocation:
    def __init__(self, names):
        self.index_names = names
        self.allocations = {}

    def set_allocations(self, array):
        for i, value in enumerate(array):
            self.allocations[self.index_names[i]] = value
        return self

    def set_allocation(self, name, value):
        self.allocations[name] = value
        return self

    def distribute_evenly(self):
        for name in self.index_names:
            self.allocations[name] = 1/len(self.index_names)


    def to_array(self) -> np.ndarray:
        x = np.zeros((len(self.index_names), 1))
        for i, name in enumerate(self.index_names):
            if name in self.allocations:
                x[i] = self.allocations[name]
            else:
                x[i] = 0
        return x

    def __str__(self):
        return str(self.allocations)


if __name__ == '__main__':
    names = ["a", "b", "c"]
    a = np.ones(3) / 2


    alloc = AssetAllocation(names)
    #alloc.set_allocations(a)

    alloc.set_allocation("a", 0.5)
    print(alloc.allocations)

    print(alloc)
    print(alloc.to_array())
