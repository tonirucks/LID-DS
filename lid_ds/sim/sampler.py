from typing import List

import numpy as np
import random
import matplotlib.pyplot as plt
from lid_ds.sim.samples.sample_factory import SampleFactory

fig = plt.figure(figsize=(5, 15))

# 1 - Zufällige Auswahl von Einträgen und Skalierung auf Aufzeichnungslänge
# 2 - Auswahl eines Ausschnitts der Aufzeichnungslänge pro Nutzer -> Problem beginnt bei 0
# 3 - Auswahl eines Ausschnitts der Aufzeichnungslänge und Extraktion der einzelnen Nutzer über IP
# 4 - Auswahl einer IP und Skalierung aller Aktionen dieser IP auf Aufzeichnungslänge
# 5 - Auswahl einer IP und Verwendung deren Aktionen innerhalb einer Aufzeichnungslänge -> Problem beginnt bei 0
# TODO: random zeitraum statt zeit über ip etc


# 3
def extract_from_sample(secs):
    sample = SampleFactory.get_sample("nasa")
    start = (sample['time'].max() - sample['time'].min()) * np.random.ranf() + sample['time'].min()
    end = start + secs
    print(start, end)
    sample = sample[sample['time'].between(start, end)]
    samples = []
    for ip in sample['ip']:
        sample_ip = sample[sample['ip'] == ip]['time']
        sample_ip -= start
        samples.append(sample_ip.to_numpy(np.float64))
    return np.array(samples)


# 4
def generate_sample_ip_all(secs):
    sample = SampleFactory.get_sample("nasa")
    ip = np.random.choice(sample['ip'])
    sample = sample[sample['ip'] == ip]["time"]
    return np.round((sample / np.amax(sample) * secs), 4)


# 5
def generate_sample_real_data_ip(secs):
    sample = SampleFactory.get_sample("nasa")
    choice = sample.sample(1).iloc[0]
    sample = sample[sample['time'].between(choice['time'], choice['time'] + secs)]
    sample = sample[sample['ip'] == choice["ip"]]
    sample = sample["time"] - choice["time"]
    return sample


# 2
def generate_sample_real_data(secs):
    sample = SampleFactory.get_sample("nasa")["time"]
    first_time = random.randrange(sample.min(), sample.max())
    sample = sample[sample.isin(range(first_time, first_time + secs))]
    sample -= first_time
    return sample.to_numpy(np.float64)


# 1
def generate_sample(secs, choice_factor=0.5, random_range=0.1):
    # random difference between behaviors +-range
    variation = round(random.uniform(1 - random_range, 1 + random_range), 2)
    sample = np.random.choice(SampleFactory.get_sample("raith")['time'], int(secs * choice_factor * variation))
    # scale sample to secs
    return np.round((sample / np.amax(sample) * secs), 0)


def convert_sample_to_wait_times(sample: np.ndarray) -> List[float]:
    sample.sort()
    wait_times = []
    last = 0
    for time in sample:
        wait_times.append(time - last)
        last = time
    return wait_times


def visualize_sample(sample: np.ndarray, bins=100):
    n = len(fig.axes)
    for i in range(n):
        fig.axes[i].change_geometry(n + 1, 1, i + 1)

    ax = fig.add_subplot(n + 1, 1, n + 1)
    ax.hist(sample, bins=bins)


def visualize(name):
    fig.savefig("behavior_%s.png" % name)


if __name__ == '__main__':
    x = extract_from_sample(300)
    print(x)
