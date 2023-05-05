import sqlite3
import time


class QValueDB:
    def __init__(self):
        self.connection = self.create_connecction()
        self.create_table()

    def create_connecction(self):
        try:
            self.connection = sqlite3.connect("databases/q_value_table.db")
            return self.connection
        except sqlite3.Error as e:
            print(e)
        return None

    def create_table(self):
        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS q_values(
        slo NOT NULL,
        range_id NOT NULL,
        q_value NOT NULL);
        '''
        try:
            c = self.connection.cursor()
            c.execute(create_table_sql)
            self.connection.commit()
        except sqlite3.Error as e:
            print(e)

    def get_q_value(self, slo, range_id):
        query = '''SELECT * FROM q_values WHERE slo=? AND range_id=?'''
        c = self.connection.cursor()
        c.execute(query, (slo, range_id))
        rows = c.fetchall()
        return rows

    def save_q_value(self, slo, range_id, q_value):
        insert_sql = '''INSERT INTO q_values(slo, range_id, q_value) VALUES (?,?,?)'''
        if self.connection:
            c = self.connection.cursor()
            c.execute(insert_sql, (slo, range_id, q_value))
            self.connection.commit()
        else:
            print("Connection Error")

    def close_connection(self):
        self.connection.close()


class HistoryDB:
    def __init__(self):
        self.db_file = "databases/experiment_history.db"
        self.connection = self.create_connection()
        self.create_table()

    def create_connection(self):
        try:
            self.connection = sqlite3.connect(self.db_file)
            return self.connection
        except sqlite3.Error as e:
            print(e)
        return None

    def create_table(self):
        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY,
        experiment_id INTEGER,
        experiment_time TEXT NOT NULL,
        range_id INTEGER NOT NULL ,
        rps_range TEXT NOT NULL ,
        rps REAL NOT NULL ,
        slo REAL NOT NULL ,
        response REAL ,
        cost REAL NOT NULL ,
        delta_si REAL,
        delta_response REAL,
        n_s INT,
        current_configs TEXT NOT NULL ,
        metrics TEXT NOT NULL,
        next_configs TEXT NOT NULL, 
        threshold REAL,
        container_stats TEXT,
        early_slo_violation REAL,
        detection_time REAL,
        responses TEXT);
        '''
        try:
            c = self.connection.cursor()
            c.execute(create_table_sql)
            self.connection.commit()
        except sqlite3.Error as e:
            print(e)

    def close_connection(self):
        self.connection.close()

    def insert_into_table(self, data):
        last_row_id = 0
        insert_value_sql = '''INSERT INTO history(experiment_id, experiment_time, range_id, rps_range, rps, slo, response, cost, delta_si,
        delta_response, n_s, current_configs, metrics, next_configs, threshold, container_stats, early_slo_violation, detection_time, responses) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
        if self.connection:
            try:
                c = self.connection.cursor()
                c.execute(insert_value_sql, (
                    data["experiment_id"], data["time"], data["range_id"], str(data["rps_range"]), data["rps"],
                    data["slo"], data["response"], data["cost"], data["delta_si"], data["delta_response"],
                    data["n_s"], str(data["current_configs"]), str(data["metrics"]),str(data["next_configs"]),
                    data["threshold"], str(data["container_stats"]), data['early_slo_violation'], data['detection_time'], str(data['responses'])))
                last_row_id = c.lastrowid
                self.connection.commit()
            except sqlite3.Error as e:
                print("Insertion failed")
                print(e)
        else:
            print("Connection Error")
        return last_row_id

    def get_data(self, query=None):
        get_data_sql = '''SELECT * FROM history;'''
        c = self.connection.cursor()
        c.execute(get_data_sql)
        rows = c.fetchall()
        for row in rows:
            print(row)

    def select_response_regression(self, slo, range_id):
        query = '''SELECT * FROM history WHERE slo=? AND range_id=?'''
        c = self.connection.cursor()
        c.execute(query, (slo, range_id))
        # c.execute(query, (range_id,))
        rows = c.fetchall()
        return rows

    def get_configuration_with_higher_cost(self, slo, range_id, cost):
        query = '''SELECT * FROM history WHERE delta_response>0 AND cost>? AND slo=? AND range_id=? ORDER BY id DESC LIMIT 1'''
        c = self.connection.cursor()
        c.execute(query, (cost, slo, range_id))
        rows = c.fetchall()

        if rows:
            data = rows[0]
            current_settings = {"id": data[0], "experiment_id": data[1], "experiment_time": data[2], "range_id": data[3],
                                "rps_range": data[4], "rps": data[5], "slo": data[6], "response": data[7], "cost": data[8],
                                "delta_si": data[9], "delta_response": data[10], "n_s": data[11], "current_configs": data[12],
                                "metrics": data[13], "next_configs": data[14], "threshold": data[15], "container_stats": data[16],
                                'early_slo_violation': data[17], "detection_time": data[18], "responses": data[19]}
            return current_settings
        return None

    def get_last_configuration(self, slo, range_id):
        query = '''SELECT * FROM history WHERE slo=? AND range_id=? ORDER BY id DESC LIMIT 1'''
        c = self.connection.cursor()
        c.execute(query, (slo, range_id))
        rows = c.fetchall()
        if rows:
            data = rows[0]
            current_settings = {"id": data[0], "experiment_id": data[1], "experiment_time": data[2], "range_id": data[3],
                                "rps_range": data[4], "rps": data[5], "slo": data[6], "response": data[7], "cost": data[8],
                                "delta_si": data[9], "delta_response": data[10], "n_s": data[11], "current_configs": data[12],
                                "metrics": data[13], "next_configs": data[14], "threshold": data[15], "container_stats": data[16],
                                "early_slo_violation":data[17], "detection_time": data[18], "responses": data[19]}
            return current_settings
        return None

    def get_last_inserted_id(self, slo, range_id):
        query = '''SELECT id FROM history WHERE slo=? AND range_id=? ORDER BY id DESC LIMIT 1'''
        c = self.connection.cursor()
        c.execute(query, (slo, range_id))
        rows = c.fetchall()
        return rows

    def update_latency_of_last_config(self, config_id, latency):
        query = '''UPDATE history SET response=? WHERE id=?'''
        if self.connection:
            try:
                c = self.connection.cursor()
                c.execute(query, (latency, config_id))
                self.connection.commit()
            except sqlite3.Error as e:
                print(e)
        else:
            print('Connection Error')



class SAMPLE_DB:
    def __init__(self):
        self.db_file = "sampling_test.db"
        self.connection = self.create_connection()
        self.create_table()

    def create_connection(self):
        try:
            self.connection = sqlite3.connect(self.db_file)
            return self.connection
        except sqlite3.Error as e:
            print(e)
        return None

    def create_table(self):
        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS samples(
        id INTEGER PRIMARY KEY,
        experiment_time TEXT NOT NULL,
        response REAL NOT NULL);
        '''
        try:
            c = self.connection.cursor()
            c.execute(create_table_sql)
            self.connection.commit()
        except sqlite3.Error as e:
            print(e)

    def insert_into_table(self, data):
        last_row_id = 0
        insert_value_sql = '''INSERT INTO samples(experiment_time, response) VALUES (?,?)'''
        if self.connection:
            try:
                c = self.connection.cursor()
                c.execute(insert_value_sql, (data["experiment_id"], data["response"]))
                last_row_id = c.lastrowid
                self.connection.commit()
            except sqlite3.Error as e:
                print(e)
        else:
            print("Connection Error")
        return last_row_id

    def get_last_configuration(self):
        query = '''SELECT * FROM samples ORDER BY id DESC LIMIT 1'''
        c = self.connection.cursor()
        c.execute(query)
        rows = c.fetchall()
        return rows

    def update_latency_of_last_config(self, config_id, latency):
        query = '''UPDATE samples SET response=? WHERE id=?'''
        if self.connection:
            try:
                c = self.connection.cursor()
                c.execute(query, (latency, config_id))
                self.connection.commit()
            except sqlite3.Error as e:
                print(e)
        else:
            print('Connection error')
# history = HistoryDB()
# # print(history.get_last_configuration(50, 4))
# data = {'experiment_id': 1, 'metrics': {'hotel-reserv-frontend':
#                                             {'cpu_utilization': 7.761958746297343, 'throttles': 0.0,
#                                              'processes': 1, 'load_average': 0.0, 'threads': 29.466666666666665,
#                                              'memory_utilization': 34540748.8, 'io_time': 1.9004484764551264e-09,
#                                              'read_seconds': 0.0, 'write_seconds': 1.0497687557066688e-09}}, 'response': 18.995058899483936,
#                                         'time': 12321321412, 'rps': 445.1,
#                                         'delta_response': -1, 'slo': 50, 'range_id': 4,
#                                         'rps_range': {'min': 401, 'max': 500}, 'cost': 51.0,
#                                         'delta_si': -1, 'n_s': -1, 'threshold': -1,
#                                         'current_configs': {'hotel-reserv-frontend': 4.0, 'hotel-reserv-geo': 2.0, 'hotel-reserv-geo-mongo': 3.0, 'hotel-reserv-profile': 3.0, 'hotel-reserv-profile-mmc': 3.0, 'hotel-reserv-profile-mongo': 3.0, 'hotel-reserv-rate': 3.0, 'hotel-reserv-rate-mmc': 3.0, 'hotel-reserv-rate-mongo': 3.0, 'hotel-reserv-recommendation': 3.0, 'hotel-reserv-recommendation-mongo': 3.0, 'hotel-reserv-reservation': 3.0, 'hotel-reserv-reservation-mmc': 3.0, 'hotel-reserv-reservation-mongo': 3.0, 'hotel-reserv-search': 4.0, 'hotel-reserv-user': 2.0, 'hotel-reserv-user-mongo': 3.0},
#                                         'next_configs': {'hotel-reserv-frontend': 4.0, 'hotel-reserv-geo': 2.0, 'hotel-reserv-geo-mongo': 3.0, 'hotel-reserv-profile': 3.0, 'hotel-reserv-profile-mmc': 3.0, 'hotel-reserv-profile-mongo': 3.0, 'hotel-reserv-rate': 3.0, 'hotel-reserv-rate-mmc': 3.0, 'hotel-reserv-rate-mongo': 3.0, 'hotel-reserv-recommendation': 3.0, 'hotel-reserv-recommendation-mongo': 3.0, 'hotel-reserv-reservation': 3.0, 'hotel-reserv-reservation-mmc': 3.0, 'hotel-reserv-reservation-mongo': 3.0, 'hotel-reserv-search': 4.0, 'hotel-reserv-user': 2.0, 'hotel-reserv-user-mongo': 3.0},
#                                         'container_stats': 'None', 'early_slo_violation': 0, 'detection_time': 120, 'responses': ['19.069158878504666', '18.889223968626503', '18.972906403546247', '18.951424853930284', '18.940293621273167', '18.986608257157243', '18.9761309221175', '18.99487648865821', '19.007909764239855', '18.996833302129055', '18.995058014724368', '18.995058899483936']}
#
# history.insert_into_table(data)
# sample = SAMPLE_DB()
# data = {'experiment_id': 4, 'response': 150}
# value = sample.insert_into_table(data)
# print(value)
# sample.update_latency_of_last_config(3, 200)
# value = sample.get_last_configuration()
# print(value)

# history.get_data()
#
# #history.select_response_regression(200, 2)
# print(history.get_previous_history(200, 0.1123))
# history.close_connection()
