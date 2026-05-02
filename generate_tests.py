import numpy as np
from PIL import Image
import os

def create_smooth_image(filename, size=(512, 512)):
    """
    Generuje gładki obraz (2D gradient).
    Brak ostrych krawędzi, mała wariancja w blokach.
    Idealny do testowania widoczności zniekształceń.
    """
    width, height = size
    x = np.linspace(0, 255, width)
    y = np.linspace(0, 255, height)
    xv, yv = np.meshgrid(x, y)
    
    r = xv  # Gradient poziomy dla czerwonego
    g = yv  # Gradient pionowy dla zielonego
    b = np.full_like(xv, 150) # Stała wartość dla niebieskiego, gdzie ładujemy dane
    
    img_array = np.dstack((r, g, b)).astype(np.uint8)
    Image.fromarray(img_array).save(filename, format="PNG")
    print(f"[+] Wygenerowano: {filename} (Gładki, {width}x{height})")


def create_sharp_edges_image(filename, size=(512, 512)):
    """
    Generuje obraz z ostrymi krawędziami (szachownica).
    Bardzo duża wariancja na granicach kwadratów, zerowa w środku.
    """
    width, height = size
    block_size = 64
    
    # Wektoryzowane generowanie szachownicy dla wydajności
    y, x = np.indices((height, width))
    checkerboard = ((x // block_size) + (y // block_size)) % 2
    
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Czerwone i ciemnoniebieskie kwadraty
    img_array[checkerboard == 0] = [220, 50, 50]
    img_array[checkerboard == 1] = [20, 20, 180]
        
    Image.fromarray(img_array).save(filename, format="PNG")
    print(f"[+] Wygenerowano: {filename} (Ostre krawędzie, {width}x{height})")


def create_textured_image(filename, size=(512, 512)):
    """
    Generuje obraz teksturowany z wykorzystaniem fal trygonometrycznych.
    Wysoka, ale naturalna wariancja w całym obrazie.
    Tutaj algorytm adaptacyjny ukryje dane najlepiej.
    """
    width, height = size
    y, x = np.indices((height, width))
    
    # Tworzenie pofalowanej "tekstury" (np. przypominającej materiał)
    z = np.sin(x * 0.1) + np.cos(y * 0.1) + np.sin((x + y) * 0.05)
    
    # Normalizacja do zakresu 0-255
    z_norm = ((z - z.min()) / (z.max() - z.min()) * 255)
    
    r = (z_norm * 0.8).astype(np.uint8)
    g = (z_norm * 0.6).astype(np.uint8)
    b = z_norm.astype(np.uint8)
    
    img_array = np.dstack((r, g, b))
    Image.fromarray(img_array).save(filename, format="PNG")
    print(f"[+] Wygenerowano: {filename} (Teksturowany, {width}x{height})")


if __name__ == "__main__":
    print("=== GENERATOR OBRAZÓW TESTOWYCH DO LABORATORIUM ===")
    
    output_dir = "test_images"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # --- PRZYPADEK TESTOWY 1 --- (512x512)
    # Zwykły obrazek do podstawowych testów działania
    create_smooth_image(os.path.join(output_dir, "test1_base_512.png"), size=(512, 512))
    
    # --- PRZYPADEK TESTOWY 2 --- (1024x1024)
    # Wielki obraz do testu pojemności i jakości
    create_textured_image(os.path.join(output_dir, "test2_capacity_1024.png"), size=(1024, 1024))
    
    # --- PRZYPADEK TESTOWY 3 --- (Trzy różne typy, 512x512)
    # Obrazy do porównania adaptacyjności (PSNR i widoczności zmian)
    create_smooth_image(os.path.join(output_dir, "test3_smooth_512.png"), size=(512, 512))
    create_sharp_edges_image(os.path.join(output_dir, "test3_sharp_512.png"), size=(512, 512))
    create_textured_image(os.path.join(output_dir, "test3_textured_512.png"), size=(512, 512))
    
    print(f"\n[+] Sukces! Wszystkie pliki zostały wygenerowane w folderze '{output_dir}'.")