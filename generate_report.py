"""
Generowanie raportu PDF z opisem projektu Big Data.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from fpdf import FPDF
import pandas as pd
import os

# --- Wczytanie danych do statystyk ---
df_raw = pd.read_csv("wynajem_wroclaw.csv")
df = pd.read_csv("wynajem_wroclaw_clean.csv")

PLOTS_DIR = "plots"

class PDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(128)
            self.cell(0, 5, "Projekt Big Data - Analiza rynku wynajmu mieszkan we Wroclawiu", align="C")
            self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, f"Strona {self.page_no()}/{{nb}}", align="C")

    def chapter_title(self, title):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(30, 60, 120)
        self.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(30, 60, 120)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def section_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(50, 50, 50)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.set_x(self.l_margin)
        self.multi_cell(0, 5.5, "  - " + text)

    def add_plot(self, path, caption="", w=170):
        if os.path.exists(path):
            self.image(path, x=(210 - w) / 2, w=w)
            if caption:
                self.set_font("Helvetica", "I", 9)
                self.set_text_color(100)
                self.cell(0, 6, caption, align="C", new_x="LMARGIN", new_y="NEXT")
            self.ln(4)


pdf = PDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=20)

# ============================================================
# STRONA TYTULOWA
# ============================================================
pdf.add_page()
pdf.ln(50)
pdf.set_font("Helvetica", "B", 28)
pdf.set_text_color(30, 60, 120)
pdf.cell(0, 15, "Analiza rynku wynajmu", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 15, "mieszkan we Wroclawiu", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(10)
pdf.set_font("Helvetica", "", 14)
pdf.set_text_color(80)
pdf.cell(0, 8, "Eksploracja danych z serwisu Otodom.pl", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)
pdf.set_draw_color(30, 60, 120)
pdf.line(60, pdf.get_y(), 150, pdf.get_y())
pdf.ln(10)
pdf.set_font("Helvetica", "", 12)
pdf.set_text_color(60)
pdf.cell(0, 8, "Projekt Big Data - CBE 6 Semestr", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, "Maj 2026", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(30)
pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(100)
pdf.cell(0, 6, f"Dane: {len(df_raw)} ofert (surowe) / {len(df)} ofert (po czyszczeniu)", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 6, "Zrodlo: www.otodom.pl | Technologia: Python, BeautifulSoup, Pandas, Matplotlib", align="C", new_x="LMARGIN", new_y="NEXT")

# ============================================================
# 1. WSTEP
# ============================================================
pdf.add_page()
pdf.chapter_title("1. Wstep i cel projektu")
pdf.body_text(
    "Celem projektu jest przeprowadzenie pelnej eksploracji danych (EDA) dotyczacych rynku "
    "wynajmu mieszkan we Wroclawiu. Projekt realizuje cztery kluczowe etapy pracy z danymi:"
)
pdf.bullet("Pobranie danych ze zrodla internetowego (web scraping)")
pdf.bullet("Wybor zagadnienia do analizy - wynajem mieszkan we Wroclawiu")
pdf.bullet("Czyszczenie i przygotowanie danych")
pdf.bullet("Analiza eksploracyjna z wizualizacjami")
pdf.ln(3)
pdf.body_text(
    "Projekt inspirowany jest analizami z bloga prokulski.science, w szczegolnosci "
    "wpisem 'Mieszkanie do wynajecia' analizujacym ceny wynajmu mieszkan w polskich miastach. "
    "Dane zostaly pobrane z serwisu Otodom.pl - jednego z najwiekszych portali "
    "nieruchomosciowych w Polsce."
)

# ============================================================
# 2. POBRANIE DANYCH
# ============================================================
pdf.chapter_title("2. Pobranie danych (Web Scraping)")
pdf.body_text(
    "Dane zostaly pobrane za pomoca skryptu scraper.py napisanego w Pythonie. "
    "Skrypt wykorzystuje biblioteki requests i BeautifulSoup do pobierania stron "
    "z wynikami wyszukiwania Otodom.pl."
)
pdf.section_title("2.1 Metoda scrapingu")
pdf.body_text(
    "Otodom.pl jest aplikacja Next.js, ktora przechowuje dane wyszukiwania w tagu "
    "<script id='__NEXT_DATA__'> w formacie JSON. Zamiast parsowac skomplikowany HTML, "
    "skrypt wyciaga ten tag i dekoduje JSON, uzyskujac dokladne dane kazdego ogloszenia. "
    "Ta metoda gwarantuje 100% dokladnosc pobranych informacji."
)
pdf.section_title("2.2 Konfiguracja")
pdf.body_text(
    "Parametry scrapingu sa definiowane w pliku options.json:\n"
    "- Typ transakcji: wynajem\n"
    "- Typ nieruchomosci: mieszkanie\n"
    "- Region: dolnoslaskie, miasto: Wroclaw\n"
    "- Liczba stron: 50 (okolo 37 ofert na strone)\n"
    "- Opoznienie miedzy zapytaniami: 1.5-3.5 sekundy (unikniecie blokady IP)"
)
pdf.section_title("2.3 Pobrane pola")
pdf.body_text(
    "Dla kazdego ogloszenia pobierane sa nastepujace informacje:\n"
    "- id - unikalny identyfikator ogloszenia\n"
    "- title - tytul ogloszenia\n"
    "- total_price - calkowita cena wynajmu [zl]\n"
    "- rent_price - czynsz administracyjny [zl]\n"
    "- price_per_sqm - cena za metr kwadratowy [zl/m2]\n"
    "- area - powierzchnia mieszkania [m2]\n"
    "- rooms - liczba pokoi\n"
    "- floor - pietro\n"
    "- location - lokalizacja (dzielnica, miasto)\n"
    "- url - link do ogloszenia"
)
pdf.body_text(f"Laczny wynik: {len(df_raw)} unikalnych ofert pobranych z 50 stron wynikow.")

# ============================================================
# 3. CZYSZCZENIE DANYCH
# ============================================================
pdf.add_page()
pdf.chapter_title("3. Czyszczenie danych")
pdf.body_text(
    "Surowe dane wymagaly kilku etapow czyszczenia, zanim mogly byc poddane analizie."
)

pdf.section_title("3.1 Raport brakow danych")
pdf.body_text(
    f"Przed czyszczeniem w {len(df_raw)} ofertach zidentyfikowano nastepujace braki:\n"
    "- total_price: 3 oferty (0.2%) - brak podanej ceny\n"
    "- rent_price: 154 oferty (8.4%) - brak czynszu administracyjnego\n"
    "- floor: 27 ofert (1.5%) - brak informacji o pietrze\n"
    "- rooms: 3 oferty (0.2%) - brak liczby pokoi\n"
    "Kolumny building_type, heating_type, year_built, ownership oraz created_at "
    "byly puste w 100% przypadkow (dane te nie sa dostepne na stronie listingu) - zostaly usuniete."
)

pdf.section_title("3.2 Konwersja typow danych")
pdf.body_text(
    "Otodom zwraca liczbe pokoi i pietro jako tekst angielski (np. 'ONE', 'TWO', 'GROUND', 'FIRST'). "
    "Wartosci te zostaly zamienione na liczby calkowite za pomoca slownikow mapujacych:\n"
    "- ONE -> 1, TWO -> 2, THREE -> 3 itd.\n"
    "- GROUND -> 0, FIRST -> 1, SECOND -> 2 itd."
)

pdf.section_title("3.3 Parsowanie lokalizacji")
pdf.body_text(
    "Pole 'location' zawiera pelna lokalizacje w formacie 'Dzielnica, Wroclaw, dolnoslaskie'. "
    "Wyodrebniono nazwe dzielnicy jako pierwszy element przed przecinkiem - "
    "jest to kluczowa zmienna do analizy przestrzennej cen."
)

pdf.section_title("3.4 Usuwanie outlierow")
pdf.body_text(
    "Zastosowano nastepujace filtry:\n"
    "- Usunieto oferty bez ceny lub powierzchni (3 oferty)\n"
    "- Odcieto skrajne 2.5% cen za m2 z obu stron rozkladu (91 ofert) - "
    "aby wyeliminowac bledne wpisy (np. cena sprzedazy zamiast wynajmu, "
    "wynajem pojedynczego pokoju z podana powierzchnia calego mieszkania)\n"
    "- Odfiltrowano nierealistyczne wartosci: powierzchnia < 10 m2 lub > 300 m2, "
    "cena < 500 zl lub > 30 000 zl"
)
pdf.body_text(f"Po czyszczeniu pozostalo {len(df)} ofert gotowych do analizy.")

# ============================================================
# 4. ANALIZA DANYCH
# ============================================================
pdf.add_page()
pdf.chapter_title("4. Analiza eksploracyjna danych")

# Statystyki
med_price = df['total_price'].median()
mean_price = df['total_price'].mean()
med_area = df['area'].median()
med_psm = df['price_per_sqm_calc'].median()

pdf.section_title("4.1 Podstawowe statystyki")
pdf.body_text(
    f"Kluczowe miary centralne dla {len(df)} ofert:\n"
    f"- Mediana ceny wynajmu: {med_price:.0f} zl/miesiac\n"
    f"- Srednia ceny wynajmu: {mean_price:.0f} zl/miesiac\n"
    f"- Mediana powierzchni: {med_area:.0f} m2\n"
    f"- Mediana ceny za m2: {med_psm:.1f} zl/m2\n"
    f"- Najczestsze mieszkanie: 2-pokojowe (~56% ofert)"
)
pdf.body_text(
    "Srednia jest wyzsza od mediany, co wskazuje na prawostronnie skosny rozklad cen - "
    "kilka drogich ofert zawyza srednia. Dlatego w dalszej analizie opieramy sie na medianach, "
    "zgodnie z podejsciem Prokulskiego."
)

pdf.section_title("4.2 Rozklad powierzchni mieszkan")
pdf.add_plot(f"{PLOTS_DIR}/01_rozklad_powierzchni.png", "Rys. 1: Rozklad powierzchni mieszkan do wynajecia")
pdf.body_text(
    f"Polowa mieszkan wystawionych na wynajem ma powierzchnie mniejsza niz {med_area:.0f} m2. "
    "Rozklad jest prawostronnie skosny - przewazaja mniejsze mieszkania. "
    "Dominuja lokale o powierzchni 25-55 m2, co odpowiada popularnym kawalerkom i mieszkaniom 2-pokojowym."
)

pdf.section_title("4.3 Rozklad cen wynajmu")
pdf.add_plot(f"{PLOTS_DIR}/02_rozklad_cen.png", "Rys. 2: Rozklad cen wynajmu")
pdf.body_text(
    f"Mediana ceny wynajmu to {med_price:.0f} zl. Wiekszosc ofert miesci sie w przedziale "
    "2000-4000 zl. Rozklad jest wyraznie prawostronnie skosny - nieliczne oferty luksusowych "
    "apartamentow znaczaco przekraczaja typowe ceny."
)

pdf.add_page()
pdf.section_title("4.4 Rozklad ceny za metr kwadratowy")
pdf.add_plot(f"{PLOTS_DIR}/03_rozklad_cena_za_m2.png", "Rys. 3: Rozklad ceny za m2")
pdf.body_text(
    f"Cena za metr kwadratowy - najbardziej miarodajna miara do porownywania ofert - "
    f"ma mediane {med_psm:.1f} zl/m2. Rozklad jest bardziej symetryczny niz ceny calkowitej, "
    "co potwierdza ze cena za m2 jest lepsza metyka porownawcza."
)

pdf.section_title("4.5 Struktura ofert wg liczby pokoi")
pdf.add_plot(f"{PLOTS_DIR}/04_rozklad_pokoi.png", "Rys. 4: Rozklad liczby pokoi")
pdf.body_text(
    "Zdecydowana wiekszosc ofert (56%) to mieszkania 2-pokojowe. "
    "Drugie w kolejnosci sa 3-pokojowe (22%), a trzecie kawalerki (19%). "
    "Mieszkania 4+ pokojowe stanowia margines rynku wynajmu."
)

pdf.add_page()
pdf.section_title("4.6 Analiza cen wg dzielnic Wroclawia")
pdf.add_plot(f"{PLOTS_DIR}/05_cena_m2_dzielnice.png", "Rys. 5: Mediana ceny za m2 wg dzielnicy")
pdf.body_text(
    "Najdrozszymi dzielnicami sa Srodmiescie i Stare Miasto (70 zl/m2) - co jest zgodne "
    "z intuicja, gdyz sa to centralne i najbardziej prestizowe lokalizacje. "
    "Krzyki (64 zl/m2) i Fabryczna (63 zl/m2) sa w srednim przedziale cenowym. "
    "Najtansze jest Psie Pole (62 zl/m2), co wynika z polozenia na obrzezach miasta."
)

pdf.add_plot(f"{PLOTS_DIR}/06_oferty_dzielnice.png", "Rys. 6: Liczba ofert wg dzielnicy")
pdf.body_text(
    "Najwiecej ofert jest na Krzykach (592), co moze wynikac z duzej liczby nowych inwestycji "
    "deweloperskich w tej dzielnicy. Stare Miasto i Fabryczna rowniez maja bogata oferte."
)

pdf.add_page()
pdf.section_title("4.7 Zaleznosc ceny od powierzchni")
pdf.add_plot(f"{PLOTS_DIR}/07_powierzchnia_vs_cena.png", "Rys. 7: Scatter plot - powierzchnia vs cena z regresja liniowa")
pdf.body_text(
    "Widac wyrazna, prawie liniowa zaleznosc - wspolczynnik determinacji R2 = 0.63. "
    "Kazdy dodatkowy metr kwadratowy kosztuje srednio okolo 51 zl wiecej czynszu. "
    "Zaleznosc jest intuicyjna: im wieksze mieszkanie, tym drozszy wynajem."
)

pdf.section_title("4.8 Cena za m2 w zaleznosci od powierzchni")
pdf.add_plot(f"{PLOTS_DIR}/08_cena_m2_vs_powierzchnia.png", "Rys. 8: Cena za m2 vs powierzchnia")
pdf.body_text(
    "Ciekawe zjawisko - mniejsze mieszkania maja wyzsza cene za m2 niz wieksze. "
    "Wynika to z mechanizmow rynkowych: kawalerki sa najbardziej poszukiwane (studenci, single), "
    "wiec konkurencja winduje cene jednostkowa. Wieksze mieszkania maja nizsza cene za m2 "
    "ze wzgledu na mniejszy popyt."
)

pdf.add_page()
pdf.section_title("4.9 Cena wg liczby pokoi")
pdf.add_plot(f"{PLOTS_DIR}/09_cena_vs_pokoje.png", "Rys. 9: Boxplot ceny wg liczby pokoi")
pdf.body_text(
    "Zgodnie z oczekiwaniami, cena rosnie wraz z liczba pokoi. Mediana dla 1-pokojowego "
    "to okolo 2200 zl, dla 2-pokojowego 2800 zl, a dla 3-pokojowego 3500 zl. "
    "Rozrzut cen rosnie tez z liczba pokoi - wieksze mieszkania maja wieksza wariancje cenowa."
)

pdf.section_title("4.10 Cena wg pokoi w top 6 dzielnicach")
pdf.add_plot(f"{PLOTS_DIR}/10_cena_pokoje_dzielnice.png", "Rys. 10: Cena vs pokoje w podziale na dzielnice", w=180)
pdf.body_text(
    "Analiza w podziale na dzielnice ujawnia roznice lokalne. Np. 3-pokojowe mieszkanie "
    "w Srodmiesciu kosztuje ~4200 zl, podczas gdy na Psim Polu tylko ~3200 zl."
)

pdf.add_page()
pdf.section_title("4.11 Wplyw pietra na cene")
pdf.add_plot(f"{PLOTS_DIR}/11_cena_vs_pietro.png", "Rys. 11: Cena wynajmu wg pietra")
pdf.body_text(
    "Pietro ma minimalny wplyw na cene wynajmu (korelacja = 0.04). "
    "Mediany sa zblizione na wszystkich pietrach, co sugeruje, ze na rynku wynajmu "
    "pietro nie jest tak istotnym czynnikiem cenowym jak na rynku sprzedazy."
)

pdf.section_title("4.12 Macierz korelacji")
pdf.add_plot(f"{PLOTS_DIR}/12_korelacja.png", "Rys. 12: Macierz korelacji zmiennych")
pdf.body_text(
    "Najsilniejsze korelacje:\n"
    "- Powierzchnia <-> Pokoje: 0.82 (oczywista zaleznosc)\n"
    "- Cena <-> Powierzchnia: 0.79 (kluczowy czynnik cenowy)\n"
    "- Cena <-> Pokoje: 0.69\n"
    "- Cena/m2 <-> Powierzchnia: -0.46 (mniejsze mieszkania drozsze za m2)\n"
    "- Pietro praktycznie nie koreluje z cena (0.04)"
)

pdf.add_page()
pdf.section_title("4.13 Struktura ofert wg pokoi i powierzchni per dzielnica")
pdf.add_plot(f"{PLOTS_DIR}/13_pokoje_dzielnice_stacked.png", "Rys. 13: Udzial procentowy wg pokoi w dzielnicach")
pdf.add_plot(f"{PLOTS_DIR}/14_powierzchnia_dzielnice.png", "Rys. 14: Udzial procentowy wg powierzchni w dzielnicach")

pdf.add_page()
pdf.section_title("4.14 Kalkulator cen wynajmu")
pdf.add_plot(f"{PLOTS_DIR}/15_kalkulator_cen.png", "Rys. 15: Mediana ceny wynajmu - dzielnica x pokoje")
pdf.body_text(
    "Heatmapa pozwala szybko sprawdzic ile powinien kosztowac wynajem konkretnego mieszkania. "
    "Przyklad: 2-pokojowe mieszkanie na Krzykach -> mediana 2800 zl, na Starym Miescie -> 3000 zl. "
    "Jesli ktos oferuje znacznie powyzej mediany - warto szukac dalej. "
    "Jesli ponizej - to moze byc okazja."
)

# ============================================================
# 5. PODSUMOWANIE
# ============================================================
pdf.add_page()
pdf.chapter_title("5. Podsumowanie i wnioski")
pdf.body_text(
    f"Na podstawie analizy {len(df)} ofert wynajmu mieszkan we Wroclawiu z serwisu Otodom.pl "
    "mozna wyciagnac nastepujace wnioski:"
)
pdf.bullet(f"Mediana ceny wynajmu we Wroclawiu to {med_price:.0f} zl/miesiac za mieszkanie o powierzchni {med_area:.0f} m2.")
pdf.bullet("Zdecydowana wiekszosc ofert (56%) to mieszkania 2-pokojowe - sa one najpopularniejsze na rynku wynajmu.")
pdf.bullet("Najdrozsze dzielnice to Srodmiescie i Stare Miasto (70 zl/m2), najtansze Psie Pole (62 zl/m2).")
pdf.bullet("Powierzchnia jest najwazniejszym czynnikiem wplywajacym na cene (korelacja 0.79).")
pdf.bullet("Pietro praktycznie nie wplywa na cene wynajmu (korelacja 0.04).")
pdf.bullet("Mniejsze mieszkania sa proporcjonalnie drozsze (wyzsza cena za m2) ze wzgledu na wiekszy popyt.")
pdf.bullet("Najwiecej ofert jest na Krzykach (592) - dzielnica z duza liczba nowych inwestycji.")
pdf.ln(5)

pdf.section_title("Technologie")
pdf.body_text(
    "- Jezyk: Python 3.13\n"
    "- Web scraping: requests, BeautifulSoup4\n"
    "- Przetwarzanie danych: pandas, numpy\n"
    "- Wizualizacja: matplotlib, seaborn\n"
    "- Statystyki: scipy\n"
    "- Raport PDF: fpdf2"
)

pdf.section_title("Struktura projektu")
pdf.body_text(
    "- scraper.py - skrypt pobierajacy dane z Otodom.pl\n"
    "- options.json - konfiguracja scrapera\n"
    "- analysis.py - czyszczenie danych i analiza eksploracyjna\n"
    "- generate_report.py - generowanie raportu PDF\n"
    "- wynajem_wroclaw.csv - surowe dane\n"
    "- wynajem_wroclaw_clean.csv - oczyszczone dane\n"
    "- plots/ - 15 wykresow PNG\n"
    "- requirements.txt - zaleznosci Pythona\n"
    "- README.md - dokumentacja projektu"
)

# Zapis
output_path = "Opis_projektu_BigData.pdf"
pdf.output(output_path)
print(f"Raport PDF wygenerowany: {output_path}")
