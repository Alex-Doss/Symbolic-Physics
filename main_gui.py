
import tkinter as tk
from tkinter import scrolledtext, messagebox
from symbolic_core import SymbolicEngine
import threading
import subprocess
import os

class MainApp:
    def __init__(self, root):
        self.engine = SymbolicEngine()
        self.engine.load_model('model_v04.json')
        self.root = root
        self.root.title('Symbolic Physics v0.4 Control Panel')

        self.log = scrolledtext.ScrolledText(root, width=100, height=20)
        self.log.pack()

        btn_frame = tk.Frame(root)
        btn_frame.pack()
        tk.Button(btn_frame, text='Run Readout', command=self.run_readout).pack(side=tk.LEFT)
        tk.Button(btn_frame, text='Phase Viz', command=self.run_phase).pack(side=tk.LEFT)
        tk.Button(btn_frame, text='Param Scan', command=self.run_scan).pack(side=tk.LEFT)
        tk.Button(btn_frame, text='Lyapunov', command=self.run_lyap).pack(side=tk.LEFT)
        tk.Button(btn_frame, text='Random Net', command=self.run_net).pack(side=tk.LEFT)
        tk.Button(btn_frame, text='AutoTest', command=self.start_autotest).pack(side=tk.LEFT)
        tk.Button(btn_frame, text='Stop AutoTest', command=self.stop_autotest).pack(side=tk.LEFT)

        self.autotest_thread = None
        self.autotest_running = False
        self.current_process = None

        self.update_loop()

    def log_append(self, text):
        self.engine.log.append(text)

    def update_loop(self):
        self.log.delete('1.0', tk.END)
        for line in self.engine.log[-200:]:
            self.log.insert(tk.END, line + '\n')
        self.root.after(300, self.update_loop)

    def run_subprocess(self, args, label):
        if not self.autotest_running and label == 'AutoTest':
            return False
        self.log_append(f'[GUI] Starting {label}')
        try:
            self.current_process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            while True:
                if not self.autotest_running:
                    self.current_process.kill()
                    self.log_append(f'[GUI] {label} killed')
                    return False
                line = self.current_process.stdout.readline()
                if line:
                    self.log_append(f'[GUI][{label}] ' + line.strip())
                if self.current_process.poll() is not None:
                    break
            # capture remaining stderr
            err = self.current_process.stderr.read()
            if err:
                self.log_append(f'[GUI][{label}][ERR] ' + err.strip())
            self.log_append(f'[GUI] Finished {label} with code {self.current_process.returncode}')
            return True
        except Exception as e:
            self.log_append(f'[GUI] Exception running {label}: {e}')
            return False
        finally:
            self.current_process = None

    def run_readout(self):
        threading.Thread(target=lambda: self.run_subprocess(['python', 'test_engine.py'], 'Readout')).start()

    def run_phase(self):
        threading.Thread(target=lambda: self.run_subprocess(['python', 'phase_visualizer.py'], 'PhaseViz')).start()

    def run_scan(self):
        threading.Thread(target=lambda: self.run_subprocess(['python', 'param_scan.py'], 'ParamScan')).start()

    def run_lyap(self):
        threading.Thread(target=lambda: self.run_subprocess(['python', 'lyapunov.py'], 'Lyapunov')).start()

    def run_net(self):
        threading.Thread(target=lambda: self.run_subprocess(['python', 'network_builder.py'], 'Network')).start()

    def start_autotest(self):
        if self.autotest_running:
            self.log_append('[GUI] AutoTest already running')
            return
        self.autotest_running = True
        def job():
            steps = [
                (['python', 'test_engine.py'], 'Readout'),
                (['python', 'phase_visualizer.py'], 'PhaseViz'),
                (['python', 'param_scan.py'], 'ParamScan'),
                (['python', 'lyapunov.py'], 'Lyapunov'),
                (['python', 'network_builder.py'], 'Network')
            ]
            for args, label in steps:
                if not self.autotest_running:
                    break
                success = self.run_subprocess(args, 'AutoTest-'+label)
                if not success:
                    self.log_append(f'[GUI] AutoTest aborted during {label}')
                    break
            self.autotest_running = False
            self.log_append('[GUI] AutoTest complete')
        self.autotest_thread = threading.Thread(target=job)
        self.autotest_thread.start()

    def stop_autotest(self):
        if self.autotest_running:
            self.autotest_running = False
            if self.current_process:
                try:
                    self.current_process.kill()
                except:
                    pass
            self.log_append('[GUI] Stop signal sent to AutoTest')
        else:
            self.log_append('[GUI] AutoTest not running')

if __name__ == '__main__':
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
