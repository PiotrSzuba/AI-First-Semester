[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/aLomsFim)
# Assignment l03

Repozytorium zawiera notebooki zawierające zadanie na ten tydzień. Wykonaj polecenia w każdym notebooku (rozszerzenie .ipynb). Następnie zacommituj pracę i wypushuj na GitHuba. Prowadzący sprawdzi wykonane zadanie po jego terminie.


Wyniki zostaną opublikowane w plikach feedbacku `*.html`. Konieczne będzie pobranie zmian i otwarcie pliku w przeglądarce (GitHub nie renderuje plików HTML).

----

## Konfiguracja środowiska
W laboratorium wykorzystywane są zeszyty [Jupyter Notebook](https://jupyter.org/). Są to interaktywne dokumenty mogące zawierać kod oraz wyniki jego działania, wraz z dodatkową treścią, dodawaną przy użyciu języka [Markdown](https://www.markdownguide.org/). W zeszytach Jupyter Notebook można wykorzystywać wiele języków; na laboratorium wykorzystywany będzie język Python.
W celu konfiguracji środowiska można użyć przygotowanego `Dockerfile` lub zainstalowac paczki we własnym środowisku.
### Docker
1. W pierwszej kolejności należy zbudować obraz:
```console
docker build --build-arg UID=$(id -u) --build-arg GID=$(id -g) -t urlab:latest .
```

2. Następnie należy uruchomić kontener z projektem zamontowanym jako `volume` oraz wystawionym odpowiednim portem:
```console
docker run --user "$(id -u):$(id -g)" --rm -p 8888:8888 -v $(pwd):/assignment urlab:latest ```
```

### Lokalne środowisko
Należy użyć języka **Python w wersji 3.10**.
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