"""Script para detectar as posições das rodas nos sprites dos carros."""
import pygame
pygame.init()
screen = pygame.display.set_mode((1, 1))

cars = [
    ("Skyline", "assets/images/car/Skyline/Skyline.png"),
    ("Dodge", "assets/images/car/Dodge/Dodge.png"),
    ("F40", "assets/images/car/F40/F40.png"),
]

for name, path in cars:
    img = pygame.image.load(path).convert_alpha()
    w, h = img.get_size()
    print(f"\n=== {name} ({w}x{h}) ===")
    
    # Encontra a área não-transparente (bounding box do conteúdo real)
    min_y = h
    max_y = 0
    min_x = w
    max_x = 0
    for y in range(h):
        for x in range(w):
            if img.get_at((x, y))[3] > 0:
                min_y = min(min_y, y)
                max_y = max(max_y, y)
                min_x = min(min_x, x)
                max_x = max(max_x, x)
    
    print(f"  Content bounds: x=[{min_x},{max_x}] y=[{min_y},{max_y}]")
    print(f"  Content size: {max_x-min_x+1}x{max_y-min_y+1}")
    
    # Procura as áreas transparentes na metade inferior (wheel wells)
    # Busca colunas com transparência dentro da área de conteúdo
    mid_y = (min_y + max_y) // 2
    bottom_y = max_y
    
    # Para cada coluna no range de conteúdo, verifica se há transparência na parte inferior
    wheel_cols = []
    for x in range(min_x, max_x + 1):
        has_content_above = False
        has_transparency_below = False
        for y in range(mid_y, bottom_y + 1):
            a = img.get_at((x, y))[3]
            if a > 0:
                has_content_above = True
            elif has_content_above and a == 0:
                has_transparency_below = True
                break
        if has_transparency_below:
            wheel_cols.append(x)
    
    # Agrupa colunas consecutivas para encontrar os wheel wells
    if wheel_cols:
        groups = []
        start = wheel_cols[0]
        prev = wheel_cols[0]
        for x in wheel_cols[1:]:
            if x - prev > 3:  # Gap > 3px = novo grupo
                groups.append((start, prev))
                start = x
            prev = x
        groups.append((start, prev))
        
        for i, (gstart, gend) in enumerate(groups):
            gw = gend - gstart + 1
            # Encontra o range Y da transparência nessa área
            gy_min = h
            gy_max = 0
            for x in range(gstart, gend + 1):
                for y in range(mid_y, bottom_y + 1):
                    if img.get_at((x, y))[3] == 0:
                        gy_min = min(gy_min, y)
                        gy_max = max(gy_max, y)
            
            cx = (gstart + gend) // 2
            cy = (gy_min + gy_max) // 2
            print(f"  Wheel well {i+1}: x=[{gstart},{gend}] y=[{gy_min},{gy_max}] " +
                  f"size={gw}x{gy_max-gy_min+1} center=({cx},{cy})")
            print(f"    From left: {gstart}px, from right: {w - gend - 1}px")
            print(f"    From top: {gy_min}px, from bottom: {h - gy_max - 1}px")

pygame.quit()
