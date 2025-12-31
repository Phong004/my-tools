from math import ceil

class AutoConcurrencyScaler:
    def __init__(self, min_threads=5, max_threads=100, latency=1.5):
        """
        
        :param min_threads: Minimum number of threads
        :param max_threads: Maximum number of threads
        :param latency: Response time (seconds).

        """
        self.min_threads = min_threads
        self.max_threads = max_threads
        self.target_latency = latency
        self.current_limit = float(min_threads)
        self.consecutive_errors = 0
    
    def update_result(self, status_code:int, latency:float):
        """
        This function is called to update concurrency
        """
        if status_code in [429, 503, 0]:
            self.consecutive_errors += 1
            self.current_limit = max(self.min_threads, self.current_limit * 0.7)
        elif latency > self.target_latency:
            self.current_limit = max(self.min_threads, self.current_limit * 0.9)
        elif status_code == 200:
            self.consecutive_errors = 0
            if self.current_limit < self.max_threads:
                self.current_limit += 1.0
    
    @property
    def limit(self):
        return ceil(self.current_limit)