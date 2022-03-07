#!/bin/bash
# vim: dict+=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /tools/annobin/Regression/segv-when-processing-multiple-params-incl-symlink
#   Description: segv-when-processing-multiple-params-incl-symlink
#   Author: Martin Cermak <mcermak@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2021 Red Hat, Inc.
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
        # This tries to test https://bugzilla.redhat.com/show_bug.cgi?id=1988715#c0
        # keeping in mind that annocheck will evolve in the future, along its
        # rules / policies, and the surrounding OS will evolve too.  This test
        # shouldn't report false positives though.
        rlRun "rpm -qf /usr/lib64/libstdc++.so*"
        rlRun "annocheck --follow-links --skip-all /usr/lib64/libstdc++.so*"
        rlRun "annocheck --ignore-links --skip-all /usr/lib64/libstdc++.so*"
   rlPhaseEnd
rlJournalPrintText
rlJournalEnd
