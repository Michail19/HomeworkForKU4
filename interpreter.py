import struct
import csv
import sys


def execute(binary_file, result_file, memory_range):
    memory = [0] * 1024  # Эмуляция памяти
    registers = [0] * 32  # Эмуляция регистров

    with open(binary_file, 'rb') as infile:
        binary_data = infile.read()

    pc = 0
    while pc < len(binary_data):
        opcode = binary_data[pc]

        if opcode == 201:  # LOAD_CONST
            b = (binary_data[pc + 1] >> 3) & 0x1F
            c = struct.unpack('<H', binary_data[pc + 1:pc + 4])[0] >> 5
            registers[b] = c
            pc += 4

        elif opcode == 57:  # READ_MEM
            b = (binary_data[pc + 1] >> 3) & 0x1F
            c = binary_data[pc + 1] & 0x1F
            registers[b] = memory[registers[c]]
            pc += 3

        elif opcode == 27:  # WRITE_MEM
            b = (binary_data[pc + 1] >> 3) & 0x1F
            c = binary_data[pc + 1] & 0x1F
            memory[registers[b]] = registers[c]
            pc += 3

        elif opcode == 113:  # LOGICAL_RSHIFT
            b = struct.unpack('<H', binary_data[pc + 1:pc + 3])[0]
            c = (binary_data[pc + 3] >> 5) & 0x1F
            d = binary_data[pc + 3] & 0x1F
            memory[b] = registers[d] >> registers[c]
            pc += 4

    # Диапазон памяти
    start, end = map(int, memory_range.split('-'))
    result = [{'Address': i, 'Value': memory[i]} for i in range(start, end + 1)]

    # Сохранение результата
    with open(result_file, 'w', newline='') as resfile:
        writer = csv.DictWriter(resfile, fieldnames=['Address', 'Value'])
        writer.writeheader()
        writer.writerows(result)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Использование: python interpreter.py <бинарный_файл> <результат_файл> <диапазон>")
        sys.exit(1)
    execute(sys.argv[1], sys.argv[2], sys.argv[3])
