import struct
import csv
import sys

# Словарь для преобразования команд
COMMANDS = {
    "LOAD_CONST": 201,
    "READ_MEM": 57,
    "WRITE_MEM": 27,
    "LOGIC_RSHIFT": 113,
}


def assemble(input_file, output_file, log_file):
    binary_data = []
    log_data = []

    # Чтение текстового файла с программой
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    for line in lines:
        line = line.strip()
        if not line:  # Пропуск пустых строк
            continue

        parts = line.split()
        cmd, *args = parts
        opcode = COMMANDS.get(cmd)

        if opcode is None:
            print(f"Неизвестная команда: {cmd}")
            continue

        if cmd == "LOAD_CONST":
            b = int(args[0])  # Адрес регистра
            c = int(args[1])  # Константа
            instruction = (opcode & 0xFF) | ((b & 0x1F) << 8) | ((c & 0x7FFFF) << 13)
            binary_data.append(struct.pack('<I', instruction))
            log_data.append({'A': opcode, 'B': b, 'C': c, 'D': ''})

        elif cmd in {"READ_MEM", "WRITE_MEM"}:
            b = int(args[0])  # Адрес регистра
            c = int(args[1])  # Адрес памяти
            instruction = (opcode & 0xFF) | ((b & 0x1F) << 8) | ((c & 0x1F) << 13)
            binary_data.append(struct.pack('<I', instruction)[:3])
            log_data.append({'A': opcode, 'B': b, 'C': c, 'D': ''})

        elif cmd == "LOGIC_RSHIFT":
            b = int(args[0])  # Адрес памяти
            c = int(args[1])  # Адрес регистра (второй операнд)
            d = int(args[2])  # Адрес регистра (первый операнд)
            instruction = (opcode & 0xFF) | ((b & 0x3FFF) << 8) | ((c & 0x1F) << 22) | ((d & 0x1F) << 27)
            binary_data.append(struct.pack('<I', instruction))
            log_data.append({'A': opcode, 'B': b, 'C': c, 'D': d})

    # Сохранение в бинарный файл
    with open(output_file, 'wb') as outfile:
        outfile.writelines(binary_data)

    # Сохранение лога
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
