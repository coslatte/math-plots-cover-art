# Instrucciones de Uso — Generador de Arte Algorítmico

Esta aplicación genera arte algorítmico y matemático en una amplia variedad de estilos. Cada ejecución produce múltiples imágenes únicas de cada tipo.

## Estilos de Arte Disponibles
- **Fractales:** Imágenes con patrones matemáticos auto-similares.
- **Atractores:** Figuras basadas en atractores caóticos (ej. Clifford).
- **Patrones Binarios:** Matrices de color y patrones digitales.
- **Campos Tensoriales:** Líneas de flujo matemáticas.
- **Cuerpos 3D:** Proyecciones de esferas, toros y paraboloides.
- **Voronoi:** Polígonos de colores generados por diagramas de Voronoi.
- **Ruido Perlin:** Texturas orgánicas y suaves.
- **Curvas Bézier:** Composiciones de líneas curvas suaves y coloridas.
- **Mosaico Pixelado:** Arte abstracto tipo mosaico de píxeles grandes.

## ¿Cómo usar?
1. Ejecuta el archivo `main.py` con Python:
   ```bash
   python main.py
   ```
2. Se generará una carpeta en `output/` con subcarpetas para cada tipo de arte y 10 variaciones de cada uno.
3. Explora las imágenes generadas. Cada ejecución produce resultados diferentes.

## Personalización
- Puedes modificar la variable `IMG_COUNT` o `num_variants` en el código para cambiar la cantidad de imágenes.
- Modifica las paletas o agrega nuevos generadores para experimentar aún más.

## Requisitos
- Python 3.x
- Paquetes: numpy, matplotlib, pillow, scipy

Instala dependencias con:
```bash
pip install numpy matplotlib pillow scipy
```

---
¡Explora y disfruta la variedad de arte generado automáticamente!
