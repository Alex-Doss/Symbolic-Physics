
import numpy as np
from symbolic_core import SymbolicEngine
import math

def estimate_lyapunov(model_file, steps=100, eps=1e-5):
    engine1 = SymbolicEngine()
    engine1.load_model(model_file)
    engine2 = SymbolicEngine()
    engine2.load_model(model_file)
    # initial small perturbation on A
    engine2.symbols['A'].state += eps
    distances = []
    for i in range(steps):
        engine1.tick()
        engine2.tick()
        a1 = engine1.symbols['A'].state
        b1 = engine1.symbols['B'].state
        a2 = engine2.symbols['A'].state
        b2 = engine2.symbols['B'].state
        d = math.sqrt((a1 - a2)**2 + (b1 - b2)**2)
        distances.append(d)
        # renormalize to keep perturbation small
        if d == 0:
            continue
        scale = eps / d
        engine2.symbols['A'].state = a1 + (a2 - a1) * scale
        engine2.symbols['B'].state = b1 + (b2 - b1) * scale
    # estimate exponent from log of growth
    logs = [math.log(max(di, 1e-16)/eps) for di in distances if di>0]
    if not logs:
        print('No divergence')
        return
    lyap = sum(logs)/len(logs)
    print(f'Approx Lyapunov exponent (average) per {steps} steps: {lyap/steps}')

if __name__ == '__main__':
    estimate_lyapunov('model_v04.json')
