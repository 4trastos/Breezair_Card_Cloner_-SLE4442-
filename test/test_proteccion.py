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

# Leer protección actual
prot_apdu = [0xFF, 0xB4, 0x00, 0x00, 0x04]
resp, sw1, sw2 = connection.transmit(prot_apdu)
print(f"Protección actual: {[hex(b) for b in resp]}")

connection.disconnect()
