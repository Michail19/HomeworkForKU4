import struct
import sys
import csv


class Interpreter:
    def __init__(self, binary_file, output_file, memory_range):
        self.binary_file = binary_file
        self.output_file = output_file
        self.memory = [0] * 1024  # Простая модель памяти
        self.memory_range = memory_range

    def load_binary(self):
        with open(self.binary_file, 'rb') as file:
            self.instructions = file.read()

    def execute(self):
        pc = 0
        while pc < len(self.instructions):
            opcode = self.instructions[pc]
            if opcode == 201:
                # Загрузка константы
                _, B, C = struct.unpack('I', self.instructions[pc:pc + 4])
                self.memory[B] = C
                pc += 4
            elif opcode == 57:
                # Чтение из памяти
                _, B, C = struct.unpack('>H', self.instructions[pc:pc + 3])
                address = self.memory[C]
                self.memory[B] = self.memory[address]
                pc += 3
            else:
                pc += 1  # Для неизвестных команд, чтобы избежать зацикливания

    def save_memory(self):
        start, end = self.memory_range
        with open(self.output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Address", "Value"])
            for i in range(start, end):
                writer.writerow([i, self.memory[i]])


if __name__ == "__main__":
    binary_file = sys.argv[1]
    output_file = sys.argv[2]
    memory_start = int(sys.argv[3])
    memory_end = int(sys.argv[4])
    interpreter = Interpreter(binary_file, output_file, (memory_start, memory_end))
    interpreter.load_binary()
    interpreter.execute()
    interpreter.save_memory()
