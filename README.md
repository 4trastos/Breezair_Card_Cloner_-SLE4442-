# 🃏 Clonador de Tarjetas Breezair (SLE4442)

Herramientas para leer y clonar las tarjetas de memoria de equipos **Australair / Breezair** usando un lector **ACS ACR39U** en macOS.

> Desarrollado en Australair España para reemplazar tarjetas descatalogadas de configuración de máquina.

---

## 🔧 Requisitos

- Python 3.x
- Lector ACS ACR39U
- Librería `pyscard`

```bash
pip install pyscard
```

---

## 📁 Scripts

| Script | Descripción |
|---|---|
| `read_memory.py` | Lee los 256 bytes de una tarjeta y muestra el volcado completo |
| `generate_structure.py` | Genera el archivo `estructura_maquina.bin` con los datos de la original |
| `write_card.py` | Escribe el `.bin` en una tarjeta nueva en blanco |
| `new_card.py` | Diagnóstico: comprueba si una tarjeta nueva está desbloqueada |

---

## 🔄 Proceso de clonado

### Paso 1 — Verificar la tarjeta original
Pon la tarjeta **original** en el lector:
```bash
python3 read_memory.py
```
Comprueba que los datos de ADDR 032, 048 y 064 son correctos.

### Paso 2 — Generar el archivo de datos
Sin tarjeta (o con cualquiera):
```bash
python3 generate_structure.py
```
Genera `estructura_maquina.bin` con los datos a escribir.

### Paso 3 — Escribir en la tarjeta nueva
Pon la tarjeta **nueva en blanco** en el lector:
```bash
python3 write_card.py
```
Cada byte escrito correctamente aparece con ✅.

### Paso 4 — Verificar el clon
Con la tarjeta **nueva** aún en el lector:
```bash
python3 read_memory.py
```
Compara el volcado con el de la original. Deben ser idénticos.

---

## 📊 Estructura de memoria (SLE4442, 256 bytes)

```
ADDR 000  A2 13 10 91 FF FF 81 15 ...  → Cabecera del chip
ADDR 016  FF FF FF FF FF D2 76 00 ...  → Identificador de aplicación (AID)
ADDR 032  00 00 00 00 00 03 01 00 ...  → Configuración de máquina  ← HAY QUE COPIAR
ADDR 048  00 00 00 00 01 2C 01 54 ...  → Offsets de firmware        ← HAY QUE COPIAR
ADDR 064  02 12 02 26 02 44 02 58 ...  → Registros de control       ← HAY QUE COPIAR
ADDR 080  FF FF FF FF FF FF FF FF ...  → Memoria vacía (no se toca)
```

---

## ⚠️ Notas importantes

- El comando de escritura correcto para el ACR39U en macOS es `FF D0` (no `FF D6`)
- El PSC (PIN de escritura) de fábrica es `FF FF FF`. Una respuesta `SW2=0x07` significa **desbloqueada y lista** — no es un error
- Los bytes `0xFF` no se escriben (ya están de fábrica), lo que acelera el proceso
- Esperar a que la máquina confirme el funcionamiento antes de clonar las siguientes unidades

---

## 🏢 Contexto

Las tarjetas originales están descatalogadas. Este proceso permite replicarlas a partir de una unidad funcional usando tarjetas SLE4442 vírgenes compatibles.
