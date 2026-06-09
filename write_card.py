from smartcard.System import readers
import os
import time

archivo_bin = "estructura_maquina.bin"
if not os.path.exists(archivo_bin):
    print(f"Error: No se encuentra el archivo {archivo_bin}")
    exit()

with open(archivo_bin, "rb") as f:
    datos_a_escribir = list(f.read())

r = readers()
if len(r) == 0:
    print("No se detecta el lector.")
    exit()

connection = r[0].createConnection()
connection.connect()
print(f"Conectado a: {r[0]}")

init_apdu = [0xFF, 0xA4, 0x00, 0x00, 0x01, 0x06]
resp, sw1, sw2 = connection.transmit(init_apdu)
print(f"Inicialización: SW1={hex(sw1)} SW2={hex(sw2)}")

print("Desbloqueando escritura (PSC)...")
psc_apdu = [0xFF, 0x20, 0x00, 0x00, 0x03, 0xFF, 0xFF, 0xFF]
resp, sw1, sw2 = connection.transmit(psc_apdu)
print(f"PSC: SW1={hex(sw1)} SW2={hex(sw2)}")

print("\n--- ESCRIBIENDO ---")

errores = 0
for offset in range(0, 256):
    un_byte = datos_a_escribir[offset]

    if un_byte == 0xFF:
        continue

    write_apdu = [0xFF, 0xD0, 0x00, offset, 0x01, un_byte]

    try:
        resp, sw1, sw2 = connection.transmit(write_apdu)
        if sw1 == 0x90 and sw2 == 0x00:
            print(f"ADDR {offset:03d} (0x{offset:02X}) -> 0x{un_byte:02X} ✅")
        else:
            print(f"FALLO en ADDR {offset}: SW1={hex(sw1)} SW2={hex(sw2)}")
            errores += 1
            if errores > 3:
                print("Demasiados errores, abortando.")
                break

        time.sleep(0.05)

    except Exception as e:
        print(f"Excepción en byte {offset}: {e}")
        errores += 1
        if errores > 3:
            break

connection.disconnect()
print(f"\nProceso finalizado. Errores: {errores}")
