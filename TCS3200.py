import machine
import time
#import micropython
#micropython.alloc_emergency_exception_buf(100)

class TCS3200:

    FULL_SCALE_FREQ = 600e3
    WAIT_PERIOD_MS = 100
    CALC_PERIOD_MS = 50
    MAX_NUM_PULSES = 200

    scaling_value = {'LL' : 0.0,
                     'LH' : 0.02,
                     'HL' : 0.2,
                     'HH' : 1.0}
    scaling_pin = {'LL' : [0, 0],
                   'LH' : [0, 1],
                   'HL' : [1, 0],
                   'HH' : [1, 1]}    
    scaling = 'HH'
    enable_scaling = False

    color_pin = {'R' : [0, 0],
                 'G' : [1, 1],
                 'B' : [0, 1],
                 'C' : [1, 0]}
    cur_color = 'C'
    cur_n_pulses = 0
    stop_calc = True

    cur_color_vector = [0, 0, 0]

    def set_scaling(self, scaling):
        if scaling in self.scaling_pin.keys() and self.enable_scaling:
            self.s0.value(self.scaling_pin[scaling][0])
            self.s1.value(self.scaling_pin[scaling][1])
            self.scaling = scaling

    def full_freq(self):
        return self.FULL_SCALE_FREQ * self.scaling_value[self.scaling]

    def choose_color(self, color):
        if color in self.color_pin.keys():
            self.s2.value(self.color_pin[color][0])
            self.s3.value(self.color_pin[color][1])
            self.cur_color = color

    def calc_freq(self):
        time.sleep_ms(self.WAIT_PERIOD_MS)
        self.cur_n_pulses = 0
        self.stop_calc = False
        start_time = time.ticks_us()
        #self.wdt.feed()
        self.out.irq(handler = self.pulse_count, trigger = machine.Pin.IRQ_FALLING, hard = True) 
        #time.sleep_ms(self.CALC_PERIOD_MS)
        #self.out.irq(handler = None)
        while not(self.stop_calc):
          #time.sleep_ms(1)
          pass
        delta_time = time.ticks_diff(time.ticks_us(), start_time)
        return 1e6 * self.cur_n_pulses / delta_time

    def pulse_count(self, isr):
        self.cur_n_pulses += 1
        if self.cur_n_pulses >= self.MAX_NUM_PULSES:
          self.out.irq(handler = None)
          self.stop_calc = True

    def get_color(self):
        # Red
        self.choose_color('R')
        freq = self.calc_freq()
        self.cur_color_vector[0] = freq / self.full_freq()
        # Green
        self.choose_color('G')
        freq = self.calc_freq()
        self.cur_color_vector[1] = freq / self.full_freq()
        # Blue
        self.choose_color('B')
        freq = self.calc_freq()
        self.cur_color_vector[2] = freq / self.full_freq()
               
    def __init__(self, out_pin, s2_pin, s3_pin, s0_pin = -1, s1_pin = -1):
        self.out = machine.Pin(out_pin, machine.Pin.IN)
        self.s2 = machine.Pin(s2_pin, machine.Pin.OUT)
        self.s3 = machine.Pin(s3_pin, machine.Pin.OUT)
        #self.wdt = machine.WDT(0)
        #self.wdt.timeout = 10000
        #self.wdt.feed()
        if s0_pin > 0 and s1_pin > 0:
            self.s0 = machine.Pin(s0_pin, machine.Pin.OUT)
            self.s1 = machine.Pin(s1_pin, machine.Pin.OUT)
            self.enable_scaling = True
            self.set_scaling('HH')
        else:
            self.enable_scaling = False
            self.scaling = 'HH'
        

