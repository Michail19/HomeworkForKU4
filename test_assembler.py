import unittest
import os
import struct
import csv
from assembler import assemble


class TestAssembler(unittest.TestCase):
    def setUp(self):
        self.input_file = "test_program.txt"
        self.output_file = "test_program.bin"
        self.log_file = "test_program_log.csv"

    def tearDown(self):
        # Удаляем тестовые файлы после выполнения тестов
        if os.path.exists(self.input_file):
            os.remove(self.input_file)
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def test_load_const(self):
        with open(self.input_file, 'w') as f:
            f.write("LOAD_CONST 1 100\n")

        assemble(self.input_file, self.output_file, self.log_file)

        # Проверка бинарного файла
        with open(self.output_file, 'rb') as f:
            data = f.read()
            self.assertEqual(len(data), 5)  # 4 байта инструкции + 1 байт окончания
            instruction = struct.unpack('<I', data[:4])[0]
            self.assertEqual(instruction & 0xFF, 201)  # Опкод
            self.assertEqual((instruction >> 8) & 0x1F, 1)  # Регистр
            self.assertEqual((instruction >> 13), 100)  # Константа

        # Проверка лог-файла
        with open(self.log_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['A'], '201')
            self.assertEqual(rows[0]['B'], '1')
            self.assertEqual(rows[0]['C'], '100')

    def test_invalid_command(self):
        with open(self.input_file, 'w') as f:
            f.write("INVALID_CMD 1 100\n")

        assemble(self.input_file, self.output_file, self.log_file)

        # Проверяем, что бинарный файл пуст
        with open(self.output_file, 'rb') as f:
            data = f.read()
            self.assertEqual(len(data), 1)  # Только байт окончания

        # Проверяем, что лог-файл пуст (кроме заголовка)
        with open(self.log_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 0)
