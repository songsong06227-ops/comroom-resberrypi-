import time

class Processor:
    def __init__(self, frequency: int):
        self._MOVING_AVERAGE_WINDOW = 10
        self.__ADAPTIVE_FACTOR = 0.8
        self.__PRESENCE_THRESHOLD = 11

        self._frequency = frequency
        self._timestamps = []
        self._ir_samples = []
        self._red_samples = []
        self._filtered_ir_samples = []
        self._filtered_red_samples = []
        self._ratios = []
        self._intervals = []
        self._amplitudes = []

        self._processed_window_size = self._frequency

    def _add_sample(self, ir_sample: int, red_sample: int) -> None:
        self._timestamps.append(time.time())
        self._ir_samples.append(ir_sample)
        self._red_samples.append(red_sample)

        if len(self._ir_samples) >= self._MOVING_AVERAGE_WINDOW:
            filtered_ir = sum(self._ir_samples[-self._MOVING_AVERAGE_WINDOW:]) / self._MOVING_AVERAGE_WINDOW
            filtered_red = sum(self._red_samples[-self._MOVING_AVERAGE_WINDOW:]) / self._MOVING_AVERAGE_WINDOW
            self._filtered_ir_samples.append(filtered_ir)
            self._filtered_red_samples.append(filtered_red)
        else:
            self._filtered_ir_samples.append(ir_sample)
            self._filtered_red_samples.append(red_sample)

        # 오래된 샘플 제거
        if len(self._ir_samples) > self._processed_window_size:
            self._ir_samples.pop(0)
            self._red_samples.pop(0)
            self._timestamps.pop(0)
            self._filtered_ir_samples.pop(0)
            self._filtered_red_samples.pop(0)

    def _presence(self) -> bool:
        if len(self._filtered_ir_samples) < self._MOVING_AVERAGE_WINDOW:
            return False

        baseline = sum(self._filtered_ir_samples[-self._MOVING_AVERAGE_WINDOW:]) / self._MOVING_AVERAGE_WINDOW
        current = self._filtered_ir_samples[-1]
        amplitude = abs(current - baseline)

        self._amplitudes.append(amplitude)
        if len(self._amplitudes) > self._processed_window_size:
            self._amplitudes.pop(0)

        if len(self._amplitudes) >= self._MOVING_AVERAGE_WINDOW:
            filtered_amplitude = sum(self._amplitudes[-self._MOVING_AVERAGE_WINDOW:]) / self._MOVING_AVERAGE_WINDOW
        else:
            filtered_amplitude = amplitude

        return filtered_amplitude > self.__PRESENCE_THRESHOLD
        
    def _peaks(self) -> list:
        peaks = []
        if len(self._filtered_ir_samples) < 3:
            return peaks

        # 동적 최소 피크 간격
        if len(self._intervals) >= self._MOVING_AVERAGE_WINDOW:
            avg_interval = sum(self._intervals[-self._MOVING_AVERAGE_WINDOW:]) / self._MOVING_AVERAGE_WINDOW
            min_interval = avg_interval * self.__ADAPTIVE_FACTOR
        else:
            min_interval = 0.3

        recent = self._filtered_ir_samples
        min_value = min(recent)
        max_value = max(recent)
        threshold = min_value + (max_value - min_value) * 0.5

        for i in range(1, len(recent) - 1):
            if recent[i] > recent[i - 1] and recent[i] > recent[i + 1] and recent[i] > threshold:
                if peaks and (self._timestamps[i] - peaks[-1][0] < min_interval):
                    if peaks[-1][1] < recent[i]:
                        peaks[-1] = (self._timestamps[i], recent[i])
                else:
                    peaks.append((self._timestamps[i], recent[i]))

        return peaks
