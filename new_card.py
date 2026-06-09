from smartcard.System import readers
from smartcard.util import toHexString

r = readers()
if len(r) == 0:
    print("No se detecta el lector.")
    exit()

reader = r[0]
connection = reader.createConnection()
connection.connect()

print(f"Lector listo: {reader}")

# 1. Intentar inicializar la tarjeta en el lector (igual que hicimos con la otra)
init_apdu = [0xFF, 0xA4, 0x00, 0x00, 0x01, 0x06]
resp, sw1, sw2 = connection.transmit(init_apdu)
print(f"Inicialización del chip: SW1={hex(sw1)} SW2={hex(sw2)}")

# 2. Verificar si el PSC (PIN de escritura) de fábrica está activo (generalmente FF FF FF)
# Estructura comando ACS: FF 20 00 00 03 [PIN_1] [PIN_2] [PIN_3]
psc_factory = [0xFF, 0x20, 0x00, 0x00, 0x03, 0xFF, 0xFF, 0xFF]
resp_psc, sw1_psc, sw2_psc = connection.transmit(psc_factory)

if sw1_psc == 0x90 and sw2_psc == 0x00:
    print("Resultado: El chip está desbloqueado con el PSC por defecto de fábrica (FF FF FF).")
    print("Estado: LISTA PARA PRODUCCIÓN. El software de gestión de tu empresa podrá inicializarla.")
elif sw1_psc == 0x63:
    print(f"Resultado: Código incorrecto. Intentos restantes: {sw2_psc & 0x0F}")
else:
    print(f"Resultado de seguridad inesperado: SW1={hex(sw1_psc)} SW2={hex(sw2_psc)}")

connection.disconnect()
