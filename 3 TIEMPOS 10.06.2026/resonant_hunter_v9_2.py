# -*- coding: utf-8 -*-
# ======================================================================
# PERCUDANI AUTHORSHIP – Viscosímetro de Señal (H1 + L1 + V1)
# Resonant Hunter v9.2 – Mapeo Topográfico de la Viscosidad Temporal
# ======================================================================
# DOIs Permanentes de Control Causal:
# Resonant Hunter v8.4: 10.5281/zenodo.18446712
# Universal Applied Time (UAT): 10.5281/zenodo.17729221
# Unified Causal Principle (UCP): 10.5281/zenodo.18210808
# ======================================================================

import numpy as np
from numpy.fft import rfft, irfft
from scipy.ndimage import uniform_filter1d
import matplotlib.pyplot as plt

def print_header():
    print("="*75)
    print("PERCUDANI AUTHORSHIP - Resonant Hunter v9.2 Engine")
    print("Viscosímetro de Señal - Mapeo Topográfico Bidimensional")
    print("DOIs: Resonant Hunter v8.4 (10.5281/zenodo.18446712)")
    print("UAT (10.5281/zenodo.17729221) | UPC (10.5281/zenodo.18210808)")
    print("="*75)

class UAT_Engine:
    def __init__(self, epsilon=1e-4, k_early=0.967):
        self.epsilon = epsilon
        self.k_early = k_early
        
    def percudani_whiten(self, signal, fs):
        N = len(signal)
        spec = rfft(signal)
        psd = np.abs(spec)**2
        psd_smooth = uniform_filter1d(psd, size=512, mode='constant')
        D = psd_smooth + self.epsilon * self.k_early
        D_safe = np.where(D > 1e-30, D, 1e-30)
        spec_white = spec / np.sqrt(D_safe)
        out = irfft(spec_white, n=N)
        out -= np.mean(out)
        std = np.std(out)
        if std > 1e-15: 
            out /= std
        return out

class ViscosityTensor:
    def __init__(self, n_phases=8, f_base=187.37, alpha=0.046, fs=4096, lr=1e-5):
        self.n_phases = n_phases
        self.phase_angles = np.deg2rad(np.arange(0, 360, 45))  # 8 frentes de fase a 45°
        self.W = np.eye(n_phases) * 0.9 + 0.02 * np.random.randn(n_phases, n_phases) * 0.1
        self.state = np.zeros(n_phases, dtype=complex)
        self.f_base = f_base
        self.alpha = alpha  # Deriva de inflación (+0.046 Hz/día)
        self.fs = fs
        self.lr = lr
        self.k_early = 0.967  # Factor de Frenado Cuántico base
        self.phase_theoretical_acc = 0.0
        self.grad_W_momentum = np.zeros((n_phases, n_phases), dtype=complex)

    def forward_step(self, x_t, t_days):
        f_t = self.f_base + self.alpha * t_days
        self.phase_theoretical_acc += 2 * np.pi * f_t / self.fs
        
        # Interferencia rotacional constructiva
        rotation = np.exp(1j * self.phase_angles) * np.exp(-1j * self.phase_theoretical_acc)
        state_prev = self.state.copy()
        
        # Inyección al estado no lineal tensorizado
        self.state = np.tanh(self.W @ self.state + x_t * rotation)
        
        baseband_phasor = np.sum(self.state * np.exp(-1j * self.phase_angles))
        measured_phase = np.angle(baseband_phasor)
        phase_drift = np.angle(np.exp(1j * (measured_phase - self.phase_theoretical_acc)))
        
        # Gradiente e impulso de momentum causal
        grad_inst = np.outer(np.exp(1j * self.phase_angles), np.conj(state_prev)) * phase_drift
        self.grad_W_momentum = 0.9999 * self.grad_W_momentum + 0.0001 * grad_inst
        
        grad_norm = np.linalg.norm(self.grad_W_momentum) + 1e-8
        if grad_norm > 1e3:
            self.grad_W_momentum *= 1e3 / grad_norm
            grad_norm = 1e3
            
        W_new = self.W - self.lr * (self.grad_W_momentum / grad_norm).real
        
        # Mecanismo de protección contra no-finitos (Evita bucle NaN manteniendo reseteo controlado)
        if np.any(np.isnan(W_new)) or np.any(np.isnan(self.state)):
            self.W = np.eye(self.n_phases) * 0.9 + 0.02 * np.random.randn(self.n_phases, self.n_phases) * 0.1
            self.state = np.zeros(self.n_phases, dtype=complex)
            self.grad_W_momentum = np.zeros((self.n_phases, self.n_phases), dtype=complex)
            phase_drift = 0.0
        else:
            self.W = W_new
            
        # Cálculo estricto del Índice de Viscosidad Temporal (TVI)
        tvi = (phase_drift / (2 * np.pi)) * self.k_early * (1 + self.alpha * t_days)
        return tvi, phase_drift

    def process_signal(self, signal, gps_start, fs, decimation=200):
        t_days0 = (gps_start - 1369483218) / 86400.0
        N = len(signal)
        tvi_out, time_out = [], []
        
        for i, x in enumerate(signal):
            t_now = t_days0 + i / (fs * 86400.0)
            tvi, _ = self.forward_step(x, t_now)
            if i % decimation == 0:
                tvi_out.append(tvi)
                time_out.append(t_now)
        return np.array(time_out), np.array(tvi_out)

class ViscosimetroDeSenal:
    def __init__(self, fs=4096):
        self.fs = fs
        self.engine = UAT_Engine()
        
    def mapear_topografia(self, h1_data, l1_data, v1_data, gps_start, duration):
        print_header()
        print(f"Iniciando Viscosímetro de Señal en segmento GPS: {gps_start}")
        
        # 1. Blanqueamiento Percudani Autónomo
        print("Aplicando Filtros de Blanqueamiento Percudani...")
        h1_w = self.engine.percudani_whiten(h1_data, self.fs)
        l1_w = self.engine.percudani_whiten(l1_data, self.fs)
        v1_w = self.engine.percudani_whiten(v1_data, self.fs)
        
        # 2. Inicialización del Enjambre de Tensores (TensorSwarm)
        print("Procesando canales concurrentes a través del TensorSwarm...")
        t_h1 = ViscosityTensor(fs=self.fs)
        t_l1 = ViscosityTensor(fs=self.fs)
        t_v1 = ViscosityTensor(fs=self.fs)
        
        time_h1, tvi_h1 = t_h1.process_signal(h1_w, gps_start, self.fs)
        _, tvi_l1 = t_l1.process_signal(l1_w, gps_start, self.fs)
        _, tvi_v1 = t_v1.process_signal(v1_w, gps_start, self.fs)
        
        # Sincronización de longitudes por seguridad analítica
        min_len = min(len(tvi_h1), len(tvi_l1), len(tvi_v1))
        time_axis = (time_h1[:min_len] - time_h1[0]) * 86400.0  # Convertido a segundos relativos
        
        tvi_h1, tvi_l1, tvi_v1 = tvi_h1[:min_len], tvi_l1[:min_len], tvi_v1[:min_len]
        
        # 3. Extracción de los Diferenciales de Viscosidad de Red (Textura Coherente)
        diff_hl = tvi_h1 - tvi_l1
        diff_hv = tvi_h1 - tvi_v1
        diff_lv = tvi_l1 - tvi_v1
        
        # 4. Construcción de la Matriz Bidimensional para el Mapa de Calor Topográfico
        # Filas: Pares de comparación topográfica (Puntos de boya en la red)
        # Columnas: Eje de tiempo
        heatmap_matrix = np.vstack([diff_hl, diff_hv, diff_lv])
        
        self._generar_reporte_grafico(time_axis, tvi_h1, tvi_l1, tvi_v1, heatmap_matrix)
        
        print("
--- MÉTRICAS CRÍTICAS DEL VISCOSÍMETRO ---")
        print(f"TVI Local Medio H1: {np.mean(tvi_h1):.6f}")
        print(f"TVI Local Medio L1: {np.mean(tvi_l1):.6f}")
        print(f"TVI Local Medio V1: {np.mean(tvi_v1):.6f}")
        print(f"Gradiente Topográfico Medio |ΔTVI| H1-L1 (Fricción Real): {np.mean(np.abs(diff_hl)):.6f}")
        print(f"Gradiente Topográfico Medio |ΔTVI| H1-V1 (Fricción Escalar): {np.mean(np.abs(diff_hv)):.6f}")
        print(f"Gradiente Topográfico Medio |ΔTVI| L1-V1 (Fricción Angular): {np.mean(np.abs(diff_lv)):.6f}")
        print("="*75)
        
        return time_axis, heatmap_matrix

    def _generar_reporte_grafico(self, time_axis, h1, l1, v1, heatmap):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [1, 1.2]})
        
        # Panel Superior: Evolución Temporal Absoluta del TVI Local
        ax1.plot(time_axis, h1, label='Boya Hanford (H1 - Real)', color='#1f77b4', linewidth=0.7, alpha=0.8)
        ax1.plot(time_axis, l1, label='Boya Livingston (L1 - Real)', color='#ff7f0e', linewidth=0.7, alpha=0.8)
        ax1.plot(time_axis, v1, label='Boya Virgo (V1 - Sintética Calibrada)', color='#2ca02c', linewidth=0.7, alpha=0.8)
        ax1.set_ylabel('Índice TVI Absoluto', fontsize=11, fontweight='bold')
        ax1.set_title('Crónica del Flujo Temporal Causal (Boyas de Red)', fontsize=13, fontweight='bold', pad=10)
        ax1.grid(True, linestyle='--', alpha=0.5)
        ax1.legend(loc='upper right')
        
        # Panel Inferior: Mapa de Calor Topográfico Bidimensional (Tiempo vs ΔTVI)
        # Usamos pcolormesh para mapear con precisión continua la rugosidad del medio
        pairs = ['ΔTVI (H1 - L1)', 'ΔTVI (H1 - V1)', 'ΔTVI (L1 - V1)']
        y_indices = np.arange(len(pairs))
        
        X, Y = np.meshgrid(time_axis, y_indices)
        mesh = ax2.pcolormesh(X, Y, heatmap, cmap='plasma', shading='auto', edgecolors='none')
        
        cbar = fig.colorbar(mesh, ax=ax2, orientation='horizontal', pad=0.15, aspect=50)
        cbar.set_label('Magnitud del Diferencial Topográfico de Viscosidad (Rugosidad Local)', fontsize=11, fontweight='bold')
        
        ax2.set_yticks(y_indices)
        ax2.set_yticklabels(pairs, fontsize=11, fontweight='bold')
        ax2.set_xlabel('Tiempo de Tránsito del Flujo (Segundos)', fontsize=11, fontweight='bold')
        ax2.set_title('Mapa Topográfico Bidimensional de la Viscosidad Temporal', fontsize=13, fontweight='bold', pad=12)
        
        plt.tight_layout()
        plt.savefig('mapa_topografico_viscosimetro.png', dpi=300)
        print("[Sistema] Mapa topográfico exportado con éxito como 'mapa_topografico_viscosimetro.png'.")
        plt.close()

# Modo de demostración/calibración con inyección sintética dinámica
if __name__ == "__main__":
    FS = 4096
    GPS_MAESTRO = 1389424640
    DURATION_S = 100  # Reducido para simulación rápida de entorno de control
    N_SAMPLES = FS * DURATION_S
    
    # Generación de señales de prueba consistentes con la deriva UAT
    t = np.arange(N_SAMPLES) / FS
    f_uat = 187.37 + 0.046 * (GPS_MAESTRO + t - 1369483218) / 86400.0
    phase_uat = 2 * np.pi * np.cumsum(f_uat) / FS
    
    # Inyección de ruidos térmicos y offsets geométricos locales reales/sintéticos
    h1_mock = np.sin(phase_uat + 3.3) + np.random.randn(N_SAMPLES) * 1e-2
    l1_mock = np.sin(phase_uat + 0.3) + np.random.randn(N_SAMPLES) * 1e-2
    v1_mock = np.sin(phase_uat + 3.14) + np.random.randn(N_SAMPLES) * 1e-5
    
    # Inicializar y ejecutar la arquitectura de mapeo continuo
    viscosimetro = ViscosimetroDeSenal(fs=FS)
    time_axis, heatmap = viscosimetro.mapear_topografia(h1_mock, l1_mock, v1_mock, GPS_MAESTRO, DURATION_S)
