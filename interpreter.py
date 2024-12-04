import struct
import sys
import csv

# Размеры памяти УВМ и регистров
MEMORY_SIZE = 1024
REGISTER_COUNT = 32

def execute(binary_file, result_file, memory_range):
    # Память и регистры УВМ
    memory = [0] * MEMORY_SIZE
    registers = [0] * REGISTER_COUNT

    # Загрузка бинарного файла
    with open(binary_file, 'rb') as infile:
        instructions = infile.read()

    # Разбор команд
    pc = 0  # Программный счетчик
    while pc < len(instructions):
        opcode = instructions[pc]  # Первый байт — код операции
        if opcode == 201:  # LOAD_CONST
            inst = struct.unpack_from('<I', instructions, pc)[0]
            b = (inst >> 8) & 0x1F
            c = (inst >> 13) & 0x7FFFF
            registers[b] = c
            pc += 4
        elif opcode == 57:  # READ_MEM
            inst = struct.unpack_from('<I', instructions, pc)[0]
            b = (inst >> 8) & 0x1F
            c = (inst >> 13) & 0x1F
            registers[b] = memory[registers[c]]
            pc += 3
        elif opcode == 27:  # WRITE_MEM
            inst = struct.unpack_from('<I', instructions, pc)[0]
            b = (inst >> 8) & 0x1F
            c = (inst >> 13) & 0x1F
            memory[registers[b]] = registers[c]
            pc += 3
        elif opcode == 113:  # LOGIC_RSHIFT
            inst = struct.unpack_from('<I', instructions, pc)[0]
            b = (inst >> 8) & 0x3FFF
            c = (inst >> 22) & 0x1F
            d = (inst >> 27) & 0x1F
            memory[b] = registers[d] >> registers[c]
            pc += 4
        else:
            print(f"Неизвестная команда: {opcode}")
            break

    # Сохранение результатов в CSV
    start, end = map(int, memory_range.split(':'))
    with open(result_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["Address", "Value"])
        for addr in range(start, end + 1):
            writer.writerow([addr, memory[addr]])


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Использование: python interpreter.py <бинарный_файл> <файл_результата> <диапазон_памяти>")
        print("Пример диапазона памяти: 0:15")
        sys.exit(1)
    execute(sys.argv[1], sys.argv[2], sys.argv[3])
