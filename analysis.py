"""
Analiza rynku wynajmu mieszkan we Wroclawiu
Dane: Otodom.pl (web scraping)
Projekt Big Data - CBE 6 Semestr
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os
import warnings
warnings.filterwarnings('ignore')

# Konfiguracja wykresów
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 12
plt.rcParams['figure.dpi'] = 120
sns.set_style("whitegrid")
sns.set_palette("husl")

OUTPUT_DIR = "plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =============================================================================
# 1. WCZYTANIE DANYCH
# =============================================================================
print("=" * 60)
print("1. WCZYTANIE DANYCH")
print("=" * 60)

df = pd.read_csv("wynajem_wroclaw.csv")
print(f"Wczytano {len(df)} ofert")
print(f"Kolumny: {df.columns.tolist()}")
print(f"\nTypy danych:\n{df.dtypes}")
print(f"\nPierwsze 5 wierszy:\n{df.head()}")
print(f"\nStatystyki opisowe:\n{df.describe()}")

# =============================================================================
# 2. CZYSZCZENIE DANYCH
# =============================================================================
print("\n" + "=" * 60)
print("2. CZYSZCZENIE DANYCH")
print("=" * 60)

# 2a. Raport braków
print(f"\nBraki danych PRZED czyszczeniem:")
nulls = df.isnull().sum()
for col in nulls.index:
    if nulls[col] > 0:
        pct = nulls[col] / len(df) * 100
        print(f"  {col}: {nulls[col]} ({pct:.1f}%)")

# 2b. Usunięcie kolumn w pełni pustych
empty_cols = [c for c in df.columns if df[c].isnull().all()]
if empty_cols:
    print(f"\nUsuwam puste kolumny: {empty_cols}")
    df = df.drop(columns=empty_cols)

# 2c. Mapowanie rooms i floor na wartości numeryczne
rooms_map = {
    'ONE': 1, 'TWO': 2, 'THREE': 3, 'FOUR': 4,
    'FIVE': 5, 'SIX': 6, 'SEVEN': 7, 'EIGHT': 8,
    'NINE': 9, 'TEN': 10
}
floor_map = {
    'GROUND': 0, 'FIRST': 1, 'SECOND': 2, 'THIRD': 3,
    'FOURTH': 4, 'FIFTH': 5, 'SIXTH': 6, 'SEVENTH': 7,
    'EIGHTH': 8, 'NINTH': 9, 'TENTH': 10,
    'ELEVENTH': 11, 'TWELFTH': 12, 'THIRTEENTH': 13,
    'FOURTEENTH': 14, 'FIFTEENTH': 15, 'SIXTEENTH': 16,
    'SEVENTEENTH': 17, 'ABOVE_17': 18, 'GARRET': -1, 'CELLAR': -2
}

df['rooms_num'] = df['rooms'].map(rooms_map)
df['floor_num'] = df['floor'].map(floor_map)

# 2d. Parsowanie lokalizacji — wyciągnięcie dzielnicy
df['district'] = df['location'].apply(
    lambda x: str(x).split(',')[0].strip() if pd.notna(x) else 'Brak'
)

# 2e. Usunięcie wierszy bez ceny lub powierzchni
before = len(df)
df = df.dropna(subset=['total_price', 'area'])
print(f"\nUsunięto {before - len(df)} ofert bez ceny/powierzchni")

# 2f. Usunięcie duplikatów
before = len(df)
df = df.drop_duplicates(subset=['id'], keep='first')
print(f"Usunięto {before - len(df)} duplikatów")

# 2g. Obliczenie ceny za m² (jeśli brak)
df['price_per_sqm_calc'] = df['total_price'] / df['area']

# 2h. Usunięcie outlierów — skrajne 5% cen za m²
q_low = df['price_per_sqm_calc'].quantile(0.025)
q_high = df['price_per_sqm_calc'].quantile(0.975)
before = len(df)
df = df[(df['price_per_sqm_calc'] >= q_low) & (df['price_per_sqm_calc'] <= q_high)]
print(f"Usunieto {before - len(df)} outlierow (cena/m2 poza [{q_low:.0f}, {q_high:.0f}] zl)")

# 2i. Filtracja nierealistycznych wartości
before = len(df)
df = df[(df['area'] >= 10) & (df['area'] <= 300)]
df = df[(df['total_price'] >= 500) & (df['total_price'] <= 30000)]
print(f"Usunięto {before - len(df)} nierealistycznych ofert")

print(f"\n>>> Po czyszczeniu: {len(df)} ofert")
print(f"Kolumny: {df.columns.tolist()}")
print(f"\nStatystyki po czyszczeniu:\n{df[['total_price','rent_price','area','rooms_num','floor_num','price_per_sqm_calc']].describe()}")

# Zapisz oczyszczone dane
df.to_csv("wynajem_wroclaw_clean.csv", index=False, encoding='utf-8')
print(f"\nZapisano oczyszczone dane do wynajem_wroclaw_clean.csv")

# =============================================================================
# 3. ANALIZA EKSPLORACYJNA (EDA)
# =============================================================================
print("\n" + "=" * 60)
print("3. ANALIZA EKSPLORACYJNA")
print("=" * 60)

# ---------------------------------------------------------------------------
# 3a. Rozkład powierzchni mieszkań
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 6))
ax.hist(df['area'], bins=50, color='#4C72B0', edgecolor='white', alpha=0.85)
median_area = df['area'].median()
mean_area = df['area'].mean()
ax.axvline(median_area, color='black', linewidth=2, linestyle='--', label=f'Mediana: {median_area:.0f} m²')
ax.axvline(mean_area, color='red', linewidth=2, linestyle='--', label=f'Średnia: {mean_area:.0f} m²')
ax.set_xlabel('Powierzchnia [m²]')
ax.set_ylabel('Liczba ofert')
ax.set_title('Rozkład powierzchni mieszkań do wynajęcia we Wrocławiu')
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/01_rozklad_powierzchni.png')
plt.close()
print(f"Mediana powierzchni: {median_area:.0f} m², średnia: {mean_area:.0f} m²")

# ---------------------------------------------------------------------------
# 3b. Rozkład cen całkowitych
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 6))
ax.hist(df['total_price'], bins=50, color='#55A868', edgecolor='white', alpha=0.85)
median_price = df['total_price'].median()
mean_price = df['total_price'].mean()
ax.axvline(median_price, color='black', linewidth=2, linestyle='--', label=f'Mediana: {median_price:.0f} zł')
ax.axvline(mean_price, color='red', linewidth=2, linestyle='--', label=f'Średnia: {mean_price:.0f} zł')
ax.set_xlabel('Cena [zł]')
ax.set_ylabel('Liczba ofert')
ax.set_title('Rozkład cen wynajmu mieszkań we Wrocławiu')
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/02_rozklad_cen.png')
plt.close()
print(f"Mediana ceny: {median_price:.0f} zł, średnia: {mean_price:.0f} zł")

# ---------------------------------------------------------------------------
# 3c. Rozkład cen za m²
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 6))
ax.hist(df['price_per_sqm_calc'], bins=50, color='#C44E52', edgecolor='white', alpha=0.85)
median_psm = df['price_per_sqm_calc'].median()
mean_psm = df['price_per_sqm_calc'].mean()
ax.axvline(median_psm, color='black', linewidth=2, linestyle='--', label=f'Mediana: {median_psm:.1f} zł/m²')
ax.axvline(mean_psm, color='red', linewidth=2, linestyle='--', label=f'Średnia: {mean_psm:.1f} zł/m²')
ax.set_xlabel('Cena za m² [zł]')
ax.set_ylabel('Liczba ofert')
ax.set_title('Rozkład ceny za metr kwadratowy wynajmu we Wrocławiu')
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/03_rozklad_cena_za_m2.png')
plt.close()
print(f"Mediana ceny/m²: {median_psm:.1f} zł, średnia: {mean_psm:.1f} zł")

# ---------------------------------------------------------------------------
# 3d. Liczba pokoi — rozkład
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))
rooms_counts = df['rooms_num'].dropna().value_counts().sort_index()
colors = sns.color_palette("husl", len(rooms_counts))
bars = ax.bar(rooms_counts.index.astype(int), rooms_counts.values, color=colors, edgecolor='white')
for bar, val in zip(bars, rooms_counts.values):
    pct = val / rooms_counts.sum() * 100
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 5,
            f'{pct:.1f}%', ha='center', va='bottom', fontsize=10)
ax.set_xlabel('Liczba pokoi')
ax.set_ylabel('Liczba ofert')
ax.set_title('Rozkład liczby pokoi w ofertach wynajmu')
ax.set_xticks(rooms_counts.index.astype(int))
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/04_rozklad_pokoi.png')
plt.close()
print(f"\nLiczba pokoi:\n{rooms_counts}")

# ---------------------------------------------------------------------------
# 3e. Analiza per dzielnica — mediana ceny/m²
# ---------------------------------------------------------------------------
district_stats = df.groupby('district').agg(
    mediana_cena_m2=('price_per_sqm_calc', 'median'),
    mediana_cena=('total_price', 'median'),
    mediana_pow=('area', 'median'),
    liczba_ofert=('id', 'count')
).reset_index()
district_stats = district_stats[district_stats['liczba_ofert'] >= 10]
district_stats = district_stats.sort_values('mediana_cena_m2', ascending=False)

fig, ax = plt.subplots(figsize=(12, 8))
bars = ax.barh(district_stats['district'], district_stats['mediana_cena_m2'],
               color=sns.color_palette("RdYlGn_r", len(district_stats)))
for bar, val, cnt in zip(bars, district_stats['mediana_cena_m2'], district_stats['liczba_ofert']):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2.,
            f'{val:.0f} zł/m² (n={cnt})', ha='left', va='center', fontsize=9)
ax.set_xlabel('Mediana ceny za m² [zł]')
ax.set_title('Mediana ceny wynajmu za m² wg dzielnicy (min. 10 ofert)')
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/05_cena_m2_dzielnice.png')
plt.close()
print(f"\nCeny za m² per dzielnica:\n{district_stats.to_string(index=False)}")

# ---------------------------------------------------------------------------
# 3f. Liczba ofert per dzielnica
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 8))
dist_sorted = district_stats.sort_values('liczba_ofert', ascending=True)
ax.barh(dist_sorted['district'], dist_sorted['liczba_ofert'],
        color=sns.color_palette("Blues_d", len(dist_sorted)))
ax.set_xlabel('Liczba ofert')
ax.set_title('Liczba ofert wynajmu wg dzielnicy')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/06_oferty_dzielnice.png')
plt.close()

# ---------------------------------------------------------------------------
# 3g. Scatter: powierzchnia vs cena (z regresją)
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 7))
ax.scatter(df['area'], df['total_price'], alpha=0.3, s=15, color='#4C72B0')
# Linia regresji
slope, intercept, r, p, se = stats.linregress(df['area'], df['total_price'])
x_line = np.linspace(df['area'].min(), df['area'].max(), 100)
ax.plot(x_line, slope * x_line + intercept, color='red', linewidth=2,
        label=f'Regresja liniowa (R²={r**2:.2f})')
ax.set_xlabel('Powierzchnia [m²]')
ax.set_ylabel('Cena [zł]')
ax.set_title('Zależność ceny od powierzchni mieszkania')
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/07_powierzchnia_vs_cena.png')
plt.close()
print(f"\nRegresja cena~powierzchnia: R²={r**2:.3f}, nachylenie={slope:.1f} zł/m²")

# ---------------------------------------------------------------------------
# 3h. Cena za m² w zależności od powierzchni
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 6))
ax.scatter(df['area'], df['price_per_sqm_calc'], alpha=0.3, s=15, color='#C44E52')
# Wygładzenie LOWESS
try:
    from statsmodels.nonparametric.smoothers_lowess import lowess
    smooth = lowess(df['price_per_sqm_calc'], df['area'], frac=0.3)
    ax.plot(smooth[:, 0], smooth[:, 1], color='black', linewidth=2.5, label='Trend (LOWESS)')
    ax.legend(fontsize=11)
except ImportError:
    # Średnia krocząca jako alternatywa
    df_sorted = df.sort_values('area')
    ax.plot(df_sorted['area'], df_sorted['price_per_sqm_calc'].rolling(50, center=True).mean(),
            color='black', linewidth=2.5, label='Średnia krocząca')
    ax.legend(fontsize=11)
ax.set_xlabel('Powierzchnia [m²]')
ax.set_ylabel('Cena za m² [zł]')
ax.set_title('Cena za m² w zależności od powierzchni')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/08_cena_m2_vs_powierzchnia.png')
plt.close()

# ---------------------------------------------------------------------------
# 3i. Boxplot: cena wg liczby pokoi
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 6))
rooms_data = df.dropna(subset=['rooms_num'])
rooms_data = rooms_data[rooms_data['rooms_num'] <= 6]
sns.boxplot(data=rooms_data, x='rooms_num', y='total_price', ax=ax, palette='husl')
ax.set_xlabel('Liczba pokoi')
ax.set_ylabel('Cena [zł]')
ax.set_title('Cena wynajmu w zależności od liczby pokoi')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/09_cena_vs_pokoje.png')
plt.close()

# ---------------------------------------------------------------------------
# 3j. Boxplot: cena/m² wg liczby pokoi per dzielnica (top 6)
# ---------------------------------------------------------------------------
top_districts = df['district'].value_counts().head(6).index.tolist()
df_top = df[df['district'].isin(top_districts)].dropna(subset=['rooms_num'])
df_top = df_top[df_top['rooms_num'] <= 4]

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
for ax, dist in zip(axes.flatten(), top_districts):
    sub = df_top[df_top['district'] == dist]
    sns.boxplot(data=sub, x='rooms_num', y='total_price', ax=ax, palette='Set2')
    ax.set_title(dist, fontsize=13, fontweight='bold')
    ax.set_xlabel('Pokoje')
    ax.set_ylabel('Cena [zł]')
plt.suptitle('Cena wynajmu wg liczby pokoi — top 6 dzielnic', fontsize=15, y=1.02)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/10_cena_pokoje_dzielnice.png', bbox_inches='tight')
plt.close()

# ---------------------------------------------------------------------------
# 3k. Boxplot: cena wg piętra
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 6))
floor_data = df.dropna(subset=['floor_num'])
floor_data = floor_data[(floor_data['floor_num'] >= 0) & (floor_data['floor_num'] <= 10)]
sns.boxplot(data=floor_data, x='floor_num', y='total_price', ax=ax, palette='coolwarm')
ax.set_xlabel('Piętro')
ax.set_ylabel('Cena [zł]')
ax.set_title('Cena wynajmu w zależności od piętra')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/11_cena_vs_pietro.png')
plt.close()

# ---------------------------------------------------------------------------
# 3l. Heatmapa korelacji
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 8))
num_cols = ['total_price', 'rent_price', 'area', 'rooms_num', 'floor_num', 'price_per_sqm_calc']
corr = df[num_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
            center=0, square=True, ax=ax,
            xticklabels=['Cena', 'Czynsz adm.', 'Powierzchnia', 'Pokoje', 'Piętro', 'Cena/m²'],
            yticklabels=['Cena', 'Czynsz adm.', 'Powierzchnia', 'Pokoje', 'Piętro', 'Cena/m²'])
ax.set_title('Macierz korelacji zmiennych')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/12_korelacja.png')
plt.close()
print(f"\nMacierz korelacji:\n{corr.round(2)}")

# ---------------------------------------------------------------------------
# 3m. Rozkład pokoi per dzielnica (stacked %)
# ---------------------------------------------------------------------------
rooms_district = pd.crosstab(df['district'], df['rooms_num'], normalize='index') * 100
rooms_district = rooms_district.loc[top_districts]
rooms_district.columns = [f'{int(c)} pok.' for c in rooms_district.columns]

fig, ax = plt.subplots(figsize=(12, 7))
rooms_district.plot(kind='barh', stacked=True, ax=ax, colormap='Set2', edgecolor='white')
ax.set_xlabel('Udział procentowy [%]')
ax.set_title('Struktura mieszkań wg liczby pokoi — top dzielnice')
ax.legend(title='Pokoje', bbox_to_anchor=(1.01, 1), loc='upper left')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/13_pokoje_dzielnice_stacked.png', bbox_inches='tight')
plt.close()

# ---------------------------------------------------------------------------
# 3n. Przedziały powierzchni per dzielnica
# ---------------------------------------------------------------------------
df['area_bin'] = pd.cut(df['area'], bins=[0, 30, 45, 60, 80, 300],
                        labels=['<30 m²', '30-45 m²', '45-60 m²', '60-80 m²', '>80 m²'])
area_district = pd.crosstab(df['district'], df['area_bin'], normalize='index') * 100
area_district = area_district.loc[top_districts]

fig, ax = plt.subplots(figsize=(12, 7))
area_district.plot(kind='barh', stacked=True, ax=ax, colormap='YlOrRd', edgecolor='white')
ax.set_xlabel('Udział procentowy [%]')
ax.set_title('Struktura mieszkań wg powierzchni — top dzielnice')
ax.legend(title='Powierzchnia', bbox_to_anchor=(1.01, 1), loc='upper left')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/14_powierzchnia_dzielnice.png', bbox_inches='tight')
plt.close()

# ---------------------------------------------------------------------------
# 3o. Kalkulator: ile powinien kosztować wynajem
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("4. ILE POWINIEN KOSZTOWAĆ WYNAJEM?")
print("=" * 60)

# Tabela: dzielnica × pokoje → mediana ceny
pivot = df.pivot_table(values='total_price', index='district', columns='rooms_num',
                       aggfunc='median').round(0)
pivot.columns = [f'{int(c)} pok.' for c in pivot.columns]
# Filtruj dzielnice z min 10 ofertami
valid_districts = df['district'].value_counts()
valid_districts = valid_districts[valid_districts >= 10].index
pivot = pivot.loc[pivot.index.isin(valid_districts)]
pivot = pivot.sort_index()

print("\nMediana ceny wynajmu [zł] wg dzielnicy i liczby pokoi:")
print(pivot.to_string())

# Heatmapa kalkulator
fig, ax = plt.subplots(figsize=(12, 8))
pivot_plot = pivot.dropna(how='all')
sns.heatmap(pivot_plot, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax,
            linewidths=0.5, linecolor='white')
ax.set_title('Mediana ceny wynajmu [zł] — dzielnica × pokoje')
ax.set_ylabel('Dzielnica')
ax.set_xlabel('Liczba pokoi')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/15_kalkulator_cen.png')
plt.close()

# ---------------------------------------------------------------------------
# PODSUMOWANIE
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("PODSUMOWANIE ANALIZY")
print("=" * 60)
print(f"""
Dane: {len(df)} ofert wynajmu mieszkań we Wrocławiu (Otodom.pl)

Kluczowe statystyki:
  • Mediana ceny:           {df['total_price'].median():.0f} zł/mies.
  • Średnia ceny:           {df['total_price'].mean():.0f} zł/mies.
  • Mediana powierzchni:    {df['area'].median():.0f} m²
  • Mediana ceny za m²:     {df['price_per_sqm_calc'].median():.1f} zł/m²
  • Najczęstsze mieszkanie: {int(df['rooms_num'].mode().iloc[0])}-pokojowe, ~{df['area'].median():.0f} m²

Najdroższe dzielnice (mediana ceny/m²):
{district_stats.head(5)[['district','mediana_cena_m2','liczba_ofert']].to_string(index=False)}

Najtańsze dzielnice (mediana ceny/m²):
{district_stats.tail(5)[['district','mediana_cena_m2','liczba_ofert']].to_string(index=False)}

Wygenerowano {len(os.listdir(OUTPUT_DIR))} wykresów w katalogu '{OUTPUT_DIR}/'.
""")
