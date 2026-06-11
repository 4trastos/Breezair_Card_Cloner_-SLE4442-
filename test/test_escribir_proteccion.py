from smartcard.System import readers
import time

r = readers()
connection = r[0].createConnection()
connection.connect()

init_apdu = [0xFF, 0xA4, 0x00, 0x00, 0x01, 0x06]
connection.transmit(init_apdu)

# PSC
psc_apdu = [0xFF, 0x20, 0x00, 0x00, 0x03, 0xFF, 0xFF, 0xFF]
resp, sw1, sw2 = connection.transmit(psc_apdu)
print(f"PSC: SW1={hex(sw1)} SW2={hex(sw2)}")

# Escribir protección con FF D1 (comando estándar SLE4442)
print("\n--- ESCRIBIENDO PROTECCIÓN ---")
protection = [0x30, 0xFF, 0x1F, 0xF8]

for i, byte in enumerate(protection):
    if byte == 0xFF:
        print(f"Byte {i} -> 0xFF, saltando")
        continue
    apdu = [0xFF, 0xD1, 0x00, i, 0x01, byte]
    resp, sw1, sw2 = connection.transmit(apdu)
    print(f"Byte {i} -> 0x{byte:02X}: SW1={hex(sw1)} SW2={hex(sw2)}")
    time.sleep(0.05)

# Verificar
print("\n--- VERIFICANDO ---")
prot_apdu = [0xFF, 0xB4, 0x00, 0x00, 0x04]
resp, sw1, sw2 = connection.transmit(prot_apdu)
print(f"Protección: {[hex(b) for b in resp]}")

if resp == [0x30, 0xFF, 0x1F, 0xF8]:
    print("✅ PROTECCIÓN ESCRITA CORRECTAMENTE")
else:
    print("❌ No se escribió correctamente")

connection.disconnect()
