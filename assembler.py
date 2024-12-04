import csv
import struct
import sys

# Определяем формат инструкций УВМ
COMMANDS = {
    "LOAD_CONST": 201,  # Загрузка константы
    "LOAD_MEM": 57,  # Чтение из памяти
    "STORE_MEM": 27,  # Запись в память
    "SHIFT_RIGHT": 113,  # Побитовый логический сдвиг вправо
}


def assemble_instruction(command, args):
    """Сборка инструкции в бинарный формат."""
    opcode = COMMANDS.get(command)
    if opcode is None:
        raise ValueError(f"Неизвестная команда: {command}")

    if command == "LOAD_CONST":
        b, c = map(int, args)
        return struct.pack("<BHB", opcode, b, c), {"A": opcode, "B": b, "C": c}
    elif command in {"LOAD_MEM", "STORE_MEM"}:
        b, c = map(int, args)
        return struct.pack("<BH", opcode, (c << 8) | b), {"A": opcode, "B": b, "C": c}
    elif command == "SHIFT_RIGHT":
        b, c, d = map(int, args)
        return struct.pack("<BHI", opcode, b, (d << 5) | c), {"A": opcode, "B": b, "C": c, "D": d}
    else:
        raise ValueError(f"Неизвестная команда: {command}")


def assemble(input_file, output_file, log_file):
    """Ассемблер для УВМ."""
    with open(input_file, "r") as infile, open(output_file, "wb") as outfile, open(log_file, "w",
                                                                                   newline="") as log_csv:
        log_writer = csv.DictWriter(log_csv, fieldnames=["A", "B", "C", "D"])
        log_writer.writeheader()

        for line in infile:
            line = line.strip()
            if not line or line.startswith("#"):  # Игнорируем комментарии и пустые строки
                continue
            parts = line.split()
            command, args = parts[0], parts[1:]
            binary, log_entry = assemble_instruction(command, args)
            outfile.write(binary)
            log_writer.writerow(log_entry)


if __name__ == "__main__":
    # Пример вызова: python assembler.py input.txt output.bin log.csv
    assemble(sys.argv[1], sys.argv[2], sys.argv[3])
