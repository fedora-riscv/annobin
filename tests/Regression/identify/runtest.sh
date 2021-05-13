#!/bin/bash
# vim: dict+=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /tools/annobin/Regression/identify
#   Description: identify
#   Author: Martin Cermak <mcermak@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2019 Red Hat, Inc.
#
#   This program is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 2 of
#   the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE.  See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see http://www.gnu.org/licenses/.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Include Beaker environment
. /usr/share/beakerlib/beakerlib.sh || exit 1

PACKAGE="annobin"

rlJournalStart
    rlPhaseStartTest
        rlRun "rpm -qa | fgrep -e redhat-rpm-config -e gcc -e annobin -e binutils | sort"
        rlRun "tool_v=$(annocheck --version | awk '/^annocheck: Version/ {print $3}')"
        rlRun "__RPM=$(rpm --queryformat='%{name}\n' -qf $(man -w annobin))"
        rlRun "rpm_v=$(rpm -q --queryformat='%{version}\n' $__RPM)"
        # Following fails for annobin-8.89-2.el8
        rlRun "[[ "x${tool_v}" == "x${rpm_v}." ]]"
    rlPhaseEnd
rlJournalPrintText
rlJournalEnd
