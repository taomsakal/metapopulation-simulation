import numpy
import scipy.integrate.odepack
import matplotlib.pyplot
import itertools

initialCondition = [float(input('Initial Resource Density (0~1): '))]
numberStrains = int(input('Number of Strains: '))
sporeChance = []

n = int(input('Seconds to simulate: '))

for i in range(0, numberStrains):
    initialCondition.append(float(input('Strain ' + str(i + 1) + ' Initial Vegetative Cell Density (0~1): ')))
    initialCondition.append(float(input('Strain ' + str(i + 1) + ' Initial Sporulated Cell Density (0~1): ')))
    sporeChance.append(float(input('Strain ' + str(i + 1) + ' Chance to Sporulate (0~1): ')))

time = numpy.linspace(0, n, n * 20 + 1)

growRS = 0.1
eatChance = 0.9
wiltChance = 0.005
conversionRate = 0.25
vDeathChance = 0.05
sDeathChance = 0.005


def multi_yeast_model(ic, t, g, e, w, c, vd, sd, sc):
    dicdt = [g - (w * ic[0])]
    for i in range(0, numberStrains):
        dicdt[0] -= e * ic[0] * ic[i * 2 + 1]
        rate = ((c * e * ic[0] * ic[i * 2 + 1]) * (1 - sc[i]) - (vd * ic[i * 2 + 1]))
        dicdt.append(rate)
        rate = ((c * e * ic[0] * ic[i * 2 + 1]) * sc[i] - (sd * ic[i * 2 + 2]))
        dicdt.append(rate)
    return dicdt


results = [numpy.empty_like(time)]
results[0][0] = initialCondition[0]
for i in range(1, numberStrains * 2 + 1):
    results.append(numpy.empty_like(time))
    results[i][0] = initialCondition[i]

for i in range(1, n * 20 + 1):
    tspan = [time[i - 1], time[i]]
    pop = scipy.integrate.odepack.odeint(multi_yeast_model, initialCondition, tspan,
                                         args=(growRS, eatChance, wiltChance, conversionRate, vDeathChance,
                                               sDeathChance, sporeChance))

    for x in range(0, numberStrains * 2 + 1):
        results[x][i] = pop[1][x]

    initialCondition = pop[1]

colors = itertools.cycle(["aqua", "green", "fuchsia", "lime", "maroon", "navy", "purple", "red", "silver", "teal"])

matplotlib.pyplot.plot(time, results[0], 'b-', label='Resources')

for i in range(0, numberStrains):
    col = next(colors)
    matplotlib.pyplot.plot(time, results[i * 2 + 1], color=col, linestyle='--', label='Vegetative Cells ' + str(i+1))
    matplotlib.pyplot.plot(time, results[i * 2 + 2], color=col, linestyle=':', label='Sporulated Cells ' + str(i+1))

matplotlib.pyplot.ylabel('Population Density')
matplotlib.pyplot.xlabel('Time')
matplotlib.pyplot.legend(loc='best')
matplotlib.pyplot.show()
