import numpy as np
import math as mt


class Statistic():
    def __init__(self):
        self.intervals_amount = 0
        self.series = []
        self.interval_series = []
        self.frequency = []
        self.relative_frequency = []
        self.grouped = []
        self.distribution_function = []
        self.average_sample = []
        self.dispersion = []
        self.deviation = []
        self.corrected_deviation = []

    def setSeries(self, series, intervalsAmount):
        self.series = sorted(series)
        self.intervals_amount = intervalsAmount
        self.interval_series = self.intervalSeries(self.series, self.intervals_amount)
        self.frequency = self.intervalFrequencyRange(self.interval_series, self.series, self.intervals_amount)
        self.relative_frequency = self.intervalRelativeFrequencyRange(self.frequency, len(self.series))
        self.grouped = self.groupedSeries(self.interval_series)
        self.distribution_function = self.empiricalDistributionFunction(self.grouped, self.relative_frequency)
        self.average_sample = self.averageSample(self.grouped, self.frequency)
        self.dispersion = self.sampleDispersion(self.grouped, self.frequency, self.average_sample)
        self.deviation = self.sampleAverageSquareDeviation(self.dispersion)
        self.corrected_deviation = self.correctedSampleAverageSquareDeviation(self.dispersion, self.frequency)

    #Получение интервального ряда
    def intervalSeries(self, list, k):
        sortList = sorted(list)

        h = (sortList[-1] - sortList[0])/k
        h = round(h, 8)

        x0 = sortList[0] - h/2
        if x0+h*k <= sortList[-1]:
            x0 = sortList[0]
        
        result = []

        for i in range(0, k):
            xi = x0 + h * i
            xi = round(xi, 8)
            yi = x0 + h * (i + 1)
            yi = round(yi, 8)
            result.append([xi, yi])
        
        return result

    #Интервальный ряд частот
    def intervalFrequencyRange(self, intervals, serias, k):
        result = []

        for i in range(0, k):
            if i != k-1:
                result.append(sum(True for item in serias if item>=intervals[i][0] and item < intervals[i][1]))
            else:
                result.append(sum(True for item in serias if item>=intervals[i][0] and item <= intervals[i][1]))

        return result

    #Интервальный ряд относительных частот
    def intervalRelativeFrequencyRange(self, frequencyRange, n):
        result = [round(item/n, 4) for item in frequencyRange]
        return result

    #Групированный ряд
    def groupedSeries(self, intervals):
        result = []

        for i in range(0, len(intervals)):
            element = (intervals[i][0] + intervals[i][1] ) / 2
            element = round(element, 8)
            result.append(element)

        return result

    #Эмпирическая функция распределения
    def empiricalDistributionFunction(self, groupedSeries, intervalRelativeFrequency):
        
        empericalFunction = []
        
        for i in range(0, len(groupedSeries)):
            empericalFunction.append(np.sum(intervalRelativeFrequency[:i], initial=0)) #сумма элементов до
            empericalFunction[i] = round(empericalFunction[i], 3)
        
        empericalFunction.append(np.sum(intervalRelativeFrequency,initial=0))
        empericalFunction[-1] = round(empericalFunction[-1], 3)
        return empericalFunction

    #X выбор
    def averageSample(self, groupSeries, frequencyRange):
        sum = np.sum(frequencyRange, initial=0)

        result = 0
        for i in range(0, len(frequencyRange)):
            result += frequencyRange[i]*groupSeries[i]
        
        result *= 1/sum
        
        return result

    #Выборочная дисперсия
    def sampleDispersion(self, groupSeries, frequencyRange, avgX):
        sum = np.sum(frequencyRange, initial=0)
        
        result = 0

        for i in range(0, len(frequencyRange)):
            result += ((groupSeries[i] - avgX)**2)*frequencyRange[i]
        
        result *= 1/sum
        return result

    #Выборочное среднее квадратическое отклонение
    def sampleAverageSquareDeviation(self, despertion):
        result = despertion ** 0.5
        return round(result,4)

    #Исправленное выборочное среднее квадратическое отклонение
    def correctedSampleAverageSquareDeviation(self, despertion, frequencyRange):
        n = np.sum(frequencyRange)

        result = (n/(n-1)*despertion) ** 0.5

        return round(result, 4)