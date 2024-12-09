import struct
import sys
import csv

MEMORY_SIZE = 1024
REGISTER_COUNT = 32


def interpret(binary_file, result_file, memory_range):
    # Инициализация памяти и регистров
    memory = [0] * MEMORY_SIZE
    registers = [0] * REGISTER_COUNT

    # Чтение бинарного файла
    with open(binary_file, 'rb') as f:
        binary_data = f.read()

    pc = 0  # Счётчик команд (Program Counter)
    while pc < len(binary_data) - 1:
        opcode = binary_data[pc]
        cmd_name = None

        if opcode == 201:  # LOAD_CONST
            cmd_name = "LOAD_CONST"
            instruction = struct.unpack_from('<I', binary_data, pc)[0]
            pc += 4

            b = (instruction >> 8) & 0x1F  # Адрес регистра
            c = instruction >> 13  # Константа

            if b < REGISTER_COUNT:
                registers[b] = c
            else:
                print(f"Ошибка: некорректный адрес регистра B={b}")
                break

        elif opcode == 57:  # READ_MEM
            cmd_name = "READ_MEM"
            instruction = struct.unpack_from('<I', binary_data, pc)[0]
            pc += 3
            b = (instruction >> 8) & 0x1F  # Адрес регистра
            c = (instruction >> 13) & 0x1F  # Адрес памяти (регистр)
            if b < REGISTER_COUNT and c < REGISTER_COUNT:
                address = registers[c]
                if 0 <= address < MEMORY_SIZE:
                    registers[b] = memory[address]
                else:
                    print(f"Ошибка: выход за границы памяти при чтении (Адрес={address})")
                    break

        elif opcode == 27:  # WRITE_MEM
            cmd_name = "WRITE_MEM"
            instruction = struct.unpack_from('<I', binary_data, pc)[0]
            pc += 3
            b = (instruction >> 8) & 0x1F  # Адрес памяти (регистр)
            c = (instruction >> 13) & 0x1F  # Значение (регистр)
            if b < REGISTER_COUNT and c < REGISTER_COUNT:
                address = registers[b]
                if 0 <= address < MEMORY_SIZE:
                    memory[address] = registers[c]
                else:
                    print(f"Ошибка: выход за границы памяти при записи (Адрес={address})")
                    break

        elif opcode == 113:  # LOGIC_RSHIFT
            cmd_name = "LOGIC_RSHIFT"
            instruction = struct.unpack_from('<I', binary_data, pc)[0]
            pc += 4
            b = (instruction >> 8) & 0x3FFF  # Адрес памяти
            c = (instruction >> 22) & 0x1F  # Адрес регистра (сдвиг)
            d = (instruction >> 27) & 0x1F  # Адрес регистра (значение)
            if b < MEMORY_SIZE and d < REGISTER_COUNT and c < REGISTER_COUNT:
                shift_amount = registers[c]
                if shift_amount >= 0:  # Проверка корректности сдвига
                    memory[b] = registers[d] >> shift_amount
                else:
                    print(f"Ошибка: недопустимый сдвиг ({shift_amount})")
                    break

        else:
            print(f"Неизвестный код операции: {opcode} по адресу {pc}")
            break

        # Отладочный вывод
        # print(f"Команда: {cmd_name}, Регистры: {registers[:8]}, Память: {memory[:8]}")

    # Сохранение результата
    start, end = map(int, memory_range.split('-'))
    with open(result_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Address", "Value"])
        for i in range(start, end + 1):
            writer.writerow([i, memory[i]])


if __name__ == "__main__":
    # with open("program1.bin", "rb") as f:
    #    print(list(f.read()))

    if len(sys.argv) != 4:
        print("Использование: python interpreter.py <бинарный_файл> <файл_результата> <диапазон_памяти>")
        sys.exit(1)

    interpret(sys.argv[1], sys.argv[2], sys.argv[3])
    # interpret('program1.bin', 'result1.csv', '0-31')
