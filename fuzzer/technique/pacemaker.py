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
        self.last_path_time = 0
        self.last_crash_time = 0
        self.key = False

        if Pacemaker.is_tmp_mode():
            self.total_finds = 0
            self.new_finds = 0

    
    def on(self):
        if self.key:
            if Pacemaker.is_tmp_mode():
                if self.new_finds > self.new_finds * Pacemaker.bound + self.total_finds:
                    self.statistics.event_pacemaker_update(False)
                    self.key = False
                    self.total_finds += self.new_finds
                    self.new_finds = 0

        else:
            if self.last_path_time:
                if time.time() - self.last_path_time >= self.time_limit:
                    if time.time() - self.last_crash_time >= self.time_limit:
                        self.statistics.event_pacemaker_update(True)
                        self.key = True
                        self.total_finds += self.new_finds
                        self.new_finds = 0
            
        return self.key


    def update(self, **data):
        if data['path_time']:
            self.last_path_time = data['path_time']
        if data['crach_time']:
            self.last_crash_time = data['crash_time']
        if data['finds']:
            self.new_finds += data['finds']