
Symbolic Physics v0.4 Expanded

Included components:
- symbolic_core.py : parametrized engine (decay_rate, bind_coeff, cycle_coeff, random_invert_p, noise_seed_p, background_noise_amp)
- test_engine.py : reservoir computing readout with Ridge regression on synthetic signal
- phase_visualizer.py : builds time series and phase space plots (saves PNGs)
- lyapunov.py : estimates average Lyapunov exponent via perturbed twin trajectories
- param_scan.py : grid search over decay/bind/cycle parameters, outputs variances to CSV
- network_builder.py : generates random multi-symbol network and simulates summary
- model_v04.json : default model with stochastic excitation and feedback
- setup_and_run.bat : will be added to orchestrate running all

Instructions:
Run setup_and_run.bat to execute full pipeline and GUI.
