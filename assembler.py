import struct
import csv
import sys


class Assembler:
    def __init__(self, source_file, binary_file, log_file):
        self.source_file = source_file
        self.binary_file = binary_file
        self.log_file = log_file

    def assemble(self):
        binary_data = []
        log_data = []

        with open(self.source_file, 'r') as file:
            for line in file:
                parts = line.strip().split()
                instruction = int(parts[0])
                if instruction == 201:
                    # Загрузка константы
                    A, B, C = int(parts[0]), int(parts[1]), int(parts[2])
                    binary_data.append(struct.pack('I', (A << 24) | (B << 8) | C))
                    log_data.append({"A": A, "B": B, "C": C})
                elif instruction == 57:
                    # Чтение значения из памяти
                    A, B, C = int(parts[0]), int(parts[1]), int(parts[2])
                    binary_data.append(struct.pack('>H', (A << 8) | (B << 4) | C))
                    log_data.append({"A": A, "B": B, "C": C})

        # Запись в бинарный файл
        with open(self.binary_file, 'wb') as file:
            for data in binary_data:
                file.write(data)

        # Запись в лог-файл
        with open(self.log_file, 'w', newline='') as csvfile:
            fieldnames = ['A', 'B', 'C']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in log_data:
                writer.writerow(row)


if __name__ == "__main__":
    source_file = sys.argv[1]
    binary_file = sys.argv[2]
    log_file = sys.argv[3]
    assembler = Assembler(source_file, binary_file, log_file)
    assembler.assemble()
