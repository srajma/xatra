import matplotlib.pyplot as plt
from xatra.colorseq import *

linear_seq = LinearColorSequence()
log_seq = LogColorSequence()
trivial_seq = RotatingColorSequence()
rotating_seq = RotatingColorSequence(color_sequences["tab10"])
matplotlib_seq = RotatingColorSequence().from_matplotlib_color_sequence("tab10")
random_seq = RandomColorSequence()
stack_overflow_seq = LinearColorSequence(CONTRASTING_COLORS)

linear_seq.append_many(30)
log_seq.append_many(30)
trivial_seq.append_many(30)
rotating_seq.append_many(30)
matplotlib_seq.append_many(30)
random_seq.append_many(30)
# stack_overflow_seq.append_many(30)

fig, ax = plt.subplots()
linear_seq.plot(ax)
# log_seq.plot(ax)
# trivial_seq.plot(ax)
# rotating_seq.plot(ax)
# matplotlib_seq.plot(ax)
# random_seq.plot(ax)
stack_overflow_seq.plot(ax)
plt.show()