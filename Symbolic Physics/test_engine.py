
import numpy as np
from symbolic_core import SymbolicEngine
from sklearn.linear_model import Ridge
import matplotlib.pyplot as plt
import json

# synthetic target: sum of two sinusoids
def generate_signal(length):
    t = np.arange(length)
    return np.sin(0.1 * t) + 0.5 * np.sin(0.05 * t + 1.0)

def main():
    # load model
    engine = SymbolicEngine()
    engine.load_model('model_v04.json')
    T = 200
    signal = generate_signal(T)
    reservoir_states = []
    targets = []

    for i in range(T-1):
        # feed signal as background_noise modifier: add to A manually
        # emulate external input by adding to symbol A
        engine.symbols['A'].state += signal[i] * 0.01  # small injection
        engine.tick()
        reservoir_states.append([engine.symbols['A'].state, engine.symbols['B'].state])
        targets.append(signal[i+1])  # predict next value

    X = np.array(reservoir_states)
    y = np.array(targets)

    # train linear readout
    model = Ridge(alpha=1.0)
    model.fit(X, y)
    pred = model.predict(X)

    # compute error
    mse = np.mean((pred - y)**2)
    print(f'Readout MSE: {mse:.6f}')

    # save model coefficients
    np.savetxt('readout_coef.txt', model.coef_)

    # plot
    plt.figure()
    plt.plot(y, label='target')
    plt.plot(pred, label='pred')
    plt.legend()
    plt.title('Reservoir readout prediction')
    plt.savefig('readout_plot.png')
    print('Saved readout_plot.png')

if __name__ == '__main__':
    main()
