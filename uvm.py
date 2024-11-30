import struct
import csv
import sys

# Размеры команд
COMMAND_SIZES = {
    201: 4,  # Загрузка константы
    57: 3,  # Чтение из памяти
    27: 3,  # Запись в память
    113: 4  # Побитовый логический сдвиг вправо
}


# Ассемблер
def assemble(input_file, output_file, log_file):
    with open(input_file, "r") as f, open(output_file, "wb") as bin_f, open(log_file, "w", newline="") as log_f:
        log_writer = csv.writer(log_f)
        log_writer.writerow(["Command", "B", "C", "D"])

        for line in f:
            parts = line.strip().split()
            opcode = int(parts[0])
            args = list(map(int, parts[1:]))
            command_size = COMMAND_SIZES.get(opcode)

            if opcode == 201:  # Загрузка константы
                b, c = args
                binary = struct.pack("<BHI", opcode, b, c)
                log_writer.writerow([opcode, b, c, "N/A"])
            elif opcode in (57, 27):  # Чтение или запись из памяти
                b, c = args
                binary = struct.pack("<BH", opcode, (b << 5) | c)
                log_writer.writerow([opcode, b, c, "N/A"])
            elif opcode == 113:  # Побитовый логический сдвиг вправо
                b, c, d = args
                binary = struct.pack("<BI", opcode, (b << 14) | (c << 9) | (d << 5))
                log_writer.writerow([opcode, b, c, d])
            else:
                raise ValueError(f"Unknown opcode: {opcode}")

            bin_f.write(binary)


# Интерпретатор
def interpret(binary_file, output_file, memory_range):
    memory = [0] * 1024
    registers = [0] * 32

    with open(binary_file, "rb") as f:
        while command := f.read(1):  # Читаем первый байт (опкод)
            opcode = command[0]
            command_size = COMMAND_SIZES.get(opcode)
            if command_size is None:
                raise ValueError(f"Unknown opcode: {opcode}")

            # Читаем необходимое количество байт для текущей команды
            command_data = f.read(command_size - 1)  # Один байт уже прочитан (опкод)

            if opcode == 201:  # Загрузка константы
                b, c = struct.unpack("<BHI", bytes(command + command_data))
                registers[b] = c
            elif opcode == 57:  # Чтение из памяти
                b, bc = struct.unpack("<BH", bytes(command + command_data))
                b = (bc >> 5) & 0x1F
                c = bc & 0x1F
                registers[b] = memory[registers[c]]
            elif opcode == 27:  # Запись в память
                b, bc = struct.unpack("<BH", bytes(command + command_data))
                b = (bc >> 5) & 0x1F
                c = bc & 0x1F
                memory[registers[b]] = registers[c]
            elif opcode == 113:  # Побитовый логический сдвиг вправо
                b, bc = struct.unpack("<BI", bytes(command + command_data))
                b = (bc >> 14) & 0x1FFFF
                c = (bc >> 9) & 0x1F
                d = (bc >> 5) & 0x1F
                memory[b] = registers[d] >> registers[c]
            else:
                raise ValueError(f"Unknown opcode: {opcode}")

    # Сохраняем результаты в файл
    with open(output_file, "w", newline="") as out_f:
        writer = csv.writer(out_f)
        writer.writerow(["Address", "Value"])
        for i in range(*memory_range):
            writer.writerow([i, memory[i]])


# Основная программа
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Assembler and Interpreter for UVM")
    subparsers = parser.add_subparsers(dest="command")

    # Ассемблер
    asm_parser = subparsers.add_parser("assemble")
    asm_parser.add_argument("input_file", help="Path to the input assembly file")
    asm_parser.add_argument("output_file", help="Path to the output binary file")
    asm_parser.add_argument("log_file", help="Path to the log file")

    # Интерпретатор
    interp_parser = subparsers.add_parser("interpret")
    interp_parser.add_argument("binary_file", help="Path to the input binary file")
    interp_parser.add_argument("output_file", help="Path to the output result file")
    interp_parser.add_argument("memory_range", type=int, nargs=2, help="Memory range to dump (start end)")

    args = parser.parse_args()

    if args.command == "assemble":
        assemble(args.input_file, args.output_file, args.log_file)
    elif args.command == "interpret":
        interpret(args.binary_file, args.output_file, args.memory_range)
