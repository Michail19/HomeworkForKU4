import csv
import struct
import sys


def interpret(binary_file, output_file, memory_range):
    memory = [0] * memory_range  # Инициализация памяти
    pc = 0  # Program counter

    # Загрузка бинарного файла
    with open(binary_file, "rb") as binary:
        program = binary.read()

    while pc < len(program):
        opcode = program[pc]
        print(f"Интерпретируем код операции: {opcode} по адресу {pc}")  # Для отладки

        if opcode == 201:  # LOAD_CONST
            b, c = struct.unpack_from("HI", program, pc + 1)
            print(f"b={b}, c={c}")  # Для отладки

            if b >= memory_range:
                b = b % memory_range  # Корректируем значение, если оно выходит за пределы

            if b >= memory_range:
                raise IndexError(f"Индекс b={b} выходит за пределы памяти")
            memory[b] = c
            pc += 7
        elif opcode == 57:  # READ_MEM
            b, c = struct.unpack_from("BB", program, pc + 1)
            print(f"b={b}, c={c}")  # Для отладки
            if b >= memory_range:
                b = b % memory_range  # Корректируем значение, если оно выходит за пределы
            if c >= memory_range:
                c = c % memory_range  # Корректируем значение, если оно выходит за пределы
            memory[b] = memory[memory[c]]
            pc += 4
        elif opcode == 27:  # WRITE_MEM
            b, c = struct.unpack_from("BB", program, pc + 1)
            print(f"b={b}, c={c}")  # Для отладки
            if b >= memory_range:
                b = b % memory_range  # Корректируем значение, если оно выходит за пределы
            if c >= memory_range:
                c = c % memory_range  # Корректируем значение, если оно выходит за пределы
            memory[memory[b]] = memory[c]
            pc += 4
        elif opcode == 113:  # LOGIC_RSHIFT
            b, c, d = struct.unpack_from("HHH", program, pc + 1)
            print(f"b={b}, c={c}, d={d}")  # Для отладки
            if b >= memory_range or c >= memory_range or d >= memory_range:
                b = b % memory_range  # Корректируем значение, если оно выходит за пределы
                c = c % memory_range  # Корректируем значение, если оно выходит за пределы
                d = d % memory_range  # Корректируем значение, если оно выходит за пределы
            memory[b] = memory[d] >> memory[c]
            pc += 8
        else:
            # Неизвестный код операции
            print(f"Неизвестный код операции: {opcode} по адресу {pc}")  # Отладочный вывод
            raise ValueError(f"Неизвестная команда: {opcode} по адресу {pc}")

    # Запись результата
    with open(output_file, "w", newline="") as result:
        writer = csv.writer(result)
        for i, value in enumerate(memory):
            writer.writerow([i, value])

    print("Интерпретация завершена.")


if __name__ == "__main__":
    with open('program.bin', 'rb') as f:
        byte = f.read(1)
        while byte:
            print(ord(byte))  # Выведет значение каждого байта в программе
            byte = f.read(1)

    if len(sys.argv) != 4:
        print("Использование: python interpreter.py binary_file output_file memory_range")
        sys.exit(1)

    binary_file, output_file, memory_range = sys.argv[1:4]
    interpret(binary_file, output_file, int(memory_range))
