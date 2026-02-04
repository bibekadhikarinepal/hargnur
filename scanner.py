#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import signal
from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import uhd
from gnuradio import gr
from gnuradio.filter import firdes
import sip

class gnr_scanner(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "5G B210 Scanner")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("5G B210 Visual Scanner")
        
        # ------------------------------------------------------------------
        # Variables
        # ------------------------------------------------------------------
        self.samp_rate = 20000000  # 20 MHz (Wide enough for 5G chunks)
        self.gain = 50             # Start Gain
        self.freq = 2536000000     # Start Frequency (Band n41)

        # ------------------------------------------------------------------
        # Interface (Layout)
        # ------------------------------------------------------------------
        self.layout = Qt.QVBoxLayout(self)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.layout.addLayout(self.top_scroll_layout)
        self.setLayout(self.layout)

        # ------------------------------------------------------------------
        # Blocks
        # ------------------------------------------------------------------
        
        # 1. The UHD USRP Source (The B210)
        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0.set_center_freq(self.freq, 0)
        self.uhd_usrp_source_0.set_gain(self.gain, 0)
        self.uhd_usrp_source_0.set_antenna('RX2', 0) # Ensures using RX2 port
        self.uhd_usrp_source_0.set_bandwidth(self.samp_rate, 0)

        # 2. The Frequency Sink (The Visual Display)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, # FFT Size
            firdes.WIN_BLACKMAN_hARRIS, # Window Type
            self.freq, # Center Freq
            self.samp_rate, # Bandwidth
            "5G Spectrum", # Name
            1 # Number of Inputs
        )
        
        # Configure Sink Visuals
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, -10)
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(True)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False) # Hides internal control panel
        
        # Add the Sink to the layout
        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_scroll_layout.addWidget(self._qtgui_freq_sink_x_0_win)

        # 3. GUI Sliders (To tune while running)
        
        # Frequency Slider
        self._freq_layout = Qt.QHBoxLayout()
        self._freq_label = Qt.QLabel("Frequency (Hz)")
        self._freq_slider = Qt.QSlider(Qt.Qt.Horizontal)
        self._freq_slider.setRange(70, 6000) # MHz range
        self._freq_slider.setValue(2536)
        self._freq_slider.valueChanged.connect(self.set_freq_slider)
        self._freq_layout.addWidget(self._freq_label)
        self._freq_layout.addWidget(self._freq_slider)
        self.layout.addLayout(self._freq_layout)
        
        # Gain Slider
        self._gain_layout = Qt.QHBoxLayout()
        self._gain_label = Qt.QLabel("Gain (dB)")
        self._gain_slider = Qt.QSlider(Qt.Qt.Horizontal)
        self._gain_slider.setRange(0, 76)
        self._gain_slider.setValue(50)
        self._gain_slider.valueChanged.connect(self.set_gain_slider)
        self._gain_layout.addWidget(self._gain_label)
        self._gain_layout.addWidget(self._gain_slider)
        self.layout.addLayout(self._gain_layout)

        # ------------------------------------------------------------------
        # Connections
        # ------------------------------------------------------------------
        self.connect((self.uhd_usrp_source_0, 0), (self.qtgui_freq_sink_x_0, 0))

    # ----------------------------------------------------------------------
    # Callbacks (To update radio when sliders move)
    # ----------------------------------------------------------------------
    def set_freq_slider(self, val):
        # Slider is in MHz, convert to Hz
        new_freq = val * 1000000
        self.freq = new_freq
        self.uhd_usrp_source_0.set_center_freq(self.freq, 0)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq, self.samp_rate)

    def set_gain_slider(self, val):
        self.gain = val
        self.uhd_usrp_source_0.set_gain(self.gain, 0)

def main(top_block_cls=gnr_scanner, options=None):
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print("Error: failed to enable real-time scheduling.")

    qapp = Qt.QApplication(sys.argv)
    tb = top_block_cls()
    tb.start()
    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    qapp.exec_()

if __name__ == '__main__':
    main()