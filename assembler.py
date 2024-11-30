import struct
import csv
import sys

# Словарь для преобразования команд
COMMANDS = {
    "LOAD_CONST": 201,
    "READ_MEM": 57,
    "WRITE_MEM": 27,
    "LOGICAL_RSHIFT": 113,
}


def validate_range(value, bits, field_name):
    """Проверяет, что значение помещается в указанное количество бит."""
    max_value = (1 << bits) - 1
    if not (0 <= value <= max_value):
        raise ValueError(f"{field_name}={value} превышает диапазон ({bits} бит).")


def to_3_bytes(instruction):
    """Преобразует 32-битное число в 3 байта."""
    return instruction.to_bytes(3, byteorder='little')


def assemble(input_file, output_file, log_file):
    binary_data = []
    log_data = []

    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    for line_num, line in enumerate(lines, start=1):
        line = line.strip()

        # Игнорируем комментарии и пустые строки
        if not line or line.startswith('#'):
            continue

        try:
            parts = line.split()
            cmd, *args = parts
            opcode = COMMANDS.get(cmd)

            if opcode is None:
                raise ValueError(f"Неизвестная команда: {cmd}")

            if cmd == "LOAD_CONST":
                b = int(args[0])  # Адрес регистра
                c = int(args[1])  # Константа
                validate_range(b, 5, "B")
                validate_range(c, 19, "C")
                instruction = (opcode & 0xFF) | ((b & 0x1F) << 8) | ((c & 0x7FFFF) << 13)
                binary_data.append(struct.pack('<I', instruction))
                log_data.append({'A': opcode, 'B': b, 'C': c, 'D': ''})

            elif cmd in {"READ_MEM", "WRITE_MEM"}:
                b = int(args[0])  # Адрес регистра
                c = int(args[1])  # Адрес памяти
                validate_range(b, 5, "B")
                validate_range(c, 5, "C")
                instruction = (opcode & 0xFF) | ((b & 0x1F) << 8) | ((c & 0x1F) << 13)
                binary_data.append(to_3_bytes(instruction))
                log_data.append({'A': opcode, 'B': b, 'C': c, 'D': ''})

            elif cmd == "LOGICAL_RSHIFT":
                b = int(args[0])  # Адрес памяти
                c = int(args[1])  # Адрес регистра (второй операнд)
                d = int(args[2])  # Адрес регистра (первый операнд)
                validate_range(b, 14, "B")
                validate_range(c, 5, "C")
                validate_range(d, 5, "D")
                instruction = (opcode & 0xFF) | ((b & 0x3FFF) << 8) | ((c & 0x1F) << 22) | ((d & 0x1F) << 27)
                binary_data.append(struct.pack('<I', instruction))
                log_data.append({'A': opcode, 'B': b, 'C': c, 'D': d})

            else:
                raise ValueError(f"Некорректное количество аргументов для команды {cmd}")

        except Exception as e:
            print(f"Ошибка в строке {line_num}: {line}")
            print(f"Причина: {e}")
            sys.exit(1)

    with open(output_file, 'wb') as outfile:
        for data in binary_data:
            outfile.write(data)

    with open(log_file, 'w', newline='') as logfile:
        fieldnames = ['A', 'B', 'C', 'D']
        writer = csv.DictWriter(logfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(log_data)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Использование: python assembler.py <входной_файл> <выходной_файл> <лог_файл>")
        sys.exit(1)
    assemble(sys.argv[1], sys.argv[2], sys.argv[3])
