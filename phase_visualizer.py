
import matplotlib.pyplot as plt
from symbolic_core import SymbolicEngine
import json

def run_and_plot(model_file, steps=200):
    engine = SymbolicEngine()
    engine.load_model(model_file)
    A_vals = []
    B_vals = []
    for _ in range(steps):
        engine.tick()
        A_vals.append(engine.symbols['A'].state)
        B_vals.append(engine.symbols['B'].state)
    plt.figure()
    plt.plot(A_vals, label='A')
    plt.plot(B_vals, label='B')
    plt.legend()
    plt.title('Time series A and B')
    plt.savefig('time_series.png')
    plt.figure()
    plt.scatter(A_vals, B_vals, s=5)
    plt.title('Phase space A vs B')
    plt.xlabel('A')
    plt.ylabel('B')
    plt.savefig('phase_space.png')
    print('Saved phase_space.png and time_series.png')

if __name__ == '__main__':
    run_and_plot('model_v04.json')
