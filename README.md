# steg-lab3-RGB

# Laboratorium 3

### Cel zadania
Implementacja adaptacyjnej steganografii RGB w obrazach PNG z wykorzystaniem bloków 8×8.

Celem zadania jest implementacja programu, który ukrywa i odczytuje wiadomość tekstową lub plik binarny w obrazie PNG. Program ma wykorzystywać prosty, deterministyczny wariant adaptacyjnego osadzania danych w przestrzeni RGB.

## Wymagania funkcjonalne
Program powinien:
- Wczytywać obraz PNG jako nośnik informacji (tryb RGB).
- Wczytywać wiadomość tekstową **lub** plik binarny do ukrycia w obrazie.
- Ukrywać dane w obrazie z wykorzystaniem adaptacyjnego wyboru bloków.
- Zapisywać obraz wynikowy (stego-obraz) w formacie PNG.
- Odczytywać ukrytą wiadomość z obrazu PNG.
- Automatycznie zapisywać długość wiadomości w obrazie (bez potrzeby podawania jej przy dekodowaniu).
- Sprawdzać, czy obraz ma wystarczającą pojemność na ukrycie danych.
- Umożliwiać powtarzalność wyników (opcjonalnie: parametr `seed` dla losowości).

## Implementacja
Program powinien być zaimplementowany w języku Python (lub MATLAB), wykorzystując bibliotekę `PIL` / `Pillow` do przetwarzania obrazów.

### Algorytm steganograficzny z adaptacyjnym progowaniem
1. Wczytaj obraz PNG i przekonwertuj do przestrzeni RGB.
2. Wczytaj wiadomość i zamień ją na ciąg bitów.
3. Dodaj na początku 32-bitową informację o długości wiadomości.
4. Podziel obraz na bloki 8×8 pikseli.
5. Dla każdego bloku oblicz wariancję jasności.
6. Wyznacz próg jako medianę wariancji wszystkich bloków.
7. Wybierz bloki, dla których `wariancja ≥ próg`.
8. Dla każdego wybranego bloku wybierz maksymalnie `N` pikseli (np. 16).
9. W każdym wybranym pikselu zakoduj bit wiadomości w LSB kanału B:
   `B = (B & 254) | bit`
10. Zapisz zmodyfikowany obraz jako PNG.
11. Przy odczycie wykonaj te same kroki selekcji bloków.
12. Odczytaj bity z LSB kanału B.
13. Pierwsze 32 bity interpretuj jako długość wiadomości.
14. Odtwórz wiadomość z kolejnych bitów.

## Przypadki testowe

### 1. Test poprawności ukrywania i odczytywania
- Ukryj krótką wiadomość tekstową (np. `"Steganografia RGB"`) w obrazie PNG o rozmiarze 512×512 pikseli.
- Odczytaj ukrytą wiadomość z zmodyfikowanego obrazu.
- **Kryterium sukcesu:** Bezbłędne odczytanie oryginalnej wiadomości.

### 2. Test pojemności i jakości
- Ukryj maksymalną możliwą ilość danych w obrazie 1024×1024 pikseli.
- Zmierz PSNR między oryginalnym a zmodyfikowanym obrazem.
- Odczytaj ukrytą wiadomość i porównaj z oryginalną.
- **Kryterium sukcesu:** `PSNR > 40 dB`, bezbłędne odczytanie wiadomości.

### 3. Test adaptacyjności
- Przygotuj zestaw obrazów o różnej charakterystyce (gładkie, teksturowane, z ostrymi krawędziami).
- Ukryj tę samą wiadomość w każdym z obrazów.
- Porównaj PSNR i widoczność zmian dla różnych typów obrazów.
- **Kryterium sukcesu:** Mniejsze zniekształcenia w obszarach teksturowanych, `PSNR > 40 dB` dla wszystkich typów obrazów.