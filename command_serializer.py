from .constants import *

def escape_specials(data: bytes) -> bytes:
    arr = bytearray()
    for byte in data:
        # byte if not default
        arr.extend(SPECIAL_CHARS.get(byte, (byte)))
    return bytes(arr)

def sum_checksum(data: bytes) -> bytes:
    return int.to_bytes(sum(data) & 255, 1, "little")

def package_data_for_bt(data_type: int, command_data: bytes, unk: int) -> bytes:
    """
    unk: Seems to be some type of ack value? Based on current understanding (1|0)
    References:
    * DataType
    * CommandBluetoothSender:sendCommandWithRetries
    * BluetoothSenderWrapper.sendCommandViaBluetooth
    # 
    """ 
    if data_type > 255 or unk > 255 or data_type < 0 or unk < 0:
        raise Exception("dataType and unk must be between 0 and 255")

    data_type_byte = int.to_bytes(data_type, 1, "little")
    unk_byte = int.to_bytes(unk, 1, "little")
    data_size_big_endian = int.to_bytes(len(command_data), 4, "big")
    data_to_check = data_type_byte + unk_byte + data_size_big_endian + command_data
    checksum = sum_checksum(data_to_check)
    data_to_escape = data_to_check + checksum
    final_command = START_MARKER + escape_specials(data_to_escape) + END_MARKER

    # Message will be chunked if it's larger than MAX_BLUETOOTH_MESSAGE_SIZE, just crash to deal with it for now
    if len(final_command) > MAX_BLUETOOTH_MESSAGE_SIZE:
        raise Exception(f"Exceeded {MAX_BLUETOOTH_MESSAGE_SIZE}, can't handle chunked messages")

    return final_command
    
