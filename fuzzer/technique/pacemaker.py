import time

class Pacemaker:
    # 0 < bound < 1 for tmp, 1 <= bound for ever
    bound = 1.1

    @staticmethod
    def is_tmp_mode():
        return 0 < Pacemaker.bound and Pacemaker.bound < 1


    def __init__(self, statistics, time_limit):
        self.statistics = statistics
        self.time_limit = time_limit * 60
        self.last_time = 0
        self.key = False

    
    def on(self):
        if self.key:
            if Pacemaker.is_tmp_mode():
                total_finds = self.statistics.data["bytes_in_bitmap"]
                new_finds = total_finds - self.total_finds_last
                if new_finds > new_finds * Pacemaker.bound + self.total_finds_last:
                    self.statistics.event_pacemaker_update(False)
                    self.key = False

        else:
            if self.last_time:
                if time.time() - self.last_time >= self.time_limit:
                    self.statistics.event_pacemaker_update(True)
                    self.key = True
                    self.total_finds_last = self.statistics.data["bytes_in_bitmap"]
            
        return self.key


    def update_new_event(self):
        self.last_time = time.time()