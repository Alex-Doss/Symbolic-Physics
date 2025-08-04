
import json
import random

class Symbol:
    def __init__(self, name, state):
        # float state for smooth dynamics
        self.name = name
        self.state = float(state)

    def invert(self):
        if self.state == 0.0:
            self.state = random.choice([1.0, -1.0])
        else:
            self.state = -self.state

    def add_noise(self, magnitude=0.05):
        self.state += random.uniform(-magnitude, magnitude)

class Link:
    def __init__(self, from_symbol, to_symbol, weight, ltype):
        self.from_symbol = from_symbol
        self.to_symbol = to_symbol
        self.weight = float(weight)
        self.type = ltype

class Modifier:
    def __init__(self, target, rule):
        self.target = target
        self.rule = rule

class SymbolicEngine:
    def __init__(self):
        self.symbols = {}  # name -> Symbol
        self.links = []    # list of Link
        self.modifiers = []  # list of Modifier
        self.step_count = 0
        self.log = []
        self.running = False

        # parameters
        self.bind_coeff = 0.1  # fraction of source passed in bind
        self.cycle_coeff = 0.2  # soft feedback from B to A (cycle)
        self.decay_rate = 0.95  # multiplicative decay factor
        self.noise_base = 0.01  # small background noise

    def load_model(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.log.append(f"[ERROR] loading model: {e}")
            return
        self.symbols = {}
        for s in data.get("symbols", []):
            if "name" in s and "state" in s:
                self.symbols[s["name"]] = Symbol(s["name"], s["state"])
        self.links = []
        for l in data.get("links", []):
            if all(k in l for k in ("from", "to", "weight", "type")):
                self.links.append(Link(l["from"], l["to"], l["weight"], l["type"]))
        self.modifiers = []
        for m in data.get("modifiers", []):
            if "target" in m and "rule" in m:
                self.modifiers.append(Modifier(m["target"], m["rule"]))
        self.log.append(f"[INFO] Model {filepath} loaded: symbols={list(self.symbols.keys())}, modifiers={[m.rule for m in self.modifiers]}, links={[ (l.from_symbol,l.to_symbol,l.type) for l in self.links ]}")

    def apply_modifiers(self):
        for m in self.modifiers:
            if m.target not in self.symbols:
                continue
            sym = self.symbols[m.target]
            if m.rule == "invert":
                sym.invert()
                self.log.append(f"[{self.step_count}] invert({m.target}) -> {sym.state:.3f}")
            elif m.rule == "threshold_invert":
                if sym.state > 0:
                    sym.invert()
                    self.log.append(f"[{self.step_count}] threshold_invert({m.target}) -> {sym.state:.3f}")
            elif m.rule == "random_invert":
                if random.random() < 0.3:
                    sym.invert()
                    self.log.append(f"[{self.step_count}] random_invert({m.target}) -> {sym.state:.3f}")
            elif m.rule == "noise_seed":
                if abs(sym.state) < 1e-6 and random.random() < 0.2:
                    sym.state = random.choice([1.0, -1.0])
                    self.log.append(f"[{self.step_count}] noise_seed applied to {m.target}, new state {sym.state:.3f}")
            elif m.rule == "background_noise":
                sym.add_noise(magnitude=0.05)
                self.log.append(f"[{self.step_count}] background_noise on {m.target} -> {sym.state:.3f}")
            else:
                self.log.append(f"[{self.step_count}] unknown modifier {m.rule} on {m.target}")

    def tick(self):
        self.step_count += 1
        # snapshot previous states for delayed cycle feedback
        prev_states = {name: sym.state for name, sym in self.symbols.items()}

        # apply modifiers first (including possible noise_seed etc.)
        self.apply_modifiers()

        # bind influence: propagate part of state from source to target
        for link in self.links:
            if link.type == "bind":
                if link.from_symbol in self.symbols and link.to_symbol in self.symbols:
                    src = self.symbols[link.from_symbol]
                    dst = self.symbols[link.to_symbol]
                    if isinstance(src.state, float) and isinstance(dst.state, float):
                        delta = src.state * link.weight * self.bind_coeff
                        dst_old = dst.state
                        dst.state += delta
                        if abs(delta) > 1e-8:
                            self.log.append(f"[{self.step_count}] bind transfer {delta:.4f} from {src.name} to {dst.name} ({dst_old:.4f}->{dst.state:.4f})")

        # cycle influence: soft feedback from previous target into source with delay
        for link in self.links:
            if link.type == "cycle":
                if link.from_symbol in prev_states and link.to_symbol in self.symbols:
                    prev_src = prev_states[link.from_symbol]
                    dst = self.symbols[link.to_symbol]
                    # apply soft move of dst toward prev_src
                    diff = prev_src - dst.state
                    adjustment = diff * self.cycle_coeff
                    old = dst.state
                    dst.state += adjustment
                    if abs(adjustment) > 1e-8:
                        self.log.append(f"[{self.step_count}] cycle feedback {adjustment:.4f} from prev {link.from_symbol} to {link.to_symbol} ({old:.4f}->{dst.state:.4f})")

        # global soft decay (multiplicative), but small noise to prevent perfect deadlock
        for s in self.symbols.values():
            old = s.state
            # apply decay
            s.state *= self.decay_rate
            # add tiny base noise always
            s.state += random.uniform(-self.noise_base, self.noise_base)
            if abs(s.state - old) > 1e-6:
                self.log.append(f"[{self.step_count}] decay/noise {s.name} {old:.4f}->{s.state:.4f}")

        self.log.append(f"[{self.step_count}] Tick complete.")
        if self.symbols:
            states = ", ".join([f"{s.name}={s.state:.4f}" for s in self.symbols.values()])
            self.log.append(f"[{self.step_count}] States: {states}")
        else:
            self.log.append(f"[{self.step_count}] States: (none)")

    def export_log(self, path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                for line in self.log:
                    f.write(line + "\n")
        except Exception as e:
            self.log.append(f"[{self.step_count}] [ERROR] exporting log: {e}")
