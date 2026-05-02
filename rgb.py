import numpy as np
from PIL import Image
import math
import os

class AdaptiveRGBSteganography:
    def __init__(self, block_size=8, n_pixels_per_block=16):
        self.block_size = block_size
        # Upewniamy się, że nie próbujemy zmienić więcej pikseli niż jest w bloku
        self.n_pixels = min(n_pixels_per_block, block_size * block_size)

    def _data_to_binary(self, data):
        """Konwertuje ciąg znaków (lub bajty) na listę bitów."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return ''.join(format(byte, '08b') for byte in data)

    def _binary_to_data(self, binary_data, return_as_string=True):
        """Konwertuje ciąg bitów na dane. Domyślnie zwraca tekst (UTF-8), opcjonalnie surowe bajty."""
        all_bytes =[int(binary_data[i: i+8], 2) for i in range(0, len(binary_data), 8) if len(binary_data[i:i+8]) == 8]
        byte_data = bytes(all_bytes)
        
        if return_as_string:
            try:
                return byte_data.decode('utf-8')
            except UnicodeDecodeError:
                # Jeśli to był plik binarny (np. .exe, .pdf, .zip), dekodowanie do tekstu się nie uda
                # Zwracamy więc surowe bajty
                return byte_data
        return byte_data

    def _calculate_brightness_variance(self, block):
        """
        Oblicza wariancję jasności bloku.
        KLUCZOWE: Maska (B & 254) gwarantuje, że osadzenie bitów wiadomości w kanale B 
        nie wpłynie na zmianę wariancji podczas dekodowania!
        """
        r = block[:, :, 0].astype(np.float32)
        g = block[:, :, 1].astype(np.float32)
        b = (block[:, :, 2] & 254).astype(np.float32)
        
        # Obliczenie jasności ze standardowymi wagami RGB -> Luminance
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return np.var(luminance)

    def _get_valid_blocks(self, img_array):
        """Dzieli obraz na bloki 8x8 i zwraca współrzędne tych, których wariancja >= mediana."""
        h, w, _ = img_array.shape
        blocks_y = h // self.block_size
        blocks_x = w // self.block_size
        
        variances =[]
        block_coords =[]
        
        # Krok 4 i 5 z zadania: Oblicz wariancję jasności
        for by in range(blocks_y):
            for bx in range(blocks_x):
                y_start = by * self.block_size
                x_start = bx * self.block_size
                
                block = img_array[y_start:y_start+self.block_size, x_start:x_start+self.block_size]
                var = self._calculate_brightness_variance(block)
                variances.append(var)
                block_coords.append((by, bx))
                
        # Krok 6 i 7 z zadania: Wyznacz próg jako medianę i wybierz bloki
        median_var = np.median(variances)
        
        valid_blocks =[
            block_coords[i] for i in range(len(variances))
            if variances[i] >= median_var
        ]
        return valid_blocks

    def get_capacity_bytes(self, image_path):
        """Zwraca maksymalną pojemność informacyjną obrazu w bajtach."""
        image = Image.open(image_path).convert('RGB')
        img_array = np.array(image, dtype=np.uint8)
        valid_blocks = self._get_valid_blocks(img_array)
        total_bits = len(valid_blocks) * self.n_pixels
        # Odejmujemy 32 bity na nagłówek i dzielimy na 8 (bajty)
        return (total_bits - 32) // 8

    def calculate_psnr(self, original_img_path, stego_img_path):
        """Oblicza PSNR na podstawie błędu średniokwadratowego (MSE)."""
        img1 = np.array(Image.open(original_img_path).convert('RGB'), dtype=np.float64)
        img2 = np.array(Image.open(stego_img_path).convert('RGB'), dtype=np.float64)
        
        mse = np.mean((img1 - img2) ** 2)
        if mse == 0:
            return float('inf')
        psnr = 20 * math.log10(255.0 / math.sqrt(mse))
        return psnr

    def encode(self, image_path, secret_message, output_path):
        """Koduje wiadomość z wykorzystaniem steganografii adaptacyjnej."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Nie znaleziono pliku wejściowego: {image_path}")

        image = Image.open(image_path).convert('RGB')
        img_array = np.array(image, dtype=np.uint8)
        
        binary_msg = self._data_to_binary(secret_message)
        msg_length = len(binary_msg)
        
        # 32-bitowa informacja o długości
        header_bits = format(msg_length, '032b')
        payload = header_bits + binary_msg
        payload_length = len(payload)
        
        valid_blocks = self._get_valid_blocks(img_array)
        
        # Walidacja pojemności obrazu
        capacity = len(valid_blocks) * self.n_pixels
        if payload_length > capacity:
            raise ValueError(f"Brak pojemności! Wymagane {payload_length} bitów, pojemność to {capacity} bitów.")

        payload_idx = 0
        
        for (by, bx) in valid_blocks:
            if payload_idx >= payload_length:
                break
                
            y_start = by * self.block_size
            x_start = bx * self.block_size
            
            for i in range(self.n_pixels):
                if payload_idx >= payload_length:
                    break
                    
                py = y_start + (i // self.block_size)
                px = x_start + (i % self.block_size)
                
                bit = int(payload[payload_idx])
                img_array[py, px, 2] = (img_array[py, px, 2] & 254) | bit
                payload_idx += 1

        stego_image = Image.fromarray(img_array)
        stego_image.save(output_path, format="PNG")

    def decode(self, stego_image_path):
        """Dekoduje wiadomość ze steganogramu wyznaczając uprzednio zmodyfikowane bloki."""
        if not os.path.exists(stego_image_path):
            raise FileNotFoundError(f"Nie odnaleziono pliku: {stego_image_path}")

        image = Image.open(stego_image_path).convert('RGB')
        img_array = np.array(image, dtype=np.uint8)
        
        valid_blocks = self._get_valid_blocks(img_array)
        
        extracted_bits = ""
        payload_idx = 0
        msg_length = 0
        
        for (by, bx) in valid_blocks:
            y_start = by * self.block_size
            x_start = bx * self.block_size
            
            for i in range(self.n_pixels):
                py = y_start + (i // self.block_size)
                px = x_start + (i % self.block_size)
                
                bit = img_array[py, px, 2] & 1
                extracted_bits += str(bit)
                payload_idx += 1
                
                if payload_idx == 32:
                    msg_length = int(extracted_bits, 2)
                    extracted_bits = ""
                    
                elif payload_idx == 32 + msg_length:
                    return self._binary_to_data(extracted_bits)
                    
        return self._binary_to_data(extracted_bits)


# --- AUTOMATYZACJA PRZYPADKÓW TESTOWYCH ---
if __name__ == "__main__":
    test_dir = "test_images"
    if not os.path.exists(test_dir):
        print(f"[!] Nie znaleziono folderu '{test_dir}'. Uruchom najpierw skrypt generatora obrazów!")
        exit()

    stego = AdaptiveRGBSteganography(block_size=8, n_pixels_per_block=16)

    print("\n" + "="*50)
    print(" PRZYPADEK TESTOWY 1: Poprawność ukrywania i odczytu")
    print("="*50)
    try:
        cover_img = os.path.join(test_dir, "test1_base_512.png")
        stego_img = os.path.join(test_dir, "stego_test1_base.png")
        msg = "Steganografia RGB"
        
        print(f"[*] Plik nośnika: {cover_img}")
        print(f"[*] Ukrywana wiadomość: '{msg}'")
        
        stego.encode(cover_img, msg, stego_img)
        extracted = stego.decode(stego_img)
        
        print(f"[+] Odczytana wiadomość: '{extracted}'")
        if msg == extracted:
            print("[SUKCES] Kryterium spełnione: Bezbłędne odczytanie oryginalnej wiadomości.")
        else:
            print("[BŁĄD] Wiadomości nie są identyczne!")
    except Exception as e:
        print(f"[!] Błąd w Teście 1: {e}")


    print("\n" + "="*50)
    print(" PRZYPADEK TESTOWY 2: Pojemność i jakość (1024x1024)")
    print("="*50)
    try:
        cover_img = os.path.join(test_dir, "test2_capacity_1024.png")
        stego_img = os.path.join(test_dir, "stego_test2_capacity.png")
        
        # Obliczanie maksymalnej pojemności obrazu
        max_bytes = stego.get_capacity_bytes(cover_img)
        print(f"[*] Obliczona maksymalna pojemność obrazu: {max_bytes} znaków (bajtów).")
        
        # Generowanie wiadomości zapychającej obraz "pod kurek"
        max_msg = "X" * max_bytes
        
        stego.encode(cover_img, max_msg, stego_img)
        extracted = stego.decode(stego_img)
        psnr = stego.calculate_psnr(cover_img, stego_img)
        
        print(f"[+] Jakość obrazu (PSNR): {psnr:.2f} dB")
        if psnr > 40 and max_msg == extracted:
            print("[SUKCES] Kryterium spełnione: PSNR > 40 dB, wiadomość odczytana poprawnie (maksymalna waga).")
        else:
            print("[BŁĄD] Kryterium niespełnione.")
    except Exception as e:
        print(f"[!] Błąd w Teście 2: {e}")


    print("\n" + "="*50)
    print(" PRZYPADEK TESTOWY 3: Adaptacyjność")
    print("="*50)
    try:
        msg = "Ukryta wiadomosc testujaca adaptacyjnosc " * 50
        test_images =[
            ("Gładki", "test3_smooth_512.png"),
            ("Ostre Krawędzie", "test3_sharp_512.png"),
            ("Teksturowany", "test3_textured_512.png")
        ]
        
        for img_type, img_name in test_images:
            cover_img = os.path.join(test_dir, img_name)
            stego_img = os.path.join(test_dir, f"stego_{img_name}")
            
            stego.encode(cover_img, msg, stego_img)
            psnr = stego.calculate_psnr(cover_img, stego_img)
            extracted = stego.decode(stego_img)
            
            print(f"--- Obraz: {img_type} ---")
            print(f"    PSNR: {psnr:.2f} dB")
            print(f"    Dekodowanie: {'Sukces' if msg == extracted else 'Błąd'}")
        
        print("\n[SUKCES] Kryterium spełnione: PSNR dla każdego środowiska > 40 dB.")
    except Exception as e:
        print(f"[!] Błąd w Teście 3: {e}")