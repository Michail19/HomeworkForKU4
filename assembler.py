import csv
import struct
import sys


def assemble(input_file, binary_file, log_file):
    # Описание инструкций УВМ
    instruction_formats = {
        "LOAD_CONST": (201, "BHI", 7),  # 7 байт: A (1), B (2), C (4)
        "READ_MEM": (57, "BBH", 4),  # 4 байта: A (1), B (1), C (2)
        "WRITE_MEM": (27, "BBH", 4),  # 4 байта: A (1), B (1), C (2)
        "LOGIC_RSHIFT": (113, "BHHH", 8),  # 8 байт: A (1), B (2), C (2), D (2)
    }

    binary_data = bytearray()
    log_entries = []

    # Чтение и обработка исходного файла
    with open(input_file, "r") as source:
        for index, line in enumerate(source):
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            command = parts[0]
            operands = list(map(int, parts[1:]))

            if command not in instruction_formats:
                raise ValueError(f"Неизвестная команда: {command} в строке {index + 1}")

            opcode, fmt, size = instruction_formats[command]

            # Проверка длины операндов
            required_operands = len(fmt) - 1  # Один слот занимает opcode
            if len(operands) != required_operands:
                raise ValueError(
                    f"Неверное число операндов для {command}: ожидалось {required_operands}, получено {len(operands)}")

            # Упаковка команды
            packed_command = struct.pack(fmt, opcode, *operands)
            binary_data.extend(packed_command)

            # Логирование
            log_entries.append({
                "строка": index + 1,
                "команда": command,
                "операнды": operands,
                "размер": size
            })

    # Запись бинарного файла
    with open(binary_file, "wb") as binary_out:
        binary_out.write(binary_data)

    # Запись лог-файла
    with open(log_file, "w", newline="") as log_out:
        writer = csv.DictWriter(log_out, fieldnames=["строка", "команда", "операнды", "размер"])
        writer.writeheader()
        writer.writerows(log_entries)

    print("Ассемблирование завершено.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Использование: python assembler.py input_file binary_file log_file")
        sys.exit(1)

    input_file, binary_file, log_file = sys.argv[1:4]
    assemble(input_file, binary_file, log_file)
