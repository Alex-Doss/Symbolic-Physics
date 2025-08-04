
import json
from symbolic_core import SymbolicEngine
import random

def make_random_network(n=5):
    symbols = [{'name': f'S{i}', 'state': random.uniform(-1,1)} for i in range(n)]
    links = []
    for i in range(n):
        for j in range(n):
            if i != j:
                if random.random() < 0.3:
                    typ = random.choice(['bind','cycle'])
                    weight = random.uniform(0.5,1.5)
                    links.append({'from':f'S{i}','to':f'S{j}','weight':weight,'type':typ})
    modifiers = []
    # give first two random_invert and noise
    modifiers.append({'target':'S0','rule':'random_invert'})
    modifiers.append({'target':'S0','rule':'noise_seed'})
    modifiers.append({'target':'S1','rule':'background_noise'})
    model = {'symbols':symbols,'links':links,'modifiers':modifiers}
    with open('random_net.json','w',encoding='utf-8') as f:
        json.dump(model,f,indent=2)
    print('Created random_net.json with',n,'symbols')

def simulate_and_summary(model_file, steps=100):
    engine = SymbolicEngine()
    engine.load_model(model_file)
    for _ in range(steps):
        engine.tick()
    # summary: average absolute states
    avg = sum(abs(s.state) for s in engine.symbols.values())/len(engine.symbols)
    print('Average magnitude of state:',avg)
    # list connections
    print('Links:',[(l.from_symbol,l.to_symbol,l.type) for l in engine.links])

if __name__ == '__main__':
    make_random_network(7)
    simulate_and_summary('random_net.json')
