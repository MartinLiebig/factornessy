import numpy as np


class AssetAllocation:
    def __init__(self, names):
        self.index_names = names
        self.allocations = {}

    def set_allocations(self, array):
        """
        Sets the asset allocation with an array
        :param array: asset allocations in the order of index_names
        :return: the asset allocation
        """
        for i, value in enumerate(array):
            self.allocations[self.index_names[i]] = value
        return self

    def set_allocation(self, name, value):
        """
        Sets a single value
        :type value: float
        :type name: String
        :param name: asset name
        :param value: allocation. has to be [0,1]
        :return: the allocation itself
        """
        self.allocations[name] = value
        return self

    def set_allocation_by_dict(self, allocation_dict):
        """
        Sets the allocation with a dictionary
        :type allocation_dict: dict
        :param allocation_dict: dictionay with names as key and allocation as value
        :return: the allocation itself
        """
        for key, value in allocation_dict.items():
            self.allocations[key] = value
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
