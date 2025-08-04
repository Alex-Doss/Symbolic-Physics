
import itertools
import json
import csv
from symbolic_core import SymbolicEngine
import os

def run_scan(model_file, output_csv='param_scan.csv'):
    # parameter grid
    decay_rates = [0.8, 0.9, 0.95]
    bind_coeffs = [0.05, 0.1, 0.2]
    cycle_coeffs = [0.2, 0.5, 0.8]
    results = []
    for dr, bc, cc in itertools.product(decay_rates, bind_coeffs, cycle_coeffs):
        config = {'decay_rate':dr, 'bind_coeff':bc, 'cycle_coeff':cc,
                  'random_invert_p':0.3,'noise_seed_p':0.2,'background_noise_amp':0.05}
        engine = SymbolicEngine(config=config)
        engine.load_model(model_file)
        # run short simulation
        for _ in range(100):
            engine.tick()
        # compute metrics: variance of A and B
        A_vals = [float(line.split('States: ')[1].split(',')[0].split('=')[1]) 
                  for line in engine.log if 'States:' in line]
        B_vals = [float(line.split('States: ')[1].split(',')[1].split('=')[1]) 
                  for line in engine.log if 'States:' in line]
        varA = sum((x - sum(A_vals)/len(A_vals))**2 for x in A_vals)/len(A_vals) if A_vals else 0
        varB = sum((x - sum(B_vals)/len(B_vals))**2 for x in B_vals)/len(B_vals) if B_vals else 0
        results.append({'decay_rate':dr,'bind_coeff':bc,'cycle_coeff':cc,'varA':varA,'varB':varB})
    # write CSV
    with open(output_csv,'w',newline='') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=['decay_rate','bind_coeff','cycle_coeff','varA','varB'])
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    print(f'Scan complete, wrote {output_csv}')

if __name__ == '__main__':
    run_scan('model_v04.json')
