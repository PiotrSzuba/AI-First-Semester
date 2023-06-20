# Zadania Lista 1

1. Korzystając z języka Python i jedynie z wbudowanych paczek, wykonaj poniższe zadania:
    <br><br>
    a) (2 pkt) Napisz dowolny skrypt pod ścieżką `<KATALOG_GŁÓWNY_PROJEKTU>/scripts/main_1.py`.
    <br><br>
    b) (3 pkt) W pliku `<KATALOG_GŁÓWNY_PROJEKTU>/src/utils.py` zamieść dowolną funkcję/klasę, którą zaimportujesz i wykorzystasz w skrypcie `scripts/main_2.py`.
    <br><br>
    **Wymagania**

   - Skrypty należy uruchomić korzystając ze środowiska w kontenerze Docker, w przeciwnym razie przyznane będzie 0pkt. (To wymaganie zostanie z nami do końca kursu.)
   - Pisząc skrypty należy skorzystać z instrukcji `if`, `else`, `for`, `range`, `return`, ze struktur `list`, `set`, `dict`, `tuple`, `class`, `dataclass` oraz z *list comprehension*. Każda instrukcja musi wystąpić **co najmniej raz** w zad. a **lub** b.
   - Program nie musi być użyteczny, ale ma mieć jednoznaczny sens. 

---
2. Korzystając ze środowiska Docker:
    <br><br>
    a) (2pkt) zainstaluj paczkę `black` specyfikując na sztywno jej wersję w pliku `requirements.txt`. Sformatuj wszystkie pliki `.py` w projekcie. Zamieść 3 zrzuty ekranu pod ścieżką `screenshots`: dowolony plik przed formatowaniem, dowolony plik po formatowaniu oraz wyjście w terminalu po komendzie formatującej. 
    <br><br>
    b) (3pkt) uruchom Jupyter Notebook lub JupyterLab w kontenerze dockerowym. Następnie utwórz notebook pod ścieżką `<KATALOG_GŁÓWNY_PROJEKTU>/notebooks/notebook_1.ipynb`, w którym w komórce typu `Markdown` wyświetlisz swój numer indeksu, a w komórce typu `Code` zaimportujesz i użyjesz funkcji/klasy z `src/utils.py`.

---

**Uwagi**
- Przy wykonywaniu listy przyda się znajomość `PYTHONPATH` oraz umiejętność przekierowania portów ;)
