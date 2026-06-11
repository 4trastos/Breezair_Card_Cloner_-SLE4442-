from smartcard.System import readers

r = readers()
c = r[0].createConnection()
c.connect()

print("=== PRUEBA TAMAÑOS ===")

for size in [1, 4, 8, 16, 32]:
    cmd = [0xFF, 0xB0, 0x00, 0x00, size]

    try:
        data, sw1, sw2 = c.transmit(cmd)

        print("SIZE", size)
        print(data)
        print(hex(sw1), hex(sw2))
        print()

    except Exception as e:
        print("ERROR:", e)

print("=== PRUEBA DIRECCIONES ===")

for addr in [0, 1, 2, 4, 8, 16, 32, 64]:
    cmd = [0xFF, 0xB0, 0x00, addr, 0x10]

    try:
        data, sw1, sw2 = c.transmit(cmd)

        print("ADDR", addr)
        print(data)
        print(hex(sw1), hex(sw2))
        print()

    except Exception as e:
        print("ERROR:", e)
