import struct
import sys


class Interpreter:
    def __init__(self, instructions):
        self.instructions = instructions

    def execute(self, start_address, end_address):
        pc = start_address
        while pc < end_address:
            if pc >= len(self.instructions):
                print(f"Ошибка: выход за пределы данных на адресе {pc}")
                break

            opcode = self.instructions[pc]
            print(f"PC: {pc}, Opcode: {opcode}")
            print(f"Next Bytes: {self.instructions[pc + 1:pc + 5]}")

            # Если нет данных для команды (меньше 4 байт для стандартной команды)
            if pc + 4 > len(self.instructions):
                print(f"Ошибка: недостаточно данных для команды на адресе {pc}")
                break

            if opcode == 0:
                # Игнорируем опкод 0 или выполняем другие действия
                pc += 1
                continue
            elif opcode == 8:
                # Пропускаем опкод 8, но проверяем, что данных хватает
                print(f"Опкод 8 на адресе {pc}, пропускаем.")
                if pc + 2 <= len(self.instructions):  # Проверяем, есть ли данные для опкода 8
                    pc += 2
                else:
                    print(f"Ошибка: недостаточно данных для опкода 8 на адресе {pc}")
                    break
                continue
            elif opcode == 30:
                # Пропускаем опкод 30
                print(f"Опкод 30 на адресе {pc}, пропускаем.")
                pc += 1
                continue

            if opcode == 201:
                # Пример обработки опкода 201
                if pc + 7 <= len(self.instructions):  # Проверка длины данных для команды
                    A, B, C = struct.unpack('>3H', self.instructions[pc + 1:pc + 7])
                    print(f"Загружена команда: opcode={opcode}, A={A}, B={B}, C={C}")
                    pc += 7  # Переход к следующей команде
                else:
                    print(f"Ошибка: недостаточно данных для команды на адресе {pc}")
                    break
            else:
                print(f"Неизвестный опкод {opcode} по адресу {pc}.")
                break


if __name__ == "__main__":
    binary_file = sys.argv[1]
    output_file = sys.argv[2]
    memory_start = int(sys.argv[3])
    memory_end = int(sys.argv[4])
    interpreter = Interpreter(binary_file, output_file, (memory_start, memory_end))
    interpreter.load_binary()
    interpreter.execute()
    interpreter.save_memory()

# Проверка содержимого бинарного файла
with open('program.bin', 'rb') as f:
    data = f.read()

print("Содержимое бинарного файла (hex):")
print(data.hex())

# Прочитаем по 4 байта и выведем их в виде целых чисел
print("\nИнтерпретация данных по 4 байта:")
for i in range(0, len(data), 4):
    chunk = data[i:i + 4]
    print(f"Адрес {i}: {chunk.hex()} -> {struct.unpack('>I', chunk)[0]}")
