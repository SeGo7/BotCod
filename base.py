import datetime
from utilities import is_phone_number

import sqlite3
from datetime import datetime

from config import symbols10, symbols11


class DatabaseManager:
    def __init__(self, db_name="Users"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.conn = sqlite3.connect(db_name)

    def name_in_base(self, full_name):
        self.cursor.execute("SELECT id_child FROM children WHERE full_name = ?", (full_name,))
        return self.cursor.fetchone()

    def registration_child(self, full_name, id_child):
        self.cursor.execute("SELECT id_child FROM children WHERE full_name = ?", (full_name,))
        result = self.cursor.fetchone()

        if result and result[0] is None:
            self.cursor.execute(
                "UPDATE children SET id_child = ? WHERE full_name = ?",
                (id_child, full_name)
            )
            self.conn.commit()
            return True
        return False

    def add_phone_number(self, id_child, telephone):
        if is_phone_number(telephone):
            self.cursor.execute("UPDATE children SET telephone = ? WHERE id_child = ?", (telephone, id_child))
            self.connection.commit()
            return True
        return False

    def set_out(self, full_name, command):
        if command == 'б':
            self.cursor.execute('''UPDATE children SET out_med = TRUE WHERE full_name = ?''', (full_name,))
        elif command == 'з':
            self.cursor.execute('''UPDATE children SET out_state = TRUE WHERE full_name = ?''', (full_name,))
        elif command == 'т':
            self.cursor.execute('''UPDATE children SET out_state = False, out_med = False WHERE full_name = ?''', (full_name,))

        self.cursor.connection.commit()

    def is_walk(self, id_child):
        self.cursor.execute("SELECT status_walk FROM children WHERE id_child = ?", (id_child,))
        return self.cursor.fetchone()[0]

    def set_walk_true(self, id_child):
        self.cursor.execute("SELECT status_walk FROM children WHERE id_child = ?", (id_child,))
        result = self.cursor.fetchone()

        if result and not result[0]:
            cur_time_hour = datetime.now().hour
            cur_time_minute = datetime.now().minute
            time_start = str(cur_time_hour) + ':' + str(cur_time_minute)
            if cur_time_hour == 15:
                time_end = str(cur_time_hour + 1) + ':' + str(cur_time_minute)
            else:
                time_end = '17:00'

            self.cursor.execute('''UPDATE children 
                                   SET time_start = ?, time_finish = ?, status_walk = ? 
                                   WHERE id_child = ?''',
                                (time_start,
                                 time_end,
                                 True, id_child))
            self.connection.commit()
            return time_end
        return False

    def return_from_walk(self, id_child):
        time_end = str(datetime.now().hour) + ':' + str(datetime.now().minute)

        self.cursor.execute('''UPDATE children 
                                           SET time_finish = ?, status_walk = ? 
                                           WHERE id_child = ?''',
                            (time_end,
                             False, id_child))
        self.connection.commit()
        return True

    def get_info_id(self, id_child):
        self.cursor.execute('''SELECT * FROM children WHERE id_child = ?''', (id_child,))
        return self.cursor.fetchone()

    def get_info_name(self, name):
        self.cursor.execute('''SELECT * FROM children WHERE full_name = ?''', (name,))
        res = self.cursor.fetchone()
        if res[3] is not None:
            return res[1] + "Номер телефона: " + res[3]
        else:
            return "Нет детальной информации"

    def get_info_class(self, class_name) -> str:
        res = f"Информация о классе {class_name}:\n"
        res += "{:<30} {:<10} {:<10} {:<10}\n".format("Ученик", "Гуляет", "Болеет", "По заявлению")
        res += "-" * 80 + "\n"

        self.cursor.execute('''SELECT * FROM children WHERE class_name = ?''', (class_name,))
        for child in self.cursor.fetchall():
            name = child[1]
            walks = "✔" if child[4] else "✖"
            sick = "✔" if child[7] else "✖"
            request = "✔" if child[8] else "✖"

            res += "{:<30} {:<10} {:<10} {:<10}\n".format(name, walks, sick, request)

        return res

    def get_info_special(self, command):
        res = []

        if command == "10":
            for i in symbols10:
                res += [self.get_info_class(f"10{i}") + "\n"]
        elif command == "11":
            for i in symbols11:
                res += [self.get_info_class(f"11{i}") + "\n"]
        elif command == "все":
            for i in symbols10:
                res += [self.get_info_class(f"10{i}") + "\n"]
            for i in symbols11:
                res += [self.get_info_class(f"11{i}") + "\n"]
        return res

    def id_in_base(self, id_child):
        self.cursor.execute('''SELECT id_child FROM children WHERE id_child = ?''', (id_child,))
        return bool(self.cursor.fetchone())
