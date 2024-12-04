import csv
import struct
import sys


class VirtualMachine:
    def __init__(self):
        self.memory = [0] * 1024  # Простая память УВМ
        self.registers = [0] * 32  # Регистр УВМ

    def execute_instruction(self, opcode, *args):
        """Выполнение одной инструкции."""
        if opcode == 201:  # LOAD_CONST
            b, c = args
            self.registers[b] = c
        elif opcode == 57:  # LOAD_MEM
            b, c = args
            addr = self.registers[c]
            self.registers[b] = self.memory[addr]
        elif opcode == 27:  # STORE_MEM
            b, c = args
            addr = self.registers[b]
            self.memory[addr] = self.registers[c]
        elif opcode == 113:  # SHIFT_RIGHT
            b, c, d = args
            self.memory[b] = self.registers[d] >> self.registers[c]
        else:
            raise ValueError(f"Неизвестный опкод: {opcode}")

    def run(self, input_file, output_file, memory_range):
        """Выполнение программы."""
        with open(input_file, "rb") as infile:
            while chunk := infile.read(4):  # Читаем инструкцию
                opcode = chunk[0]
                if opcode == 201:
                    b, c = struct.unpack("<HB", chunk[1:])
                    self.execute_instruction(opcode, b, c)
                elif opcode in {57, 27}:
                    combined = struct.unpack("<H", chunk[1:])[0]
                    b, c = combined & 0x1F, combined >> 8
                    self.execute_instruction(opcode, b, c)
                elif opcode == 113:
                    b, c, d = struct.unpack("<HI", chunk[1:])
                    c, d = c & 0x1F, c >> 5
                    self.execute_instruction(opcode, b, c, d)

        # Записываем результаты в CSV
        start, end = map(int, memory_range.split(":"))
        with open(output_file, "w", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["Address", "Value"])
            for i in range(start, end + 1):
                writer.writerow([i, self.memory[i]])


if __name__ == "__main__":
    # Пример вызова: python interpreter.py program.bin result.csv 0:10
    vm = VirtualMachine()
    vm.run(sys.argv[1], sys.argv[2], sys.argv[3])
