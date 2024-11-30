import struct
import csv
import sys


class UVM:
    def __init__(self, memory_size=1024, num_registers=32):
        self.memory = [0] * memory_size  # Память УВМ
        self.registers = [0] * num_registers  # Регистр УВМ
        self.pc = 0  # Программный счётчик

    def load_binary(self, binary_file):
        """Загрузка бинарного файла программы."""
        with open(binary_file, 'rb') as f:
            self.program = f.read()

    def fetch_instruction(self):
        """Получение текущей инструкции."""
        if self.pc >= len(self.program):
            return None  # Конец программы
        if len(self.program) - self.pc >= 4:
            instruction = struct.unpack('<I', self.program[self.pc:self.pc + 4])[0]
            self.pc += 4
        else:
            instruction = struct.unpack('<I', self.program[self.pc:self.pc + 3] + b'\x00')[0]
            self.pc += 3
        return instruction

    def execute(self, instruction):
        """Выполнение инструкции."""
        opcode = instruction & 0xFF  # Извлечение младших 8 бит
        if opcode == 201:  # LOAD_CONST
            b = (instruction >> 8) & 0x1F  # 5 бит: b-регистр
            c = (instruction >> 13) & 0x7FFFF  # 19 бит: константа
            self.registers[b] = c
        elif opcode == 57:  # READ_MEM
            b = (instruction >> 8) & 0x1F  # 5 бит: b-регистр
            c = (instruction >> 13) & 0x1F  # 5 бит: c-регистр
            address = self.registers[c]
            if 0 <= address < len(self.memory):
                self.registers[b] = self.memory[address]
            else:
                raise ValueError(f"Ошибка: неверный адрес памяти {address}.")
        elif opcode == 27:  # WRITE_MEM
            b = (instruction >> 8) & 0x1F  # 5 бит: b-регистр
            c = (instruction >> 13) & 0x1F  # 5 бит: c-регистр
            address = self.registers[b]
            if 0 <= address < len(self.memory):
                self.memory[address] = self.registers[c]
            else:
                raise ValueError(f"Ошибка: неверный адрес памяти {address}.")
        elif opcode == 113:  # LOGICAL_RSHIFT
            b = (instruction >> 8) & 0x3FFF  # 14 бит: адрес памяти
            c = (instruction >> 22) & 0x1F  # 5 бит: c-регистр
            d = (instruction >> 27) & 0x1F  # 5 бит: d-регистр
            if 0 <= b < len(self.memory):
                self.memory[b] = self.registers[d] >> self.registers[c]
            else:
                raise ValueError(f"Ошибка: неверный адрес памяти {b}.")
        else:
            raise ValueError(f"Неизвестная команда с опкодом {opcode}.")

    def run(self):
        """Запуск интерпретации программы."""
        while True:
            instruction = self.fetch_instruction()
            if instruction is None:
                break
            self.execute(instruction)

    def save_memory(self, output_file, memory_range):
        """Сохранение значений из памяти в CSV-файл."""
        start, end = memory_range
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Address", "Value"])
            for i in range(start, end):
                writer.writerow([i, self.memory[i]])


def main():
    if len(sys.argv) < 5:
        print("Использование: python interpreter.py <бинарный_файл> <результат_файл> <диапазон_памяти>")
        print("Пример: python interpreter.py program.bin result.csv 0 10")
        sys.exit(1)

    binary_file = sys.argv[1]
    result_file = sys.argv[2]
    memory_range = (int(sys.argv[3]), int(sys.argv[4]))

    uvm = UVM()
    uvm.load_binary(binary_file)
    uvm.run()
    uvm.save_memory(result_file, memory_range)


if __name__ == "__main__":
    with open("program.bin", "rb") as f:
        binary_data = list(f.read())
    print("Содержимое program.bin:")
    print(binary_data)

    main()
