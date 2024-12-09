import csv
import os
import struct
import unittest

from interpreter import interpret


class TestInterpreter(unittest.TestCase):
    def setUp(self):
        self.binary_file = "test_program.bin"
        self.result_file = "test_result.csv"

    def tearDown(self):
        # Удаляем тестовые файлы после выполнения тестов
        if os.path.exists(self.binary_file):
            os.remove(self.binary_file)
        if os.path.exists(self.result_file):
            os.remove(self.result_file)

    def test_load_const(self):
        # Генерация бинарного файла
        instruction = (201 & 0xFF) | ((1 & 0x1F) << 8) | (100 << 13)
        with open(self.binary_file, 'wb') as f:
            f.write(struct.pack('<I', instruction))
            f.write(b'\x00')  # Байт окончания

        interpret(self.binary_file, self.result_file, "0-31")

        # Проверяем результат в памяти
        with open(self.result_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 32)  # Проверяем диапазон 0-31
            self.assertEqual(rows[1]['Value'], str(100))  # Регистр 1 должен содержать 100

    def test_out_of_memory(self):
        # Генерация команды с выходом за пределы памяти
        instruction = (27 & 0xFF) | ((31 & 0x1F) << 8) | ((32 & 0x1F) << 13)
        with open(self.binary_file, 'wb') as f:
            f.write(struct.pack('<I', instruction)[:3])
            f.write(b'\x00')  # Байт окончания

        interpret(self.binary_file, self.result_file, "0-31")

        # Проверяем, что память не изменилась
        with open(self.result_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            for row in rows:
                self.assertEqual(row['Value'], '0')
