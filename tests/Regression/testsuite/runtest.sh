#!/bin/bash
# vim: dict+=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /tools/annobin/Regression/testsuite
#   Description: testsuite
#   Author: Martin Cermak <mcermak@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2018 Red Hat, Inc.
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

PACKAGE="${PACKAGE:-$(rpm -qf --queryformat=%{name} $(man -w annobin))}"
export PACKAGE

GCC="${GCC:-$(which gcc)}"


rlJournalStart
    rlPhaseStartSetup
        rlLogInfo "PACKAGES=$PACKAGES"
        rlLogInfo "REQUIRES=$REQUIRES"
        rlLogInfo "COLLECTIONS=$COLLECTIONS"
        rlLogInfo "X_SCLS=$X_SCLS"
        rlLogInfo "GCC=$GCC"

        # In case more than one devtoolset- or gcc-toolset -build package is
        # installed (they can co-exist from the packaging persp, but their
        # coexistence causes unexpected results with rpm macros), then we have
        # a mess of defined rpm macros coming e.g. from
        # /etc/rpm/macros.gcc-toolset-10-config
        # /etc/rpm/macros.gcc-toolset-9-config etc.  To have just the needed
        # macros (respective to given SCL under test) defined without
        # uninstalling unneeded RPMs, we'll need an override mechanism. The
        # following assumes just one SCL *enabled* (more than one installed),
        # and doesn't care of a (useless) revert:
        echo ${X_SCLS} | fgrep toolset && \
            rlRun "cat /etc/rpm/*${X_SCLS%\ }* > ~/.rpmmacros"

        rlAssertRpm $PACKAGE
        rlRun "TMP=\$(mktemp -d)"
        rlRun "pushd $TMP"

	rlFetchSrcForInstalled $PACKAGE
	rlRun "yum-builddep -y *src.rpm"
	rlRun "rpm --define='_topdir $TMP' -Uvh *src.rpm"
	rlRun "rpmbuild --define='_topdir $TMP' -bc SPECS/annobin.spec"
    rlPhaseEnd

    rlPhaseStartTest
	rlRun "pushd BUILD/annobin-*"
	set -o pipefail
	rlRun "make check |& tee $TMP/check.log"
	rlRun -l "grep '^PASS:' $TMP/check.log" 0
	rlRun -l "grep '^FAIL:' $TMP/check.log" 1
	PASSCOUNT=$(grep '^PASS:' $TMP/check.log | wc -l)
	rlRun "[[ $PASSCOUNT -ge 7 ]]"
    rlPhaseEnd

    rlPhaseStartCleanup
        rlRun "popd"
        rlRun "rm -r $TMP"
    rlPhaseEnd
rlJournalPrintText
rlJournalEnd
