from smartcard.System import readers
from smartcard.util import toHexString

# 1. Detectar el lector ACR39
r = readers()
if len(r) == 0:
    print("No se detecta ningún lector.")
    exit()

reader = r[0]
print(f"Usando lector: {reader}")
connection = reader.createConnection()
connection.connect()

print("\n--- INICIALIZANDO MODO SÍNCRONO EN LECTOR ---")
# Comando ACS para configurar el lector en modo tarjeta de memoria síncrona estándar
init_apdu = [0xFF, 0xA4, 0x00, 0x00, 0x01, 0x06]
resp_init, sw1_init, sw2_init = connection.transmit(init_apdu)
print(f"Respuesta inicialización: SW1={hex(sw1_init)} SW2={hex(sw2_init)}")

print("\n--- NUEVO VOLCADO DE MEMORIA ---")

bytes_per_block = 16
total_memory_size = 256

for offset in range(0, total_memory_size, bytes_per_block):
    # Intentamos la lectura con el lector ya configurado en el modo correcto
    apdu = [0xFF, 0xB0, 0x00, offset, bytes_per_block]
    
    response, sw1, sw2 = connection.transmit(apdu)
    
    if sw1 == 0x90 and sw2 == 0x00:
        hex_data = toHexString(response)
        print(f"ADDR {offset:03d} (0x{offset:02X}): {hex_data}")
    else:
        # Si da error, probamos con la instrucción alternativa de lectura de datos (0x01)
        # que usan algunos firmwares de ACS antiguos para saltarse la cabecera fija
        alt_apdu = [0x00, 0xB0, 0x00, offset, bytes_per_block]
        response, sw1, sw2 = connection.transmit(alt_apdu)
        if sw1 == 0x90 and sw2 == 0x00:
            print(f"ADDR {offset:03d} (0x{offset:02X}) [ALT]: {toHexString(response)}")
        else:
            print(f"Error en ADDR {offset}: SW1={hex(sw1)} SW2={hex(sw2)}")

connection.disconnect()
