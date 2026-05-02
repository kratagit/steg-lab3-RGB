import os
from PIL import Image

def create_horizontal_collage(image_paths, output_path, padding=15):
    """
    Łączy listę obrazów w jeden poziomy plik z zachowaniem estetycznych odstępów.
    """
    # Sprawdzenie, czy wszystkie pliki istnieją
    valid_paths =[p for p in image_paths if os.path.exists(p)]
    if not valid_paths:
        print(f"[!] Nie znaleziono plików dla: {output_path}. Upewnij się, że testy zostały wykonane.")
        return
        
    images = [Image.open(p) for p in valid_paths]
    
    # Obliczanie wymiarów nowego obrazu
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths) + padding * (len(images) - 1)
    max_height = max(heights)
    
    # Tworzenie nowego, białego tła
    new_img = Image.new('RGB', (total_width, max_height), color='white')
    
    # Wklejanie obrazów jeden po drugim
    x_offset = 0
    for img in images:
        new_img.paste(img, (x_offset, 0))
        x_offset += img.width + padding
        
    new_img.save(output_path)
    print(f"[+] Wygenerowano gotowy obraz do sprawozdania: {output_path}")

if __name__ == "__main__":
    TEST_DIR = "test_images"
    
    print("=== GENERATOR ZESTAWIEŃ DO SPRAWOZDANIA ===")

    # ---------------------------------------------------------
    # RYSUNEK 1: Porównanie nośnika oryginalnego i steganogramu
    # ---------------------------------------------------------
    test1_files =[
        os.path.join(TEST_DIR, "test1_base_512.png"),
        os.path.join(TEST_DIR, "stego_test1_base.png")
    ]
    create_horizontal_collage(test1_files, os.path.join(TEST_DIR, "raport_rys1.png"))

    # ---------------------------------------------------------
    # RYSUNEK 3: Zestawienie trzech środowisk z testu adaptacyjności
    # ---------------------------------------------------------
    test3_files =[
        os.path.join(TEST_DIR, "test3_smooth_512.png"),
        os.path.join(TEST_DIR, "test3_sharp_512.png"),
        os.path.join(TEST_DIR, "test3_textured_512.png")
    ]
    create_horizontal_collage(test3_files, os.path.join(TEST_DIR, "raport_rys3.png"))

    print("\nGotowe! Pliki 'raport_rys1.png' i 'raport_rys3.png' czekają w folderze test_images.")