# Assignment l05

Repozytorium zawiera notebooki zawierające zadanie na ten tydzień. Wykonaj polecenia w każdym notebooku (rozszerzenie .ipynb). Następnie zacommituj pracę i wypushuj na GitHuba. Prowadzący sprawdzi wykonane zadanie po jego terminie.


Wyniki zostaną opublikowane w plikach feedbacku `*.html`. Konieczne będzie pobranie zmian i otwarcie pliku w przeglądarce (GitHub nie renderuje plików HTML).

----

## Konfiguracja środowiska

W laboratorium wykorzystywane są zeszyty [Jupyter Notebook](https://jupyter.org/). Są to interaktywne dokumenty mogące zawierać kod oraz wyniki jego działania, wraz z dodatkową treścią, dodawaną przy użyciu języka [Markdown](https://www.markdownguide.org/). W zeszytach Jupyter Notebook można wykorzystywać wiele języków; na laboratorium wykorzystywany będzie język Python.
    
Przygotowanie środowiska polega na zainstalowaniu wymaganych paczek z dostarczonego pliku `requirements.txt`:

```console
pip install -r requirements.txt
```

Polecamy wykorzystanie [wirtualnych środowisk](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) w celu izolacji od systemowego interpretera Python (plik `requirements.txt` może się zmieniać na kolejnych laboratoriach).

Po zainstalowaniu paczek środowiska należy uruchomić serwer Jupyter poleceniem:

```console
jupyter notebook
```

Po uruchomieniu w przeglądarce otworzy się strona Jupyter, z której można wybrać plik zeszytu (o rozszerzeniu `*.ipynb`), aby go otworzyć. Jeżeli strona nie otworzyła się automatycznie, można wykorzystać link, który pojawi się w konsoli.