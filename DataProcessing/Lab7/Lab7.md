# Zadania Lista 7

**Uwagi ogólne**

1. Z powodu, że przyszłe zajęcia będą skrócone, może braknąć czasu na indywidualną prezentację rozwiązań. 
   Proszę więc przyłożyć się do tworzenia zrzutów ekranu.  

## (5 pkt) 1. Zbuduj frontend aplikacji

Zdobądź dane do autoryzacji poprzez rejestrację [link](https://praw.readthedocs.io/en/stable/getting_started/authentication.html).

W zadaniu należy wykorzystać model do analizy emocji z platformy HuggingFace [link](https://huggingface.co/bhadresh-savani/albert-base-v2-emotion).

Wykorzystując bibliotekę [praw](https://github.com/praw-dev/praw) oraz Streamlit napisz skrypt, który pobiera dane z wybranego subreddita 
i dokonuje na nich analizy sentymentu. Aplikacja ma posiadać następujące funkcjonalności:
* możliwość podania nazwy subreddita profilu do zescrapowania 
* użycie metody cache'ującej wyniki scrapowania, by zaoszczędzić transfer i czas
* wykres liczby postów w czasie
* wykres nacechowania emocjonalnego postów ogółem 
* wykres nacechowania emocjonalnego postów w czasie
* dwa dowolne inne wykresy przedstawiające inne statystyki
* progressbar pokazujący postęp analizy sentymentu

Stworzoną aplikację udokumentuj zrzutami ekranu.

## (2 pkt) 2. Zbuduj obraz Dockerowy aplikacji
* Na bazie kodu z pkt 1 stwórz obraz Dockera zawierający i uruchamiający aplikację, umożliwiający 
dostać się do niej z komputera hosta. 
Obraz ma mieć charakter produkcyjny, czyli:
* Obraz ma być minimalny, zawierać tylko niezbędne biblioteki i pliki. 
* Obraz ma być kompletny i nie wymagać podmontowania żadnych zewnętrznych plików.
* Obraz ma nie zawierać żadnych danych autoryzacyjnych, które są potrzebne do uruchomienia aplikacji. 
(Szczególnie jeśli wykonujesz dodatkowe zadanie nr 5!!!)

## (3 pkt) 3. Zbieraj statystyki produkcyjne

Używając Docker Compose, stwórz środowisko umożliwiajace zbieranie statystyk:
* złącz swoją aplikację z obrazami Graphite i Grafany w jedno środowisko dockerowe
* rozpocznij zbieranie trzech różnych statystyk z aplikacji. Przykładowe statystyki - ilość uruchomień, ilość użyć cache, czas pobierania danych, czas analizy sentymentu, ilość zebranych postów, wyniki sentymentu (jako timing), ilość błędów pobierania danych itp.
* stwórz dashboard w Grafanie zawierający wykresy stworzone na bazie zbieranych metryk

Stworzone wykresy udokumentuj zrzutami ekranu.

## (dodatkowe) 4. (0.5 pkt) Załóż alert na któryś z wykresów Grafany

## (dodatkowe) 5. (0.5 pkt) Opublikuj obraz utworzony w zad 2 na Docker Hub.
   
