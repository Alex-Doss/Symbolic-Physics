
import json
import random
import copy

class Symbol:
    def __init__(self, name, state):
        self.name = name
        self.state = float(state)

    def invert(self):
        if self.state == 0.0:
            self.state = random.choice([-1.0, 1.0])
        else:
            self.state = -self.state

class Link:
    def __init__(self, from_symbol, to_symbol, weight, ltype):
        self.from_symbol = from_symbol
        self.to_symbol = to_symbol
        self.weight = weight
        self.type = ltype

class Modifier:
    def __init__(self, target, rule):
        self.target = target
        self.rule = rule

class SymbolicEngine:
    def __init__(self, config=None):
        # config holds coefficients: decay_rate, bind_coeff, cycle_coeff, random_invert_p, noise_seed_p, background_noise_amp
        self.symbols = {}
        self.links = []
        self.modifiers = []
        self.step_count = 0
        self.log = []
        self.config = config or {
            'decay_rate':0.9,
            'bind_coeff':0.1,
            'cycle_coeff':0.5,
            'random_invert_p':0.3,
            'noise_seed_p':0.2,
            'background_noise_amp':0.05
        }
        self.prev_B = {}

    def load_model(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.log.append(f'[ERROR] loading model: {e}')
            return
        self.symbols = {s['name']: Symbol(s['name'], s['state']) for s in data.get('symbols', []) if 'name' in s}
        self.links = []
        for l in data.get('links', []):
            if all(k in l for k in ('from','to','weight','type')):
                self.links.append(Link(l['from'], l['to'], l['weight'], l['type']))
        self.modifiers = []
        for m in data.get('modifiers', []):
            if 'target' in m and 'rule' in m:
                self.modifiers.append(Modifier(m['target'], m['rule']))
        # store previous B for cycle feedback
        self.prev_B = {name: sym.state for name, sym in self.symbols.items()}
        self.log.append(f'[INFO] Model {filepath} loaded: symbols={list(self.symbols.keys())}, modifiers={[m.rule for m in self.modifiers]}, links={[ (l.from_symbol,l.to_symbol,l.type) for l in self.links ]}')

    def apply_modifiers(self):
        for m in self.modifiers:
            if m.target in self.symbols:
                sym = self.symbols[m.target]
                if m.rule == 'invert':
                    sym.invert()
                    self.log.append(f'[{self.step_count}] invert({m.target})')
                elif m.rule == 'random_invert':
                    if random.random() < self.config['random_invert_p']:
                        sym.invert()
                        self.log.append(f'[{self.step_count}] random_invert({m.target})')
                elif m.rule == 'noise_seed':
                    if sym.state == 0.0 and random.random() < self.config['noise_seed_p']:
                        sym.state = random.choice([-1.0,1.0])
                        self.log.append(f'[{self.step_count}] noise_seed applied to {m.target}, new state {sym.state}')
                elif m.rule == 'background_noise':
                    amp = self.config['background_noise_amp']
                    delta = random.uniform(-amp, amp)
                    old = sym.state
                    sym.state += delta
                    self.log.append(f'[{self.step_count}] background_noise on {m.target} -> {delta:.4f}')
                else:
                    self.log.append(f'[{self.step_count}] unknown modifier {m.rule} on {m.target}')

    def tick(self):
        self.step_count += 1
        self.apply_modifiers()

        # bind transfer
        for link in self.links:
            if link.from_symbol in self.symbols and link.to_symbol in self.symbols:
                src = self.symbols[link.from_symbol]
                dst = self.symbols[link.to_symbol]
                if link.type == 'bind':
                    delta = src.state * link.weight * self.config['bind_coeff']
                    dst.state += delta
                    if abs(delta) > 1e-8:
                        self.log.append(f'[{self.step_count}] bind transfer {delta:.4f} from {src.name} to {dst.name}')
                elif link.type == 'cycle':
                    prev = self.prev_B.get(link.from_symbol, 0.0)
                    feedback = prev * self.config['cycle_coeff']
                    # apply to target
                    tgt = self.symbols[link.to_symbol]
                    old = tgt.state
                    tgt.state += feedback
                    if abs(feedback) > 1e-8:
                        self.log.append(f'[{self.step_count}] cycle feedback {feedback:.4f} from prev {link.from_symbol} to {link.to_symbol} ({old:.4f}->{tgt.state:.4f})')

        # decay towards zero gently
        for s in self.symbols.values():
            if isinstance(s.state, float):
                old = s.state
                s.state *= self.config['decay_rate']
                if abs(old - s.state) > 1e-6:
                    self.log.append(f'[{self.step_count}] decay/noise {s.name} {old:.4f}->{s.state:.4f}')

        # update previous B values for next tick
        self.prev_B = {name: sym.state for name, sym in self.symbols.items()}

        self.log.append(f'[{self.step_count}] Tick complete.')
        if self.symbols:
            states = ', '.join([f'{s.name}={s.state:.4f}' for s in self.symbols.values()])
            self.log.append(f'[{self.step_count}] States: {states}')
        else:
            self.log.append(f'[{self.step_count}] States: (none)')

    def export_log(self, path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                for line in self.log:
                    f.write(line + '\n')
        except Exception as e:
            self.log.append(f'[ERROR] exporting log: {e}')
