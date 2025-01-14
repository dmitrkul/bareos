#!/usr/bin/env python
# -*- coding: utf-8 -*-
# BAREOS - Backup Archiving REcovery Open Sourced
#
# Copyright (C) 2014-2014 Bareos GmbH & Co. KG
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of version three of the GNU Affero General Public
# License as published by the Free Software Foundation, which is
# listed in the file LICENSE.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
# Author: Maik Aussendorf
#
# Baseclass for Bareos python plugins
# Functions taken and adapted from bareos-dir.py

import bareosdir
from bareosdir import bDirEventType, bDirVariable, bRCs
import time


class BareosDirPluginBaseclass(object):

    """ Bareos DIR python plugin base class """

    def __init__(self, plugindef):
        bareosdir.DebugMessage(
            100, "Constructor called in module %s\n" % (__name__)
        )
        events = []

        events.append(bDirEventType[b"bDirEventJobStart"])
        events.append(bDirEventType[b"bDirEventJobEnd"])
        events.append(bDirEventType[b"bDirEventJobInit"])
        events.append(bDirEventType[b"bDirEventJobRun"])
        bareosdir.RegisterEvents(events)

        # get some static Bareos values
        self.jobName = bareosdir.GetValue(bDirVariable[b"bDirVarJobName"])
        self.jobLevel = chr(bareosdir.GetValue(bDirVariable[b"bDirVarLevel"]))
        self.jobType = bareosdir.GetValue(bDirVariable[b"bDirVarType"])
        self.jobId = int(bareosdir.GetValue(bDirVariable[b"bDirVarJobId"]))
        self.jobClient = bareosdir.GetValue(bDirVariable[b"bDirVarClient"])
        self.jobStatus = bareosdir.GetValue(bDirVariable[b"bDirVarJobStatus"])
        self.Priority = bareosdir.GetValue(bDirVariable[b"bDirVarPriority"])

        bareosdir.DebugMessage(
            100,
            "JobName = %s - level = %s - type = %s - Id = %s - \
Client = %s - jobStatus = %s - Priority = %s - BareosDirPluginBaseclass\n"
            % (
                self.jobName,
                self.jobLevel,
                self.jobType,
                self.jobId,
                self.jobClient,
                self.jobStatus,
                self.Priority,
            ),
        )

    def __str__(self):
        return "<$%:jobName=%s jobId=%s client=%s>" % (
            self.__class__,
            self.jobName,
            self.jobId,
            self.Client,
        )

    def parse_plugin_definition(self, plugindef):
        """
        Called with the plugin options from the bareos configfiles
        You should overload this method with your own and do option checking
        here, return bRCs['bRC_Error'], if options are not ok
        or better call super.parse_plugin_definition in your own class and
        make sanity check on self.options afterwards
        """
        bareosdir.DebugMessage(
            100, "plugin def parser called with %s\n" % (plugindef)
        )
        # Parse plugin options into a dict
        self.options = dict()
        plugin_options = plugindef.split(":")
        for current_option in plugin_options:
            key, sep, val = current_option.partition("=")
            bareosdir.DebugMessage(100, "key:val = %s:%s" % (key, val))
            if val == "":
                continue
            else:
                self.options[key] = val
        return bRCs[b"bRC_OK"]

    def handle_plugin_event(self, event):
        """
        This method is called for each of the above registered events
        Overload this method to implement your actions for the events,
        You may first call this method in your derived class to get the
        job attributes read and then only adjust where useful.
        """
        if event == bDirEventType[b"bDirEventJobInit"]:
            self.jobInitTime = time.time()
            self.jobStatus = chr(
                bareosdir.GetValue(bDirVariable[b"bDirVarJobStatus"])
            )
            bareosdir.DebugMessage(
                100,
                "bDirEventJobInit event triggered at Unix time %s\n"
                % (self.jobInitTime),
            )

        elif event == bDirEventType[b"bDirEventJobStart"]:
            self.jobStartTime = time.time()
            self.jobStatus = chr(
                bareosdir.GetValue(bDirVariable[b"bDirVarJobStatus"])
            )
            bareosdir.DebugMessage(
                100,
                "bDirEventJobStart event triggered at Unix time %s\n"
                % (self.jobStartTime),
            )

        elif event == bDirEventType[b"bDirEventJobRun"]:
            # Now the jobs starts running, after eventually waiting some time,
            # e.g for other jobs to finish
            self.jobRunTime = time.time()
            bareosdir.DebugMessage(
                100,
                "bDirEventJobRun event triggered at Unix time %s\n" % (self.jobRunTime),
            )

        elif event == bDirEventType[b"bDirEventJobEnd"]:
            self.jobEndTime = time.time()
            bareosdir.DebugMessage(
                100,
                "bDirEventJobEnd event triggered at Unix time %s\n" % (self.jobEndTime),
            )
            self.jobLevel = chr(
                bareosdir.GetValue(bDirVariable[b"bDirVarLevel"])
            )
            self.jobStatus = chr(
                bareosdir.GetValue(bDirVariable[b"bDirVarJobStatus"])
            )
            self.jobErrors = int(
                bareosdir.GetValue(bDirVariable[b"bDirVarJobErrors"])
            )
            self.jobBytes = int(
                bareosdir.GetValue(bDirVariable[b"bDirVarJobBytes"])
            )
            self.jobFiles = int(
                bareosdir.GetValue(bDirVariable[b"bDirVarJobFiles"])
            )
            self.jobNumVols = int(
                bareosdir.GetValue(bDirVariable[b"bDirVarNumVols"])
            )
            self.jobPool = bareosdir.GetValue(bDirVariable[b"bDirVarPool"])
            self.jobStorage = bareosdir.GetValue(
                bDirVariable[b"bDirVarStorage"]
            )
            self.jobMediaType = bareosdir.GetValue(
                bDirVariable[b"bDirVarMediaType"]
            )

            self.jobTotalTime = self.jobEndTime - self.jobInitTime
            self.jobRunningTime = self.jobEndTime - self.jobRunTime
            self.throughput = 0
            if self.jobRunningTime > 0:
                self.throughput = self.jobBytes / self.jobRunningTime

        return bRCs[b"bRC_OK"]


# vim: ts=4 tabstop=4 expandtab shiftwidth=4 softtabstop=4
