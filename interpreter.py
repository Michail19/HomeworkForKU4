import struct
import csv
import sys

# Размер памяти виртуальной машины
MEMORY_SIZE = 4096
REGISTER_COUNT = 32

# Константы для команд
COMMANDS = {
    201: "LOAD_CONST",
    57: "READ_MEM",
    27: "WRITE_MEM",
    113: "LOGIC_RSHIFT",
}


def interpret(binary_file, output_file, memory_range):
    # Инициализация памяти и регистров
    memory = [0] * MEMORY_SIZE
    registers = [0] * REGISTER_COUNT

    # Чтение бинарного файла
    with open(binary_file, 'rb') as infile:
        binary_data = infile.read()

    # Разбор команд
    pc = 0  # Счётчик команд (программный счётчик)
    while pc < len(binary_data):
        opcode = binary_data[pc]
        cmd_name = COMMANDS.get(opcode)

        if cmd_name == "LOAD_CONST":
            instruction = struct.unpack_from('<I', binary_data, pc)[0]
            pc += 4

            b = (instruction >> 8) & 0x1F
            c = (instruction >> 13) & 0x7FFFF
            registers[b] = c

        elif cmd_name == "READ_MEM":
            instruction = struct.unpack_from('<I', binary_data + b'\x00', pc)[0]
            pc += 3

            b = (instruction >> 8) & 0x1F
            c = (instruction >> 13) & 0x1F
            address = registers[c]
            if address < MEMORY_SIZE:
                registers[b] = memory[address]
            else:
                print(f"Ошибка: выход за границы памяти ({address})")
                break

        elif cmd_name == "WRITE_MEM":
            instruction = struct.unpack_from('<I', binary_data + b'\x00', pc)[0]
            pc += 3

            b = (instruction >> 8) & 0x1F
            c = (instruction >> 13) & 0x1F
            address = registers[b]
            if address < MEMORY_SIZE:
                memory[address] = registers[c]
            else:
                print(f"Ошибка: выход за границы памяти ({address})")
                break

        elif cmd_name == "LOGIC_RSHIFT":
            instruction = struct.unpack_from('<I', binary_data, pc)[0]
            pc += 4
            b = (instruction >> 8) & 0x3FFF  # Адрес памяти
            c = (instruction >> 22) & 0x1F  # Адрес регистра (второй операнд)
            d = (instruction >> 27) & 0x1F  # Адрес регистра (первый операнд)
            if b < MEMORY_SIZE and d < REGISTER_COUNT and c < REGISTER_COUNT:
                shift_amount = registers[c]
                if shift_amount >= 0:  # Сдвиг на 0 бит допустим
                    memory[b] = registers[d] >> shift_amount
                else:
                    print(f"Ошибка: недопустимый сдвиг ({shift_amount})")
                    break
            else:
                print(f"Ошибка: выход за границы памяти или регистров (B={b}, C={c}, D={d})")
                break

        else:
            print(f"Неизвестная команда: {opcode}")
            break

    # Сохранение указанного диапазона памяти в файл
    start, end = map(int, memory_range.split('-'))
    if start >= 0 and end < MEMORY_SIZE and start <= end:
        with open(output_file, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["Address", "Value"])
            for addr in range(start, end + 1):
                writer.writerow([addr, memory[addr]])
    else:
        print(f"Ошибка: неверный диапазон памяти ({memory_range})")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Использование: python interpreter.py <бинарный_файл> <файл_результата> <диапазон_памяти>")
        sys.exit(1)
    interpret(sys.argv[1], sys.argv[2], sys.argv[3])
