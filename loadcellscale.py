# Write your code here :-)

from cedargrove_nau7802 import NAU7802
import board


class LoadCell:

    def __init__(self, address=0x2A, nau7802=None):
        # Instantiate 24-bit load sensor ADC; one channels, default gain of 128
        if nau7802 is None:
            self.nau7802 = NAU7802(board.I2C(), address=address, active_channels=1)
        else:
            self.nau7802 = nau7802

        self.enabled = self.nau7802.enable(True)
        self.nau7802.channel = 1
        self.zero_offset = self.zero_channel()

    def set_calibration(self, physical_measurement=198.3, adc_measurement=159100):
        self.phys_meas = physical_measurement
        self.adc_meas = adc_measurement
        self.calib_scaling = self.phys_meas / self.adc_meas

    def zero_channel(self):
        """Initiate internal calibration for current channel; return raw zero
        offset value. Use when scale is started, a new channel is selected, or to
        adjust for measurement drift. Remove weight and tare from load cell before
        executing."""
        print(
            "channel %1d calibrate.INTERNAL: %5s"
            % (self.nau7802.channel, self.nau7802.calibrate("INTERNAL"))
        )
        print(
            "channel %1d calibrate.OFFSET:   %5s"
            % (self.nau7802.channel, self.nau7802.calibrate("OFFSET"))
        )
        zero_offset = self.read_raw_value(100)  # Read 100 samples to get zero offset
        print("...channel %1d zeroed" % self.nau7802.channel)
        return zero_offset

    def read_raw_value(self, samples=3):
        """Read and average consecutive raw sample values. Return average raw value."""
        sample_sum = 0
        sample_count = samples
        while sample_count > 0:
            if self.nau7802.available():
                sample_sum = sample_sum + self.nau7802.read()
                sample_count -= 1
        return int(sample_sum / samples)

    def read_calibrated_value(self, samples=3):
        raw_value = self.read_raw_value(samples)
        return raw_value * self.calib_scaling


if __name__ == "__main__":
    bob = LoadCell()
    bob.set_calibration()
    print(f'current weight is {bob.read_calibrated_value()}')

