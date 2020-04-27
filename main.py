import random
import math
import matplotlib
from matplotlib import pylab
import numpy as np

class Requests(object):
    def __init__(self, lmbd, wait_average, doing_time):
        self.arrive_time = math.ceil(math.log(random.random())/(-lmbd))
        #self.arrive_time = math.ceil(np.random.exponential(1 / lmbd))
        #self.arrive_time = math.ceil(random.expovariate(lmbd))
        self.leave_time = math.ceil(random.expovariate(1/wait_average))
        #self.leave_time = math.ceil(np.random.exponential(wait_average))
        #self.leave_time = math.ceil(math.log(random.random()) / (-wait_average))
        self.doing_time = math.ceil(random.expovariate(doing_time))
        #self.doing_time = math.ceil(np.random.exponential(doing_time))
        #self.doing_time = math.ceil(math.log(random.random()) / (-doing_time))
        #self.arrive_time = int(1/lmbd)
        #self.leave_time = wait_average
        #self.doing_time = int(1/doing_time)

    time_of_living = 0
    time_of_doing = 0

    def living(self):
        self.time_of_living += 1

    def doing(self):
        self.time_of_doing += 1

    def get_arrive(self):
        return self.arrive_time

    def get_doing(self):
        return self.doing_time

    def get_leaving(self):
        return self.leave_time

    def get_living(self):
        return self.time_of_living


n, m, end_time = 5, 8, 70
lmbd, wait_average, doing_time = 0.5, 15, 0.05
trying_requests, completed_requests, denied_requests = 0, 0, 0
time_in_system, time_in_queue, time_in_channel = 0, 0, 0
requests_in_queue, request_in_channels, requests_in_system = 0, 0, 0
queues = 0
iterations = 10000
probabilities = [[0 for i in range(n + m + 2)] for j in range(end_time)]
for i in range(iterations):
    queue = []
    channels = [None for j in range(n)]
    new_request = Requests(lmbd, wait_average, doing_time)
    time_to_next_left = int(new_request.get_arrive())
    for current_time in range(end_time):
        # из очереди в канал
        if len(queue) != 0:
            if None in channels:
                time_in_queue += queue[0].time_of_living
                channels[channels.index(None)] = queue[0]
                queue.pop(0)
        # новый заказ
        if time_to_next_left == 0:
            new_request = Requests(lmbd, wait_average, doing_time)
            trying_requests += 1
            # если есть свободный канал, то на него
            if None in channels:
                channels[channels.index(None)] = new_request
            # иначе в очередь
            elif len(queue) < m:
                queue.append(new_request)
            # или вообще отказ
            else:
                denied_requests += 1
                probabilities[current_time][-1] += 1
            time_to_next_left = int(new_request.get_arrive())
        time_to_next_left -= 1
        # обновляем заявки в каналах
        doing = 0
        for item in channels:
            if item is not None:
                item.living()
                item.doing()
                doing += 1
                if item.time_of_doing == item.get_doing():
                    channels[channels.index(item)] = None
                    completed_requests += 1
                    time_in_system += item.time_of_living
                    time_in_channel += item.time_of_doing
        # записываем, была ли очередь и сколько где заявок
        if len(queue) > 0:
            queues += 1
        requests_in_queue += len(queue)
        request_in_channels += doing
        requests_in_system += len(queue) + doing
        probabilities[current_time][len(queue) + doing] += 1
        # обновляем заявки в очереди
        for item in queue:
            item.living()
            if item.get_living() == item.get_leaving():
                queue.remove(item)
                time_in_system += item.time_of_living
                time_in_queue += item.time_of_living

print('интенсивность', trying_requests/(iterations*end_time))
print('вероятность отсутсвия очереди', (end_time*iterations - queues)/(end_time*iterations))
print('вероятность образования очереди', queues/(end_time*iterations))
print('вероятность отказа', denied_requests/trying_requests)
print('относительная пропускная способность', (trying_requests - denied_requests)/trying_requests)
print('абсолютная пропускная способность', (trying_requests - denied_requests)/(end_time*iterations))
print('среднее число заявок в очереди', requests_in_queue/(end_time*iterations))
print('среднее количество заявок на обслуживании', request_in_channels/(end_time*iterations))
print('среднее число заявок в системе', requests_in_system/(end_time*iterations))
print('среднее время ожидания в очереди', time_in_queue/(trying_requests - denied_requests))
print('среднее время обслуживания', time_in_channel/completed_requests)
print('среднее время пребывания заявки в СМО', time_in_system/completed_requests)
print('вероятность ухода из очереди', (trying_requests - denied_requests - completed_requests)/trying_requests)
for i in range(n + 1):
    print('предельная вероятность ', i, ' ', probabilities[-1][i]/iterations)
for i in range(m + 1):
    print('предельная вероятность ', n, '-', i, ' ', probabilities[-1][i + n] / iterations)
print('предельная вероятность отказа', probabilities[-1][-1]/iterations)

x = [i for i in range(len(probabilities))]
for j in range(len(probabilities[0])):
    plot = [0 for i in range(len(probabilities))]
    for i in range(len(probabilities)):
        plot[i] = probabilities[i][j]/iterations
    pylab.plot(x, plot)
pylab.show()


