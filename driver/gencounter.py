#!   /usr/bin/env   python3
#    coding: utf8
'''
Abstract class to define the API for a Frequency Counter/Timer

This API defines the usual commands for a Frequency Counter/Timer:
- Measure Frequency of an input channel
- Measure Period of an input channel
- Measure Time Interval
- Measure Peak-to-Peak input voltage
And some common commands to manage the instrument.

@file
@author Felipe Torres González (torresfelipex1<AT>gmail.com)
@date Created on Nov 3, 2016
@copyright GPL v3
'''

# API for the Frequency Counter/Timer instruments
# Copyright (C) 2016  Felipe Torres González (torresfelipex1<AT>gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import abc
import enum
import logging


__meas_instr__ = "GenCounter"

class Interfaces(enum.Enum) :
    '''
    This class represents the supported interfaces in the instruments.
    '''
    usb      = 0
    usb_acm  = 1
    vxi11    = 2

class GenCounter() :
    '''
    Abstract class to define the API for a Frequency Counter/Timer
    '''
    __metaclass__ = abc.ABCMeta

    ## How many input channels has the instrument
    _nChannels = 2

    ## How many samples take (for supported measures)
    _samples = 1

    ## Time between samples (ms)
    _interval = 1e3

    ## Enable debug output
    _dbg = False

    ## Driver for the communication
    _drv = None

    ## The port used (IP, serial, usbtmc)
    _port = None

    ## The interface used by the driver
    _conn = None

    ## Trigger system saved configuration
    _trigcfg = None


    @abc.abstractmethod
    def __init__(self, interface, port, name=None) :
        '''
        Constructor

        Args:
            interface (Interfaces) : The interface used to communicate with the device
            port (str) : The port used (serial port, IP, ...)
            name (str) : An identifier for the device
        '''

    @abc.abstractmethod
    def open(self) :
        '''
        Method to open the connection with the device
        '''

    @abc.abstractmethod
    def close(self) :
        '''
        Method to close the connection with the device
        '''

    @abc.abstractmethod
    def resetDevice(self) :
        '''
        Method to reset the device
        '''

    @abc.abstractmethod
    def trigLevel(self, cfgstr) :
        '''
        Method to set the trigger level for a channel

        Args:
            cfgstr (str) : A string containing valid params

        The expected params in this method are:
            trig<ch>:<value> Where ch is the channel index in the counter and value could be:
                - A numeric value for the voltage (in V).
                - a<%> The key "a" (auto) followed by a percentage, i.e. a50 for mode auto at 50% of the amplitude for the signal.
        '''

    @abc.abstractmethod
    def freq(self, cfgstr, meas_out) :
        '''
        Method to measure the frequency of the input signal in a channel

        Args:
            cfgstr (str) : A string containing valid params
            meas_out (MeasuredData) : Data container

        The expected params in this method are (optional between <>):
            ch (int) : Index of the channel, (ch:1 or ch:2)
            cou (str) : Input coupling (ac or dc)
            <exp> (str) : Expected frequency value, i.e. 125E6
            <res> (int) : Resolution bits 5 to 15
            <sampl> (int) : How many samples take
        '''

    @abc.abstractmethod
    def period(self, cfgstr, meas_out) :
        '''
        Method to measure the period of the input signal in a channel

        Args:
            ch (int) : Index of the channel
            meas_out (MeasuredData) : Data container
        '''

    @abc.abstractmethod
    def timeInterval(self, cfgstr, meas_out) :
        '''
        Method to measure Time Interval between the input channels

        Args:
            cfgstr (str) : A string containing valid params
            meas_out (MeasuredData) : Data container

        The expected params in this method are:
            ref (int) : The channel used as reference
            ch (int) : The channel to measure the time interval
            (ref:A, ref_chan = 1, other chan = 2; else ref_chan = 2, other chan=1)
            tstamp (str) : Time Stamp: (Y)es or (N)o, (tstamp:Y)
            sampl (int) : Samples number, range 1 - 1000000, (sampl:1000000)
            coup (str) : coupling ac or dc, (coup:dc)
            imp (int or str) : impedance range 50 - 1000000, (imp:1000000)
        '''

    @abc.abstractmethod
    def freqRatio(self, cfgstr, meas_out) :
        '''
        Method to measure Frequncy Ratio of two input channels

        Args:
            cfgstr (str) : A string containing valid params
            meas_out (MeasuredData) : Container for the samples

        The expected params in this method are:
            ref (int) : The channel used as reference
            sampl (int) : Number of samples to be taken
            res (int) : Number of digits of resolution (5 to 15)
        '''

    @abc.abstractmethod
    def pkToPk(self, cfgstr, meas_out) :
        '''
        Method to measure the pk-to-pk amplitude of an input signal

        Args:
            cfgstr (str) : A string containing valid params
            meas_out (MeasuredData) : Data container
        '''

    def parseConfig(self, cfgstr) :
        '''
        Method to parse a configuration string

        Methods defined by this API expect a string containing the
        arguments needed by the methods. The syntax should be:
        <token>:<value> [<token>:<value>]

        This method parses the input string to a dict ready to be
        passed to a method.

        The parseConfig method doesn't filters out any token. The
        other caller method should take only the needed tokens
        from the dict.

        Args:
            cfgstr (str) : A string containing a configuration chain.
        '''
        if cfgstr is None:
            logging.warning("Empty cfg string passed to the Config Parser")
            return ""

        cfgstr = cfgstr.strip()
        cfgdict = {}

        for s in cfgstr.split(" ") :
            if s[0] == " " : continue
            key, val = s.split(":")
            cfgdict[key] = val

        return cfgdict
