import struct
import csv
import sys

# Размер памяти и регистров для УВМ
MEMORY_SIZE = 1024
REGISTER_COUNT = 32

# Инициализация памяти и регистров
memory = [0] * MEMORY_SIZE
registers = [0] * REGISTER_COUNT

def interpret(input_file, result_file, memory_range):
    # Загрузка бинарных данных
    with open(input_file, 'rb') as infile:
        binary_data = infile.read()

    # Индекс текущей команды
    pc = 0  # Program Counter

    while pc < len(binary_data):
        # Определение размера команды (по opcode)
        opcode = binary_data[pc] & 0xFF

        if opcode == 201:  # LOAD_CONST
            instruction = struct.unpack('<I', binary_data[pc:pc+4])[0]
            b = (instruction >> 8) & 0x1F
            c = (instruction >> 13) & 0x7FFFF
            registers[b] = c
            pc += 4

        elif opcode == 57:  # READ_MEM
            instruction = struct.unpack('<I', binary_data[pc:pc+3] + b'\x00')[0]
            b = (instruction >> 8) & 0x1F
            c = (instruction >> 13) & 0x1F
            address = registers[c]
            if 0 <= address < MEMORY_SIZE:
                registers[b] = memory[address]
            else:
                raise ValueError(f"Ошибка: Адрес {address} вне границ памяти")
            pc += 3

        elif opcode == 27:  # WRITE_MEM
            instruction = struct.unpack('<I', binary_data[pc:pc+3] + b'\x00')[0]
            b = (instruction >> 8) & 0x1F
            c = (instruction >> 13) & 0x1F
            address = registers[b]
            if 0 <= address < MEMORY_SIZE:
                memory[address] = registers[c]
            else:
                raise ValueError(f"Ошибка: Адрес {address} вне границ памяти")
            pc += 3

        elif opcode == 113:  # LOGIC_RSHIFT
            instruction = struct.unpack('<I', binary_data[pc:pc+4])[0]
            b = (instruction >> 8) & 0x3FFF
            c = (instruction >> 22) & 0x1F
            d = (instruction >> 27) & 0x1F
            value = registers[d] >> registers[c]
            if 0 <= b < MEMORY_SIZE:
                memory[b] = value
            else:
                raise ValueError(f"Ошибка: Адрес {b} вне границ памяти")
            pc += 4

        else:
            raise ValueError(f"Неизвестный opcode: {opcode}")

    # Сохранение результатов
    memory_start, memory_end = map(int, memory_range.split('-'))
    if not (0 <= memory_start < memory_end <= MEMORY_SIZE):
        raise ValueError("Диапазон памяти указан неверно")

    with open(result_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Address', 'Value'])
        for addr in range(memory_start, memory_end):
            writer.writerow([addr, memory[addr]])

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Использование: python interpreter.py <входной_файл> <файл_результатов> <диапазон_памяти>")
        sys.exit(1)

    interpret(sys.argv[1], sys.argv[2], sys.argv[3])
