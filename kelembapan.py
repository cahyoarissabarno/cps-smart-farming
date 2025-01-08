# Library yang digunakan
import numpy as np
import matplotlib.pyplot as plt

# =======================================
# 1. PARAMETER UMUM
# =======================================
simulation_time = 300  # Total waktu simulasi (hari)
time_step = 1          # Interval waktu simulasi (hari)
t = np.arange(0, simulation_time, time_step)  # Array waktu simulasi (hari)
temperature = 28       # Suhu optimal untuk cabai (°C) di antara

# Parameter umum kelembapan tanah - H(t)
# dHt / dt = (W(t) / Vpot) - E(t)
phi = 3.14             # Luas penampang pot (m²) sesuai bentuk lingkaran
r = 0.1                # Radius pot (m)
H_pot = 1.0            # Tinggi pot (m)
V_pot = phi * r * H_pot  # Volume pot (m³)
W_pump = 3             # Debit air (L/hari)
threshold = 0.65       # Ambang batas kelembapan tanah untuk cabai (65%)

# Parameter nutrisi - N(t)
# dN(t) / dt = (Cnutrisi(t) * W(t)) / Vpot - U(t)
C_nutrisi = 0.05       # Konsentrasi nutrisi (mol/L) disesuaikan untuk tanaman cabai
Vmax = 25              # Laju maksimum penyerapan nutrisi
Km = 10                # Konsentrasi setengah laju maksimum (mol/L)

# Parameter Penyerapan nutrisi - U(t)
#U(t) = k * H(t) * T(t) * N(t)
k = 0.12               # Koefisien penyerapan nutrisi (efisiensi tinggi untuk cabai)

# Parameter pH tanah - P(t)
# 𝑑𝑃(𝑡) / d𝑡 = 𝜃𝐺(𝑊(𝑡) ∗ 𝑁(𝑡)) − 𝜆𝐶(𝑃(𝑡))

theta = 0.03           # Koefisien peningkatan pH
lambda_ = 0.015        # Koefisien penurunan pH

# Parameter dan variabel untuk pemodelan korelasi
# 1. Korelasi antara pH tanah pada kelembapan tanah jika terjadi proses pemupukan pada tanaman kemangi dan cabai 
# dT = (dQ / (pbV(Cs + Cw * W))) - (QCwdW / (pbV(Cs + Cw.W)pangkat 2)) 
rho_b = 1.2            # Massa jenis tanah (g/cm³)
C_s = 1.1              # Panas spesifik tanah (kJ/kg·°C)
C_w = 4.18             # Panas spesifik air (kJ/kg·°C)
dQ = 80                # Perubahan energi
dW = 0.08              # Perubahan kelembapan tanah
W = np.linspace(0.1, 0.5, 100)  # Kandungan air tanah

dpH = (dQ / (rho_b * V_pot * (C_s + C_w * W))) - (dQ * C_w * dW) / (rho_b * V_pot * (C_s + C_w * W)**2)

# 2. Korelasi antara kelembapan pada pengaruh suhu tanah dengan kandungan air berdasarkan proses penyerapannya 
# dW = (P + I − J − U − ET0 × Kc × Ks ) / pbV
# P = 6                  # Energi masuk (kJ)
# I = 3                  # Intensitas cahaya
# J = 1.5                # Panas hilang
# U = 2.5                # Penyerapan panas oleh tanaman
# ET0 = 4                # Evapotranspirasi (mm/hari)
# Kc = 0.9               # Koefisien tanaman
# Ks = 0.85              # Faktor ketersediaan air
P = 5        # Presipitasi (mm)
I = 2        # Irigasi (mm)
J = 1        # Limpasan permukaan tanah (mm)
U = 3        # Infiltrasi (mm)
ET0 = 2      # Evapotranspirasi aktual (mm/hari)
Kc = 0.8     # Koefisien tanaman
Ks = 0.9     # Koefisien stres air
dW_values = (P + I - J - U - ET0 * Kc * Ks) / (rho_b * V_pot)

# 3. Korelasi antara suhu tanah pada pengaruh pH tanah dan kelembapan tanah berdasarkan udara
# ΔTa = (∫A0 * exp(−z/D)) / 3D 
A0 = 12                # Parameter suhu tanah awal
D = 0.3                # Kedalaman efektif (m)
z = np.linspace(0, 0.5, 100)  # Kedalaman tanah (m)
delta_T = (A0 * np.exp(-z / D)) / (3 * D)

# Parameter fotosintesis
# P(t) = (Pmax * I(t)) / (K + I(t))
P_max = 35             # Laju fotosintesis maksimum (disesuaikan untuk cabai)
K = 20                 # Konstanta saturasi cahaya
# I_t = 150 * (1 + np.sin(2 * np.pi * t / 50))  # Intensitas cahaya (berfluktuasi)
I_t = 200 * (1 + np.sin(2 * np.pi * t / 50))

#Parameter Model Farquhar
# Pcarboxylation = Vmax * (C / (Kc + C)) * (O / (Ko + o)
# Pphotorespiration =  γ * (O / (Ko + o)
# Plight = α * I
alpha = 0.08           # Efisiensi fotosintesis cahaya
V_max = 60             # Laju maksimum karboksilasi
K_C = 40               # Konstanta CO₂
K_O = 350              # Konstanta O₂
gamma = 0.6            # Faktor respirasi foto
C = 400                # Konsentrasi CO₂ (ppm)
O = 210000             # Konsentrasi O₂ (ppm)

# Parameter suhu tanah
A0 = 10                # Parameter suhu tanah awal
D = 0.5                # Kedalaman efektif (m)
z = np.linspace(0, 2, 100)  # Kedalaman tanah (m)


# Parameter fase pertumbuhan
k1, k2, k3, k4 = 0.06, 0.035, 0.025, 0.015  # Koefisien fase pertumbuhan (disesuaikan untuk cabai)
Ns = 0.12             # Konsentrasi nutrisi untuk perkecambahan (mol/L)
F_t = 0.9             # Faktor pembentukan bunga

# Parameter sistem dinamis kelembapan tanah
I = 1.0    # Laju infiltrasi (mm/h atau cm³/h)
k_m = 0.02  # Konstanta transfer massa
H_a = 0.0   # Kelembapan udara awal (asumsi tidak ada pengaruh awal)
A_p = 0.5   # Laju serapan tanaman (mm/h atau cm³/h)
D = 0.3     # Faktor drainase (mm/h atau cm³/h)
M_t0 = 5.0  # Kelembapan awal tanah dalam persen atau volumetrik (%)

# =======================================
# 2. VARIABEL AWAL SIMULASI
# =======================================
# Variabel kelembapan tanah
H_t = np.zeros_like(t, dtype=float)  # Kelembapan tanah
E_t = 0.05 * (np.sin(2 * np.pi * t / 50) + 1)  # Penguapan
W_t_signal = np.zeros_like(t)  # Sinyal pemberian air

# Variabel nutrisi
N_t = np.zeros_like(t, dtype=float)  # Konsentrasi nutrisi
U_t = np.zeros_like(t, dtype=float)  # Penyerapan nutrisi

# Variabel pH tanah
P_t = np.zeros_like(t, dtype=float)  # pH tanah

# Variabel pertumbuhan tanaman
G_t = np.zeros_like(t, dtype=float)  # Perkecambahan
L_t = np.zeros_like(t, dtype=float)  # Pertumbuhan daun
B_t = np.zeros_like(t, dtype=float)  # Pembentukan bunga
Fb_t = np.zeros_like(t, dtype=float)  # Pembentukan buah
E_growth_t = np.zeros_like(t, dtype=float)  # Energi fotosintesis

# Variabel biomassa dan luas
B_t_stem = np.zeros_like(t, dtype=float)  # Biomassa batang
V_nutrisi = np.zeros_like(t, dtype=float)  # Laju pertumbuhan nutrisi
F_t_flower = np.zeros_like(t, dtype=float)  # Biomassa bunga
Ab_t = np.zeros_like(t, dtype=float)  # Luas bunga
Ad_t = np.zeros_like(t, dtype=float)  # Luas daun dari tunas
Ld_t = np.zeros_like(t, dtype=float)  # Luas daun
Ab_t[0] = 0.01
Ld_t[0] = 0.05
F_t_flower[0] = 0.01
Ad_t[0] = 0.01


# Variabel fotosintesis
P_t_energy = np.zeros_like(t, dtype=float)  # Energi fotosintesis
P_carb = np.zeros_like(t, dtype=float)      # Karboksilasi
P_photoresp = np.zeros_like(t, dtype=float) # Respirasi foto
P_light = np.zeros_like(t, dtype=float)     # Cahaya
P_farquhar = np.zeros_like(t, dtype=float)  # Output model Farquhar

M_t = np.zeros_like(t, dtype=float)  # Massa air dalam tanah
M_t[0] = M_t0  # Inisialisasi massa air awal

# =======================================
# 3. FUNGSI-FUNGSI MODEL
# =======================================

# Model kelembapan tanah
# dHt / dt = (W(t) / Vpot) - E(t)
def moisture_model(H_prev, W, E, V):
    return H_prev + (W / V) - E

# Model Nutrisi
# dN(t) / dt = (Cnutrisi(t) * W(t)) / Vpot - U(t)
def nutrient_model(N_prev, C_nutrisi, W, V, U):
    return N_prev + (C_nutrisi * W / V) - U

# Model Penyerapan Nutrisi
# U(t) = k * H(t) * T(t) * N(t)
def nutrient_absorption(k, H, T, N):
    return k * H * T * N

# Model pH Tanah
# 𝑑𝑃(𝑡) / d𝑡 = 𝜃𝐺(𝑊(𝑡) ∗ 𝑁(𝑡)) − 𝜆𝐶(𝑃(𝑡))
def ph_model(P_prev, W, N, theta, lambda_):
    G = np.log(1 + W * N)
    C = P_prev
    return P_prev + theta * G - lambda_ * C

# Model Energi Fotosintesis
# P(t) = (Pmax * I(t)) / (K + I(t))
def energy_model(P_max, I, K):
    return (P_max * I) / (K + I)

# Model Farquhar
# Pcarboxylation = Vmax * (C / (Kc + C)) * (O / (Ko + o)
# Pphotorespiration =  γ * (O / (Ko + o)
# Plight = α * I
def farquhar_model(V_max, C, O, K_C, K_O, gamma, alpha, I):
    P_carboxylation = V_max * (C / (K_C + C)) * (O / (K_O + O))
    P_photorespiration = gamma * (O / (K_O + O))
    P_light = alpha * I
    return min(P_carboxylation, P_photorespiration, P_light)

# Model Pertumbuhan Fase
# Fase 1: Bibit sampai Berkecambah
# 𝑑𝐺(𝑡) /𝑑𝑡	= 𝑘1. 𝑊𝑡 𝑇(𝑡). 𝑁(𝑠)
def germination_rate(W, T, Ns, k1):
    return k1 * W * T * Ns

'''
•	W(t): Kelembapan tanah pada waktu t
•	T(t) : Suhu tanah pada waktu t
•	Ns  :Nutrisi yang disimpan dalam biji
•	G(t) : Tingkat perkecambahan
•	k1 adalah konstanta pertumbuhan untuk fase ini.
'''

# Fase 2: Berkecambah sampai Bertumbuh Tunas Daun
# Model Energi yang diperoleh dari fotosintesis
# 𝐸(𝑡) = 𝛼. 𝑃𝑡 𝐼(𝑡)
# 𝑑𝐿(𝑡)  / 𝑑𝑡	= 𝑘2. 𝐸𝑡
'''
dimana:
•	E(t) : Energi yang diperoleh dari fotosintesis
•	P(t) : Laju fotosintesis
•	L(t) : Pertumbuhan daun
•	I(t) adalah intensitas cahaya matahari
•	P(t) adalah laju fotosintesis
•	k2 adalah konstanta pertumbuhan fase ini.
'''

def photosynthesis_energy(P, I, alpha):
    return alpha * P * I

def leaf_growth_rate(E, k2):
    return k2 * E

# Fase 3: Bertumbuh Daun hingga Berbunga
# 𝑑𝐵(𝑡) / 𝑑𝑡	= 𝑘3. 𝐿𝑡. 𝐹𝑡 
'''
dimana:
•	B(t) : Tingkat pembentukan bunga
•	L(t) : Pertumbuhan daun
•	F(t) : Faktor transisi dari daun ke bunga
•	F(t)bisa berupa rasio nutrisi yang berperan dalam memicu pembungaan.
'''
def flower_formation_rate(L, F, k3):
    return k3 * L * F

# Fase 4: Berbunga hingga Berbuah
# 𝑑𝐹𝑏(𝑡)  / 𝑑𝑡 = 𝑘4. 𝐵𝑡. 𝐸𝑡 
'''
•	Fb(t) : Tingkat pembentukan buah
•	B(t) : Jumlah bunga
•	E(t) : Energi fotosintesis
•	Setiap fase transisi ini dipengaruhi oleh variabel lingkungan seperti kelembapan tanah, suhu, dan intensitas cahaya matahari. Parameter k1,k2,k3,k4 mewakili konstanta spesifik yang dapat ditentukan
'''
def fruit_formation_rate(B, E, k4):
    return k4 * B * E

# Proses Fase Dorman
# Pertumbuhan Biomassa batang
# 𝑑𝐵 / 𝑑𝑡  = 𝑓(𝑇, 𝑊, 𝑁, 𝐿) 
'''
dimana:
•	B adalah biomassa batang
•	T adalah suhu (temp)
•	W adalah ketersediaan air (water) => setara dengan debit air
•	N adalah ketersediaan nutrisi (nutrients)
•	L adalah jumlah cahaya yang diterima (light)
'''
def stem_biomass_growth(T, W, N, L):
    return 0.1 * (T * W * N * L)

# Perhitungan Luas Daun
# 𝑑𝐿𝑑 / 𝑑𝑡 = 𝑟𝑔𝑟𝑜𝑤𝑡ℎ (𝑇, 𝑁, 𝑊, 𝐿). 𝐿𝑑 
'''
dimana:
•	Ld adalah luas daun
•	Rgrowth adalah laju pertumbuhan daun, yang tergantung pada suhu, ketersediaan air, nutrisi, dan Cahaya 
'''
def leaf_area_growth_rate(T, N, W, Ld):
    # rgrowth = 0.05 * (T + N + W + Ld)
    # return rgrowth * Ld
    rgrowth = 0.08 * (T + N + W + Ld)
    return rgrowth * Ld


# Perhitungan penyerapan nutrisi untuk mempengaruhi laju pertumbuhan daun
# 𝑉(𝑁) = (𝑉𝑚𝑎𝑥 𝑥 𝑁)  / (𝐾𝑚 + 𝑁)
'''
Di mana Vmax adalah laju maksimum penyerapan nutrisi dan Km adalah konsentrasi nutrisi pada setengah laju maksimum.
'''
def nutrient_growth(Vmax, N, Km):
    return (Vmax * N) / (Km + N)

# Fase membentuk cikal bakal bunga
# 𝑑𝐹/𝑑𝑡  = 𝑟𝑓𝑙𝑜𝑤𝑒𝑟(𝑇, 𝑁, 𝑊). 𝐹
'''
Di mana:

•	F adalah biomassa bunga
•	Rflower adalah laju pertumbuhan bunga yang dipengaruhi oleh suhu, air, dan nutrisi
'''
def flower_biomass_growth(T, N, W, F):
    # rflower = 0.02 * (T + N + W)
    # return rflower * F
    rflower = 0.05 * (T + N + W)
    return rflower * F

# Model Luas Bunga dan Kuncup Bunga dari Hari ke Hari
# 𝑑𝐴𝑏 / dt = 𝑟𝑏𝑢𝑛𝑔𝑎 . 𝐴𝑏 

'''
Di mana:

•	Ab adalah luas bunga pada hari tertentu.
•	Rbunga adalah laju pertumbuhan bunga yang dipengaruhi oleh suhu, cahaya, dan nutrisi, dapat dihitung sebagai:

𝑟𝑏𝑢𝑛𝑔𝑎 = 𝑓 (𝑇, 𝐿, 𝑁)

•	Di mana T adalah suhu, L adalah intensitas cahaya, dan N adalah ketersediaan nutrisi

'''
def flower_area_growth(T, L, N, Ab):
    # rbunga = 0.03 * (T + L + N)
    # return rbunga * Ab
    rbunga = 0.03 * (T + L + N) * np.exp(-0.05 * Ab)
    return rbunga * Ab


# Model Luas Daun dari Tunas ke Daun Dewasa dari Hari ke Hari
'''
𝑑𝐴𝑑 / dt = 𝑟𝑑𝑎𝑢𝑛 . 𝐴𝑑 
 
Di mana:

•	Ad adalah luas daun pada hari tertentu.
•	Rdaun adalah laju pertumbuhan daun yang dipengaruhi oleh suhu, cahaya, dan ketersediaan nutrisi, dengan persamaan:

𝑟𝑏𝑢𝑛𝑔𝑎 = 𝑓 (𝑇, 𝐿, 𝑁)

Di mana T adalah suhu, Ladalah intensitas cahaya, dan N adalah ketersediaan nutrisi. Implementasi dalam Bentuk Discrete Time
'''
def leaf_area_growth_from_shoots(T, L, N, Ad):
    rdaun = 0.10 * (T + L + N)
    return rdaun * Ad

def soil_moisture_dynamic(M_prev, I, k_m, H_a, A_p, D, dt):
    """
    Menghitung kelembapan tanah menggunakan metode Euler dengan pengaruh drainase.
    Rumus: dM_t/dt = I - [k_m * (M_t - H_a) + A_p + D]
    """
    dMt_dt = I - (k_m * (M_prev - H_a) + A_p + D)
    return M_prev + dMt_dt * dt

# =======================================
# 4. SIMULASI MODEL
# =======================================


for i in range(1, len(t)):
    # Cek kebutuhan air berdasarkan ambang batas
    W_t_signal[i] = W_pump if H_t[i-1] < threshold else 0
    
    # Model kelembapan tanah
    H_t[i] = moisture_model(H_t[i-1], W_t_signal[i], E_t[i], V_pot)
    H_t[i] = max(0, min(1, H_t[i]))

    # Penyerapan dan konsentrasi nutrisi
    U_t[i] = nutrient_absorption(k, H_t[i], temperature, N_t[i-1])
    N_t[i] = max(0, nutrient_model(N_t[i-1], C_nutrisi, W_t_signal[i], V_pot, U_t[i]))

    # Model pH tanah
    P_t[i] = max(0, min(14, ph_model(P_t[i-1], W_t_signal[i], N_t[i], theta, lambda_)))

    # Fase pertumbuhan
    G_t[i] += germination_rate(H_t[i], temperature, Ns, k1) * time_step
    E_growth_t[i] = photosynthesis_energy(P_t[i], I_t[i], alpha)
    L_t[i] += leaf_growth_rate(E_growth_t[i], k2) * time_step
    B_t[i] += flower_formation_rate(L_t[i], F_t, k3) * time_step
    Fb_t[i] += fruit_formation_rate(B_t[i], E_growth_t[i], k4) * time_step

    # Model energi fotosintesis dan Farquhar
    P_t_energy[i] = energy_model(P_max, I_t[i], K)
    P_farquhar[i] = farquhar_model(V_max, C, O, K_C, K_O, gamma, alpha, I_t[i])
    
    # Model biomassa dan luas
    B_t_stem[i] = max(0, B_t_stem[i-1] + stem_biomass_growth(temperature, W_t_signal[i], N_t[i], E_t[i]))
    Ld_t[i] = max(0, Ld_t[i-1] + leaf_area_growth_rate(temperature, N_t[i], W_t_signal[i], Ld_t[i-1]))
    V_nutrisi[i] = nutrient_growth(Vmax, N_t[i], Km)
    F_t_flower[i] = max(0, F_t_flower[i-1] + flower_biomass_growth(temperature, N_t[i], W_t_signal[i], F_t_flower[i-1]))
    Ab_t[i] = max(0, Ab_t[i-1] + flower_area_growth(temperature, E_t[i], N_t[i], Ab_t[i-1]))
    Ad_t[i] = max(0, Ad_t[i-1] + leaf_area_growth_from_shoots(temperature, E_t[i], N_t[i], Ad_t[i-1]))

    # Hitung kelembapan tanah menggunakan model dinamis
    M_t[i] = soil_moisture_dynamic(M_t[i - 1], I, k_m, H_a, A_p, D, time_step)
    # Pastikan nilai kelembapan tidak negatif
    M_t[i] = max(0, M_t[i])
# =======================================
# 5. VISUALISASI HASIL SIMULASI
# =======================================
# Plot figure 1: Model kelembapan, nutrisi, dan pH
plt.figure(figsize=(14, 12))

# Grafik Kelembapan Tanah
# Visualisasi hubungan antara kelembapan tanah, volume air masuk, dan penguapan.
plt.subplot(3, 1, 1)
plt.plot(t, H_t, label="H(t) - Kelembapan", color="green", linewidth=2)
plt.plot(t, W_t_signal / 10, label="W(t) - Volume Air Masuk (Scaled)", color="blue", linestyle="--")
plt.plot(t, E_t, label="E(t) - Penguapan", color="orange", linestyle="-.")
plt.axhline(y=threshold, color='red', linestyle='--', label="Ambang Batas (70%)")
plt.xlabel("Waktu (detik)")
plt.ylabel("Nilai")
plt.title("Grafik Kelembapan: H(t), W(t), dan E(t)")
plt.legend()
plt.grid()

# Grafik Nutrisi Tanah
# Visualisasi konsentrasi dan penyerapan nutrisi tanah.
plt.subplot(3, 1, 2)
plt.plot(t, N_t, label="N(t) - Konsentrasi Nutrisi", color="purple", linewidth=2)
plt.plot(t, U_t, label="U(t) - Penyerapan Nutrisi", color="teal", linestyle="--")
plt.plot(t, M_t, label="M(t) - Massa Air dalam Tanah", color="blue", linewidth=2)
# plt.axhline(y=D, color='red', linestyle='--', label="Drainase (D)")

plt.xlabel("Waktu (detik)")
plt.ylabel("Konsentrasi / Penyerapan")
plt.title("Grafik Konsentrasi dan Penyerapan Nutrisi")
plt.legend()
plt.grid()

# Grafik pH Tanah
# Visualisasi perubahan pH tanah selama simulasi.
plt.subplot(3, 1, 3)
plt.plot(t, P_t, label="P(t) - pH Tanah", color="brown", linewidth=2)
plt.xlabel("Waktu (detik)")
plt.ylabel("pH")
plt.title("Grafik Perubahan pH Tanah P(t)")
plt.legend()
plt.grid()

# Atur tata letak dan tampilkan
plt.tight_layout()
plt.show()

# =======================================
# Korelasi pH, Kelembapan, dan Suhu Tanah
plt.figure(figsize=(14, 10))


# Grafik dpH/dT
# Hubungan antara kandungan air dan perubahan pH tanah
plt.subplot(3, 1, 1)
plt.plot(W, dpH, label="dpH/dT", color="blue")
plt.xlabel("Kandungan Air (W)")
plt.ylabel("Perubahan pH (dpH/dT)")
plt.title("Korelasi pH Tanah dan Kelembapan Tanah")
plt.legend()
plt.grid()

# Grafik Input dan Output Air
# Visualisasi input (debit air, intensitas cahaya) dan output (penguapan)
plt.subplot(3, 1, 2)
plt.bar(["P + I", "J + U + ET0"], [P + I, J + U + ET0 * Kc * Ks], color=["green", "orange"])
# plt.axhline(y=dW_values, color="red", linestyle="--", label="dW (Kelembapan Tanah)")
plt.xlabel("Komponen Input dan Output")
plt.ylabel("Kelembapan Tanah (dW)")
plt.title("Korelasi Kelembapan dan Suhu Tanah")
plt.legend()
plt.grid()

# Grafik Suhu Tanah
# Perubahan suhu tanah berdasarkan kedalaman
plt.subplot(3, 1, 3)
plt.plot(z, delta_T, label="ΔT_A", color="purple")
plt.xlabel("Kedalaman Tanah (z)")
plt.ylabel("Perubahan Suhu Tanah (ΔT_A)")
plt.title("Korelasi Suhu Tanah dengan pH dan Kelembapan")
plt.legend()
plt.grid()

# Atur tata letak dan tampilkan
plt.tight_layout()
plt.show()

# =======================================
# Fase Pertumbuhan Tanaman
plt.figure(figsize=(14, 10))

# Grafik Fase 1: Perkecambahan
plt.subplot(4, 1, 1)
plt.plot(t, G_t, label="G(t) - Perkecambahan", color="green", linewidth=2)
plt.xlabel("Waktu (detik)")
plt.ylabel("Perkecambahan (G)")
plt.title("Fase 1: Bibit hingga Berkecambah")
plt.legend()
plt.grid()

# Grafik Fase 2: Pertumbuhan Daun
plt.subplot(4, 1, 2)
plt.plot(t, L_t, label="L(t) - Pertumbuhan Daun", color="blue", linewidth=2)
plt.plot(t, E_growth_t, label="E(t) - Energi Fotosintesis", color="orange", linestyle="--")
plt.xlabel("Waktu (detik)")
plt.ylabel("Pertumbuhan Daun (L) dan Energi (E)")
plt.title("Fase 2: Berkecambah hingga Bertunas Daun")
plt.legend()
plt.grid()

# Grafik Fase 3: Pembentukan Bunga
plt.subplot(4, 1, 3)
plt.plot(t, B_t, label="B(t) - Pembentukan Bunga", color="purple", linewidth=2)
plt.plot(t, E_growth_t, label="E(t) - Energi Fotosintesis", color="orange", linestyle="--")
plt.xlabel("Waktu (detik)")
plt.ylabel("Pembentukan Bunga (B)")
plt.title("Fase 3: Tumbuh Daun hingga Berbunga")
plt.legend()
plt.grid()

# Grafik Fase 4: Pembentukan Buah
plt.subplot(4, 1, 4)
plt.plot(t, Fb_t, label="Fb(t) - Pembentukan Buah", color="brown", linewidth=2)
plt.plot(t, E_growth_t, label="E(t) - Energi Fotosintesis", color="orange", linestyle="--")
plt.xlabel("Waktu (detik)")
plt.ylabel("Pembentukan Buah (Fb)")
plt.title("Fase 4: Berbunga hingga Berbuah")
plt.legend()
plt.grid()

# Atur tata letak dan tampilkan
plt.tight_layout()
plt.show()

# # =======================================
# # Grafik Energi dan Model Farquhar
# plt.figure(figsize=(14, 10))

# # Grafik Energi Fotosintesis
# plt.subplot(3, 1, 1)
# plt.plot(t, P_t_energy, label="P(t) - Energi Fotosintesis", color="green")
# plt.xlabel("Waktu (detik)")
# plt.ylabel("Energi (P)")
# plt.title("Energi Fotosintesis P(t)")
# plt.legend()
# plt.grid()

# # Komponen Farquhar
# plt.subplot(3, 1, 2)
# plt.plot(t, P_carb, label="P_carboxylation", color="blue")
# plt.plot(t, P_photoresp, label="P_photorespiration", color="orange")
# plt.plot(t, P_light, label="P_light", color="purple")
# plt.xlabel("Waktu (detik)")
# plt.ylabel("Komponen Fotosintesis")
# plt.title("Komponen Model Farquhar")
# plt.legend()
# plt.grid()

# # Output Model Farquhar
# plt.subplot(3, 1, 3)
# plt.plot(t, P_farquhar, label="P_farquhar (Minimum)", color="brown")
# plt.xlabel("Waktu (detik)")
# plt.ylabel("Output Farquhar")
# plt.title("Hasil Minimum Model Farquhar")
# plt.legend()
# plt.grid()

# # Atur tata letak dan tampilkan
# plt.tight_layout()
# plt.show()

# # =======================================
# Grafik Simulasi Biomassa dan Luas
plt.figure(figsize=(14, 10))

# Grafik Biomassa Batang
plt.subplot(3, 2, 1)
plt.plot(t, B_t_stem, label="Biomassa Batang (B_t)", color="brown")
plt.xlabel("Waktu (detik)")
plt.ylabel("Biomassa Batang")
plt.title("Biomassa Batang")
plt.legend()
plt.grid()

# Grafik Luas Daun
plt.subplot(3, 2, 2)
plt.plot(t, Ld_t, label="Luas Daun (Ld_t)", color="green")
plt.xlabel("Waktu (detik)")
plt.ylabel("Luas Daun")
plt.title("Luas Daun")
plt.legend()
plt.grid()

# Grafik Laju Pertumbuhan Nutrisi
plt.subplot(3, 2, 3)
plt.plot(t, V_nutrisi, label="Laju Nutrisi (V_t)", color="purple")
plt.xlabel("Waktu (detik)")
plt.ylabel("Laju Nutrisi")
plt.title("Laju Pertumbuhan Nutrisi")
plt.legend()
plt.grid()

# Grafik Biomassa Bunga
plt.subplot(3, 2, 4)
plt.plot(t, F_t_flower, label="Biomassa Bunga (F_t)", color="red")
plt.xlabel("Waktu (detik)")
plt.ylabel("Biomassa Bunga")
plt.title("Biomassa Bunga")
plt.legend()
plt.grid()

# Grafik Luas Bunga
plt.subplot(3, 2, 5)
plt.plot(t, Ab_t, label="Luas Bunga (Ab_t)", color="orange")
plt.xlabel("Waktu (detik)")
plt.ylabel("Luas Bunga")
plt.title("Luas Bunga")
plt.legend()
plt.grid()

# Grafik Luas Daun Tunas
plt.subplot(3, 2, 6)
plt.plot(t, Ad_t, label="Luas Daun Tunas (Ad_t)", color="blue")
plt.xlabel("Waktu (detik)")
plt.ylabel("Luas Daun")
plt.title("Luas Daun dari Tunas")
plt.legend()
plt.grid()

# Atur tata letak dan tampilkan
plt.tight_layout()
plt.show()

# plt.figure(figsize=(10, 6))
# plt.plot(t, M_t, label="M(t) - Massa Air dalam Tanah", color="blue", linewidth=2)
# plt.axhline(y=D, color='red', linestyle='--', label="Drainase (D)")
# plt.xlabel("Waktu (hari)")
# plt.ylabel("Kelembapan Tanah (%)")
# plt.title("Perubahan Kelembapan Tanah dengan Drainase")
# plt.legend()
# plt.grid()
# plt.show()