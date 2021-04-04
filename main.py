from factor_estimator import FactorEstimator
from factor_estimator import get_common_index_codes

if __name__ == '__main__':

    estimator = FactorEstimator()
    index_codes = get_common_index_codes()
    for index_code in index_codes.values():
        print(index_code)
        factors, model, data = estimate(index_code)
        #print("Multi")
        print(factors)
        print("r2",model.rsquared)

    # momentum_factors = estimator.estimate("WQDS.L",period='max')
    # print("Quality")
    # print(momentum_factors)
    # print(momentum_factors.sum())
    # world_factors = estimator.estimate("H4ZJ.F",period='max')
    # print("World")
    # print(world_factors)
    # print(world_factors.sum())
    # value_factors = estimator.estimate("IWVG.L",period='max')
    # print("value")
    # print(value_factors)
    # print(value_factors.sum())
    #
    # small_cap = estimator.estimate("VBR",period='max')
    # print("small cap")
    # print(small_cap)
    # print(small_cap.sum())
    #
    # eimi = estimator.estimate("EIMI.L",period='max')
    # print("EIMI cap")
    # print(eimi)
    # print(eimi.sum())

