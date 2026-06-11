#! /usr/bin/env python

import sys
from smartcard.scard import *
import smartcard.util

SELECT = [0xFF, 0xA4, 0x00, 0x00, 0x01, 0x06]
READ = [0xFF, 0xB0, 0x00]
WRITE = [0xFF, 0xD0, 0x00]
UNLOCK_WRITING = [0xFF, 0x20, 0x00, 0x00, 0x03]
CHANGE_PIN = [0xFF, 0xD2, 0x00, 0x01, 0x03]

hcard = None
dwActiveProtocol = None
hcontext = None
reader = None

def connect():
    global hcard, dwActiveProtocol, hcontext, reader
    try:
        hresult, hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
        if hresult != SCARD_S_SUCCESS:
            raise Exception('Failed to establish context: ' + SCardGetErrorMessage(hresult))
        print('Context established!')

        hresult, readers = SCardListReaders(hcontext, [])
        if hresult != SCARD_S_SUCCESS:
            raise Exception('Failed to list readers: ' + SCardGetErrorMessage(hresult))
        print('PCSC Readers:', readers)

        if len(readers) < 1:
            raise Exception('No smart card readers')

        reader = readers[0]
        print("Using reader:", reader)

        hresult, hcard, dwActiveProtocol = SCardConnect(hcontext, reader, SCARD_SHARE_SHARED, SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1)
        if hresult != SCARD_S_SUCCESS:
            raise Exception('Unable to connect: ' + SCardGetErrorMessage(hresult))
        print('Connected with active protocol', dwActiveProtocol)

        hresult, response = SCardTransmit(hcard, dwActiveProtocol, SELECT)
        if hresult != SCARD_S_SUCCESS:
            raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
        print('Card initialized successfully')
        
    except Exception as message:
        print("Exception:", message)

def read_all():
    try:
        hresult, response = SCardTransmit(hcard, dwActiveProtocol, READ + [0, 255])
        if hresult != SCARD_S_SUCCESS:
            raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
        if (response[-2] == 144):
            hex_data = [format(byte, '02X') for byte in response[:-2]]
            print('Read data:', ' '.join(hex_data))
    except Exception as message:
        print("Exception:", message)

def write_all(data):
    try:
        result = [ord(c) for c in data]
        hresult, response = SCardTransmit(hcard, dwActiveProtocol, WRITE + [0, len(result)] + result)
        if hresult != SCARD_S_SUCCESS:
            raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
        print('Write successful')
    except Exception as message:
        print("Exception:", message)

def unlock(pin):
    try:
        if len(pin) != 6:
            print('PIN must be three characters long')
        else:
            hresult, response = SCardTransmit(hcard, dwActiveProtocol, UNLOCK_WRITING + [int(pin[i:i+2],16) for i in range(0,6,2)])
            if hresult != SCARD_S_SUCCESS:
                raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
            if response[-1] == 7:
                print('Card unlocked for writing')
            elif response[-1] == 0:
                print("Card is locked")
            else:
                print("Incorrect PIN")
    except Exception as message:
        print("Exception:", message)

def change_pin(pin):
    try:
        if len(pin) != 6:
            print('PIN must be three characters long')
        else:
            hresult, response = SCardTransmit(hcard, dwActiveProtocol, CHANGE_PIN + [int(pin[i:i+2],16) for i in range(0,6,2)])
            if hresult != SCARD_S_SUCCESS:
                raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
            if (response[-2] == 144):
                print('PIN changed successfully')
    except Exception as message:
        print("Exception:", message)

def disconnect():
    try:
        hresult = SCardDisconnect(hcard, SCARD_UNPOWER_CARD)
        if hresult != SCARD_S_SUCCESS:
            raise Exception('Failed to disconnect: ' + SCardGetErrorMessage(hresult))
        print('Disconnected')
        hresult = SCardReleaseContext(hcontext)
        if hresult != SCARD_S_SUCCESS:
            raise Exception('Failed to release context: ' + SCardGetErrorMessage(hresult))
        print('Released context.')
    except Exception as message:
        print("Exception:", message)

def write_protection():
    WRITE_PROT = [0xFF, 0xD1, 0x00]
    READ_PROT = [0xFF, 0xB4, 0x00, 0x00, 0x04]
    protection = [0x30, 0xFF, 0x1F, 0xF8]
    try:
        for i, byte in enumerate(protection):
            if byte == 0xFF:
                continue
            hresult, response = SCardTransmit(hcard, dwActiveProtocol, WRITE_PROT + [i, 0x01, byte])
            if hresult != SCARD_S_SUCCESS:
                raise Exception('Failed to transmit: ' + SCardGetErrorMessage(hresult))
            print(f'Protection byte {i} -> 0x{byte:02X}: {[hex(b) for b in response]}')
        hresult, response = SCardTransmit(hcard, dwActiveProtocol, READ_PROT)
        print(f'Protection memory: {[hex(b) for b in response[:-2]]}')
    except Exception as message:
        print("Exception:", message)

if __name__ == "__main__":
    connect()
    
    while True:
        command = input("Enter command (read/write/unlock/change_pin/disconnect/protect/exit): ").strip().lower()
        
        if command == 'read':
            read_all()
        elif command == 'write':
            data = input("Enter data to write (255 characters max): ")
            write_all(data[:255])
        elif command == 'unlock':
            pin = input("Enter PIN to unlock: ")
            unlock(pin)
        elif command == 'change_pin':
            pin = input("Enter new PIN (3 characters): ")
            change_pin(pin)
        elif command == 'disconnect':
            disconnect()
            break
        elif command == 'protect':
            write_protection()
        elif (command == 'exit') or (command == 'q'):
            break
        else:
            print("Unknown command.")

