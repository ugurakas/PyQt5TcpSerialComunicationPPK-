

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget,QTextEdit,QPushButton,QMainWindow,QVBoxLayout,QHBoxLayout,QComboBox
from PyQt5.QtSerialPort import QSerialPortInfo,QSerialPort
from PyQt5.QtWidgets import QMainWindow, QWidget
import os
import time
import socket
import sys
import time
import struct
import logging
import serial.tools.list_ports
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 


#define Baud115200       CBR_115200
cliv=0
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.listSerialPorts()


    def listSerialPorts(self):
        serialPortInfo=QSerialPortInfo()
        for serialPort in serialPortInfo.availablePorts():
            self.comboSeriPortList.addItem(serialPort.portName())

    def portDisconnect(self):
        if self.serialPort.isOpen():
            self.serialPort.close()
            self.pushButtonConnect.setEnabled(True)
            self.pushButtonDisconnect.setEnabled(False)
    def abc(self):
          
        number1 = 0
        number2 = 2000
        data = []
        for i in range (0,20):
            read_data = ppk2_test.get_data()
            if read_data != b'':
                samples = ppk2_test.get_samples(read_data)
                print(f"#Average of {len(samples)} samples is: {sum(samples)/len(samples)}uA*")
                number = sum(samples)/len(samples)                      
                if number1 <= number:
                    number1 = number
                if number2 >= number:
                    number2=number
                number=round(number,2)
                number1=round(number1,2)
                number2=round(number2,2)
                data.append( '.SampleCurrent: ' + str(number) + '')
                self.textEditReceiveData.setText("\n".join(data))
                W.send(b'Current:')
                W.send(str(number).encode('utf-8'))
                W.send(b' * Max:')
                W.send(str(number1).encode('utf-8'))
                W.send(b' * Min:')
                W.send(str(number2).encode('utf-8'))
                W.send(b' uA \n')
            time.sleep(0.02)
                            
    def portConnect(self):
        recivedTcp = W.recvfrom(4096)
        if recivedTcp != b'':
            self.counter = 0
            self.abc()
                      
        

    def initUI(self):
        self.serialPort=QSerialPort()
        self.setGeometry(20,50,320,300)
        self.setWindowTitle("SerialPort")
        self.setFixedWidth(400)
        self.setStyleSheet("background: lightgrey")
        vboxana=QVBoxLayout()
        hbox1=QHBoxLayout()
        self.comboSeriPortList=QComboBox()
        hbox1.addWidget(self.comboSeriPortList)
        self.pushButtonConnect=QPushButton("Start")
        self.pushButtonDisconnect=QPushButton("Stop")
        self.pushButtonDisconnect.setEnabled(False)
        hbox1.addWidget(self.pushButtonConnect)
        hbox1.addWidget(self.pushButtonDisconnect)
        self.pushButtonConnect.setStyleSheet("QPushButton"
                             "{"
                             "background-color : lightblue;"
                             "}"
                             "QPushButton::pressed"
                             "{"
                             "background-color : red;"
                             "}"
                             )
        self.pushButtonDisconnect.setStyleSheet("QPushButton"
                             "{"
                             "background-color : lightblue;"
                             "}"
                             "QPushButton::pressed"
                             "{"
                             "background-color : red;"
                             "}"
                             )
        hbox1.addStretch()
        vboxana.addLayout(hbox1)

        hbox2=QHBoxLayout()
        self.textEditReceiveData = QTextEdit(self)
        self.textEditReceiveData.move(50, 210)
        self.textEditReceiveData.resize(540, 200)
        self.textEditReceiveData.setReadOnly(True)
        hbox2.addWidget(self.textEditReceiveData)  
        vboxana.addLayout(hbox2)         

        vboxana.addStretch()
        centralWidget=QWidget()
        centralWidget.setLayout(vboxana)
        self.setCentralWidget(centralWidget)

        self.pushButtonConnect.clicked.connect(self.portConnect)
        self.pushButtonDisconnect.clicked.connect(self.portDisconnect)


class PPK2_Command():
    """Serial command opcodes"""
    NO_OP = 0x00
    TRIGGER_SET = 0x01
    AVG_NUM_SET = 0x02  # no-firmware
    TRIGGER_WINDOW_SET = 0x03
    TRIGGER_INTERVAL_SET = 0x04
    TRIGGER_SINGLE_SET = 0x05
    AVERAGE_START = 0x06
    AVERAGE_STOP = 0x07
    RANGE_SET = 0x08
    LCD_SET = 0x09
    TRIGGER_STOP = 0x0a
    DEVICE_RUNNING_SET = 0x0c
    REGULATOR_SET = 0x0d
    SWITCH_POINT_DOWN = 0x0e
    SWITCH_POINT_UP = 0x0f
    TRIGGER_EXT_TOGGLE = 0x11
    SET_POWER_MODE = 0x11
    RES_USER_SET = 0x12
    SPIKE_FILTERING_ON = 0x15
    SPIKE_FILTERING_OFF = 0x16
    GET_META_DATA = 0x19
    RESET = 0x20
    SET_USER_GAINS = 0x25

class PPK2_Modes():
    """PPK2 measurement modes"""
    AMPERE_MODE = "AMPERE_MODE"
    SOURCE_MODE = "SOURCE_MODE"

class PPK2_API():
    def __init__(self, port):
        self.ser = None
        self.ser = serial.Serial(port)
        self.ser.baudrate = 115200

        self.modifiers = {
            "Calibrated": None,
            "R": {"0": 1031.64, "1": 101.65, "2": 10.15, "3": 0.94, "4": 0.043},
            "GS": {"0": 1, "1": 1, "2": 1, "3": 1, "4": 1},
            "GI": {"0": 1, "1": 1, "2": 1, "3": 1, "4": 1},
            "O": {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0},
            "S": {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0},
            "I": {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0},
            "UG": {"0": 1, "1": 1, "2": 1, "3": 1, "4": 1},
            "HW": None,
            "IA": None
        }

        self.vdd_low = 800
        self.vdd_high = 5000

        self.current_vdd = None

        self.adc_mult = 1.8 / 163840

        self.MEAS_ADC = self._generate_mask(14, 0)
        self.MEAS_RANGE = self._generate_mask(3, 14)
        self.MEAS_LOGIC = self._generate_mask(8, 24)

        self.mode = None

        self.rolling_avg = None
        self.rolling_avg4 = None
        self.prev_range = None
        self.consecutive_range_samples = 0

        self.spike_filter_alpha = 0.18
        self.spike_filter_alpha5 = 0.06
        self.spike_filter_samples = 3
        self.after_spike = 0

        # adc measurement buffer remainder and len of remainder
        self.remainder = {"sequence": b'', "len": 0}
    def __del__(self):
        """Destructor"""
        try:
            if self.ser:
                self.ser.close()
        except Exception as e:
            logging.error(f"An error occured while closing ppk2_api: {e}")

    def _pack_struct(self, cmd_tuple):
        """Returns packed struct"""
        return struct.pack("B" * len(cmd_tuple), *cmd_tuple)

    def _write_serial(self, cmd_tuple):
        """Writes cmd bytes to serial"""
        try:
            cmd_packed = self._pack_struct(cmd_tuple)
            self.ser.write(cmd_packed)
        except Exception as e:
            logging.error(f"An error occured when writing to serial port: {e}")

    def _twos_comp(self, val):
        """Compute the 2's complement of int32 value"""
        if (val & (1 << (32 - 1))) != 0:
            val = val - (1 << 32)  # compute negative value
        return val

    def _convert_source_voltage(self, mV):
        """Convert input voltage to device command"""
        # minimal possible mV is 800
        if mV < self.vdd_low:
            mV = self.vdd_low

        # maximal possible mV is 5000
        if mV > self.vdd_high:
            mV = self.vdd_high

        offset = 32
        # get difference to baseline (the baseline is 800mV but the initial offset is 32)
        diff_to_baseline = mV - self.vdd_low + offset
        base_b_1 = 3
        base_b_2 = 0  # is actually 32 - compensated with above offset

        # get the number of times we have to increase the first byte of the command
        ratio = int(diff_to_baseline / 256)
        remainder = diff_to_baseline % 256  # get the remainder for byte 2

        set_b_1 = base_b_1 + ratio
        set_b_2 = base_b_2 + remainder

        return set_b_1, set_b_2

    def _read_metadata(self):
        """Read metadata"""
        # try to get metadata from device
        for _ in range(0, 5):
            # it appears the second reading is the metadata
            read = self.ser.read(self.ser.in_waiting)
            time.sleep(0.1)

            # TODO add a read_until serial read function with a timeout
            if read != b'' and "END" in read.decode("utf-8"):
                return read.decode("utf-8")

    def _parse_metadata(self, metadata):
        """Parse metadata and store it to modifiers"""
        # TODO handle more robustly
        try:
            data_split = [row.split(": ") for row in metadata.split("\n")]

            for key in self.modifiers.keys():
                for data_pair in data_split:
                    if key == data_pair[0]:
                        self.modifiers[key] = data_pair[1]
                    for ind in range(0, 5):
                        if key+str(ind) == data_pair[0]:
                            if "R" in data_pair[0]:
                                # problem on some PPK2s with wrong calibration values - this doesn't fix it
                                if float(data_pair[1]) != 0:
                                    self.modifiers[key][str(ind)] = float(
                                        data_pair[1])
                            else:
                                self.modifiers[key][str(ind)] = float(
                                    data_pair[1])
            return True
        except Exception as e:
            # if exception triggers serial port is probably not correct
            return None

    def _generate_mask(self, bits, pos):
        pos = pos
        mask = ((2**bits-1) << pos)
        mask = self._twos_comp(mask)
        return {"mask": mask, "pos": pos}

    def _get_masked_value(self, value, meas):
        masked_value = (value & meas["mask"]) >> meas["pos"]
        if meas["pos"] == 24:
            if masked_value == 255:
                masked_value = -1
        return masked_value

    def _handle_raw_data(self, adc_value):
        """Convert raw value to analog value"""
        try:
            current_measurement_range = min(self._get_masked_value(
                adc_value, self.MEAS_RANGE), 4)  # 5 is the number of parameters
            adc_result = self._get_masked_value(adc_value, self.MEAS_ADC) * 4
            bits = self._get_masked_value(adc_value, self.MEAS_LOGIC)
            analog_value = self.get_adc_result(
                current_measurement_range, adc_result) * 10**6
            return analog_value
        except Exception as e:
            print("Measurement outside of range!")
            return None

    @staticmethod
    def list_devices():
        
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        if os.name == 'nt':
            devices = [port.device for port in ports if port.description.startswith("nRF Connect USB CDC ACM")]
        else:
            devices = [port.device for port in ports if port.product == 'PPK2']
        return devices

    def get_data(self):
        """Return readings of one sampling period"""
        sampling_data = self.ser.read(self.ser.in_waiting)
        return sampling_data

    def get_modifiers(self):
        """Gets and sets modifiers from device memory"""
        self._write_serial((PPK2_Command.GET_META_DATA, ))
        metadata = self._read_metadata()
        ret = self._parse_metadata(metadata)
        return ret

    def start_measuring(self):
        """Start continuous measurement"""
        if not self.current_vdd:
            if self.mode == PPK2_Modes.SOURCE_MODE:
                raise Exception("Output voltage not set!")
            if self.mode == PPK2_Modes.AMPERE_MODE:
                raise Exception("Input voltage not set!")

        self._write_serial((PPK2_Command.AVERAGE_START, ))

    def stop_measuring(self):
        """Stop continuous measurement"""
        self._write_serial((PPK2_Command.AVERAGE_STOP, ))

    def set_source_voltage(self, mV):
        """Inits device - based on observation only REGULATOR_SET is the command. 
        The other two values correspond to the voltage level.

        800mV is the lowest setting - [3,32] - the values then increase linearly
        """
        b_1, b_2 = self._convert_source_voltage(mV)
        self._write_serial((PPK2_Command.REGULATOR_SET, b_1, b_2))
        self.current_vdd = mV

    def toggle_DUT_power(self, state):
        """Toggle DUT power based on parameter"""
        if state == "ON":
            self._write_serial(
                (PPK2_Command.DEVICE_RUNNING_SET, PPK2_Command.TRIGGER_SET))  # 12,1

        if state == "OFF":
            self._write_serial(
                (PPK2_Command.DEVICE_RUNNING_SET, PPK2_Command.NO_OP))  # 12,0

    def use_ampere_meter(self):
        """Configure device to use ampere meter"""
        self.mode = PPK2_Modes.AMPERE_MODE
        self._write_serial((PPK2_Command.SET_POWER_MODE,
                            PPK2_Command.TRIGGER_SET))  # 17,1

    def use_source_meter(self):
        """Configure device to use source meter"""
        self.mode = PPK2_Modes.SOURCE_MODE
        self._write_serial((PPK2_Command.SET_POWER_MODE,
                            PPK2_Command.AVG_NUM_SET))  # 17,2

    def get_adc_result(self, current_range, adc_value):
        """Get result of adc conversion"""
        current_range = str(current_range)
        result_without_gain = (adc_value - self.modifiers["O"][current_range]) * (
            self.adc_mult / self.modifiers["R"][current_range])
        adc = self.modifiers["UG"][current_range] * (result_without_gain * (self.modifiers["GS"][current_range] * result_without_gain + self.modifiers["GI"][current_range]) + (
            self.modifiers["S"][current_range] * (self.current_vdd / 1000) + self.modifiers["I"][current_range]))

        prev_rolling_avg = self.rolling_avg
        prev_rolling_avg4 = self.rolling_avg4

        # spike filtering / rolling average
        if self.rolling_avg is None:
            self.rolling_avg = adc
        else:
            self.rolling_avg = self.spike_filter_alpha * adc + (1 - self.spike_filter_alpha) * self.rolling_avg
        
        if self.rolling_avg4 is None:
            self.rolling_avg4 = adc
        else:
            self.rolling_avg4 = self.spike_filter_alpha5 * adc + (1 - self.spike_filter_alpha5) * self.rolling_avg4

        if self.prev_range is None:
            self.prev_range = current_range

        if self.prev_range != current_range or self.after_spike > 0:
            if self.prev_range != current_range:
                self.consecutive_range_samples = 0
                self.after_spike = self.spike_filter_samples
            else:
                self.consecutive_range_samples += 1

            if current_range == "4":
                if self.consecutive_range_samples < 2:
                    self.rolling_avg = prev_rolling_avg
                    self.rolling_avg4 = prev_rolling_avg4
                adc = self.rolling_avg4
            else:
                adc = self.rolling_avg
            
            self.after_spike -= 1

        self.prev_range = current_range
        return adc

    def _digital_to_analog(self, adc_value):
        """Convert discrete value to analog value"""
        return int.from_bytes(adc_value, byteorder="little", signed=False)  # convert reading to analog value

    def get_samples(self, buf):
        """
        Returns list of samples read in one sampling period.
        The number of sampled values depends on the delay between serial reads.
        Manipulation of samples is left to the user.
        See example for more info.
        """

        sample_size = 4  # one analog value is 4 bytes in size
        offset = self.remainder["len"]
        samples = []

        first_reading = (
            self.remainder["sequence"] + buf[0:sample_size-offset])[:4]
        adc_val = self._digital_to_analog(first_reading)
        measurement = self._handle_raw_data(adc_val)
        if measurement is not None:
            samples.append(measurement)

        offset = sample_size - offset

        while offset <= len(buf) - sample_size:
            next_val = buf[offset:offset + sample_size]
            offset += sample_size
            adc_val = self._digital_to_analog(next_val)
            measurement = self._handle_raw_data(adc_val)
            if measurement is not None:
                samples.append(measurement)

        self.remainder["sequence"] = buf[offset:len(buf)]
        self.remainder["len"] = len(buf)-offset

        return samples  # return list of samples, handle those lists in PPK2 API wrapper





host = socket.gethostname()
port = 12345                   # The same port as used by the server
W = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
W.connect((host, port))    

ppk2s_connected = PPK2_API.list_devices()
if(len(ppk2s_connected) == 1):
    ppk2_port = ppk2s_connected[0]
    print(f'Found PPK2 at {ppk2_port}')
else:
    print(f'Too many connected PPK2\'s: {ppk2s_connected}')
    exit()

    """Initiliazing Power Profiler Kit|| Mode """



ppk2_test = PPK2_API("dev\ttpyUSB0")  # Write your own serialPortserial port will be different for you
ppk2_test.get_modifiers()
ppk2_test.use_ampere_meter()    #you can change the measurement mod by changing this section
ppk2_test.set_source_voltage(3300)  # set source voltage in mV
ppk2_test.toggle_DUT_power("ON")  # disable DUT power
ppk2_test.start_measuring()  # start measuring

    # measurements are a constant stream of bytes
    # the number of measurements in one sampling period depends on the wait between serial reads
    # it appears the maximum number of bytes received is 1024
    # the sampling rate of the PPK2 is 100 samples per millisecond
    #def getValues():
    #ser.write(b'g')
        #arduinoData = ser.readline().decode().split('\r\n')
        
app=QApplication(sys.argv)
window=MainWindow()
window.show()
app.exec_()                
sys.exit() //app.setActiveWindow

    #samples = ppk2_test.get_samples(read_data)
    #number = sum(samples)/len(samples)
    #MainWindow.portConnect(str(number).encode('utf-16'))        

