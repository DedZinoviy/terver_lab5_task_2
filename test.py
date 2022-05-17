from statisticalDataBigArray import *

stat = Statistic()

ar = [153,154,155,155,156,157,158,159,160,163,164,
      165,166,167,167,169,170,171,171,172,173,173,
      175,175,178,179,179,182,183,186]

stat.setSeries(ar, 6)

range = stat.interval_series
print(range, '\n')

h_lenght = stat.interval_series[0][1] - stat.interval_series[0][0]
print(h_lenght, ' ')
print(stat.frequency)
frequencies = [i / h_lenght for i in stat.frequency]
print(frequencies, '\n')

relativeFrequencies = stat.relative_frequency
print(relativeFrequencies, '\n')

group = stat.grouped
print(group, '\n')

F = stat.distribution_function
print(F, '\n')

X = stat.average_sample
print(X, '\n')

D = stat.dispersion
print(D, '\n')

sigma = stat.deviation
print(sigma, '\n')

S = stat.corrected_deviation
print(S, '\n')