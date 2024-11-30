import struct
import csv
import sys


def execute(input_file, output_file, memory_range):
    # Инициализация памяти и регистров
    memory = [0] * 1024  # Условный размер памяти УВМ
    registers = [0] * 32

    # Диапазон памяти для результата
    mem_start, mem_end = map(int, memory_range.split('-'))

    # Чтение бинарного файла
    with open(input_file, 'rb') as infile:
        binary_data = infile.read()

    pc = 0  # Указатель команд

    while pc < len(binary_data):
        opcode = binary_data[pc]  # Первый байт - это A

        if opcode == 201:  # LOAD_CONST (4 байта)
            b = binary_data[pc] & 0x1F
            c = struct.unpack('<H', binary_data[pc + 1:pc + 3])[0] >> 5
            registers[b] = c
            pc += 4

        elif opcode == 57:  # READ_MEM (3 байта)
            b = binary_data[pc] & 0x1F
            c = (binary_data[pc + 1] >> 5) & 0x1F
            registers[b] = memory[registers[c]]
            pc += 3

        elif opcode == 27:  # WRITE_MEM (3 байта)
            b = binary_data[pc] & 0x1F
            c = (binary_data[pc + 1] >> 5) & 0x1F
            memory[registers[b]] = registers[c]
            pc += 3

        elif opcode == 113:  # LOGICAL_RSHIFT (4 байта)
            b = struct.unpack('<H', binary_data[pc:pc + 2])[0] & 0x3FFF
            c = (binary_data[pc + 2] >> 5) & 0x1F
            d = (binary_data[pc + 2] >> 27) & 0x1F
            memory[b] = registers[d] >> registers[c]
            pc += 4

        else:
            print(f"Неизвестная команда: {opcode}")
            break

    # Сохранение результата в CSV
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Address', 'Value'])
        for addr in range(mem_start, mem_end + 1):
            writer.writerow([addr, memory[addr]])


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Использование: python interpreter.py <бинарный_файл> <результат_файл> <диапазон>")
        sys.exit(1)
    execute(sys.argv[1], sys.argv[2], sys.argv[3])
