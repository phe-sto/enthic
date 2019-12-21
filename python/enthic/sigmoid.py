"""
Fit a sigmoid to the dataset
============================

Program loading data fitting it to sigmoid, writing best fit parameters and
displaying plot.
"""
from json import dumps

from numpy import array, exp, linspace
from numpy import int as npInt
from pylab import plot, xlim, ylim, legend, show
from scipy.optimize import curve_fit
from csv import reader


def sigmoid(x, x0, k):
    """
    Sigmoid to calculate with optimal parameters
       :param x: Variable (in the range of real numbers from −∞ to +∞)
       :param x0: Optimal value for the parameters so that the sum of the squared
          residuals of ``f(xdata, *popt) - ydata`` is minimized
       :param k: Optimal value for the parameters so that the sum of the squared
          residuals of ``f(xdata, *popt) - ydata`` is minimized
       :return: The sigmoid value.
    """
    return 1 / (1 + exp(-k * (x - x0)))


def linear(x, x0, k):
    """
    Sigmoid to calculate with optimal parameters
       :param x: Variable (in the range of real numbers from −∞ to +∞)
       :param x0: Optimal value for the parameters so that the sum of the squared
          residuals of ``f(xdata, *popt) - ydata`` is minimized
       :param k: Optimal value for the parameters so that the sum of the squared
          residuals of ``f(xdata, *popt) - ydata`` is minimized
       :return: The sigmoid value.
    """
    return x0 * x + k


############################################################################
# CHECKING THE INPUT AND OUTPUT AND DIRECTORY PATH
# INPUT

with open("../output/distribution-revenue.csv", mode='r') as infile:
    reader = reader(infile, delimiter=';')
    # get header from first row
    headers = next(reader)
    # get all the rows as a list
    data = list(reader)
    # transform data into numpy array
    data = array(data).astype(npInt)
xdata = list(map(lambda x: x[1], data))
ydata = list(map(lambda x: x[0], data))
# xdata = array([0.0, 1.0, 3.0, 4.3, 7.0, 8.0, 8.5, 10.0, 12.0])
# ydata = array([-0.01, 0.02, 0.04, 0.11, 0.43, 0.7, 0.89, 0.95, 0.99])

for function in (linear, sigmoid):
    popt, pcov = curve_fit(function, xdata, ydata)
    with open("sigmoid-parameter.json", mode="w") as parameter_file:
        parameter_file.write(dumps({"x0": popt[0], "k": popt[1]}))

    print(popt)
    print(pcov)
x = linspace(-1, 15, 50)
y = linear(x, *popt)

plot(xdata, ydata, 'o', label='data')
plot(x, y, label='fit')
ylim(-10000, 10000)
xlim(-10, 1000000000)
legend(loc='best')
show()
