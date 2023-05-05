import time

from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Algorithm_History(Base):
    __tablename__ = 'algorithm_history'
    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer)
    experiment_time = Column(String)
    range_id = Column(Integer)
    rps_range = Column(String)
    rps = Column(Float)
    slo = Column(Float)
    response = Column(Float)
    cost = Column(Float)
    delta_si = Column(Float)
    delta_response = Column(Float)
    n_s = Column(Integer)
    old_configs = Column(String)
    current_configs = Column(String)
    metrics = Column(String)
    threshold = Column(Float)
    container_stats = Column(String)


class Database:
    def __init__(self, database_file):
        self.engine = create_engine(f'sqlite:///{database_file}')
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def add_data(self, data):
        session = self.Session()
        instance = Algorithm_History(experiment_id=data["experiment_id"], experiment_time=data["time"], range_id=data["range_id"],
                                     rps_range=str(data["rps_range"]), rps=data["rps"], slo=data["slo"],
                                     response=data["response"], cost=data["cost"], delta_si=data["delta_si"],
                                     delta_response=data["delta_response"], n_s=data['n_s'], old_configs=str(data["old_configs"]),
                                     current_configs=str(data["current_configs"]), metrics=str(data['metrics']), threshold=data['threshold'],
                                     container_stats=str(data["container_stats"]))
        result = session.add(instance)
        session.commit()
        session.close()
        return result

    def get_data(self):
        session = self.Session()
        data = session.query(Database).all()
        session.close()
        return data


if __name__ == '__main__':
    history = Database('experiment_history2.db')
    history.create_tables()
    data = {"experiment_id": 100, "time": str(time.time()), "range_id": 1, "rps_range": "{min:300, max:600}","rps": 305,
            "slo": 200, "response": 175.52, "cost": 0.1235, "delta_si": 0.1111, "delta_response": 26.213, "n_s": 1,
            "old_configs": {'carts': 2.0, 'front-end': 3.4}, "current_configs": {'carts': 1.0, 'front-end': 2.4},
            "metrics": {'carts': 14.012, 'catalogue': 45.01}, "threshold": 20.0, 'container_stats': None}

    result = history.add_data(data)
    print(result)
    # print(history.get_data())
