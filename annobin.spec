
# Do not build the annobin plugin with annotation enabled.
# This is because if we are bootstrapping a new build environment we can have
# a new version of gcc installed, but without a new of annobin installed.
# (ie we are building the new version of annobin to go with the new version
# of gcc).  If the *old* annobin plugin is used whilst building this new
# version, the old plugin will complain that version of gcc for which it
# was built is different from the version of gcc that is now being used, and
# then it will abort.
%undefine _annotated_build

Name:    annobin
Summary: Binary annotation plugin for GCC
Version: 5.11
Release: 1%{?dist}

License: GPLv3+
URL:     https://fedoraproject.org/wiki/Toolchain/Watermark

# Use "--without tests" to disable the testsuite.  The default is to run them.
%bcond_without tests

# Set this to zero to disable the requirement for a specific version of gcc.
# This should only be needed if there is some kind of problem with the version
# checking logic.
%global with_hard_gcc_version_requirement 1

#---------------------------------------------------------------------------------
Source:  https://nickc.fedorapeople.org/annobin-%{version}.tar.xz
# For the latest sources use:  git clone git://sourceware.org/git/annobin.git

# Insert patches here, if needed.
# Patch01: annobin-xxx.patch


Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info

BuildRequires: gcc-plugin-devel pkgconfig coreutils info

%description
A plugin for GCC that records extra information in the files that it compiles,
and a set of scripts that analyze the recorded information.  These scripts can
determine things ABI clashes in compiled binaries, or the absence of required
hardening options.

Note - the plugin is enabled in gcc builds via flags provided by the
redhat-rpm-macros package, and the analysis tools rely upon the readelf program
from the binutils package.

#---------------------------------------------------------------------------------
%if %{with tests}

%package tests
Summary: Test scripts and binaries for checking the behaviour and output of the annobin plugin

%description tests
Provides a means to test the generation of annotated binaries and the parsing
of the resulting files.
# FIXME: Does not actually do this yet...

%endif
#---------------------------------------------------------------------------------

%global ANNOBIN_PLUGIN_DIR %(gcc --print-file-name=plugin)

# [Stolen from gcc-python-plugin]
# GCC will only load plugins that were built against exactly that build of GCC
# We thus need to embed the exact GCC version as a requirement within the
# metadata.
#
# Define "gcc_vr", a variable to hold the VERSION-RELEASE string for the gcc
# we are being built against.
#
# Unfortunately, we can't simply run:
#   rpm -q --qf="%%{version}-%%{release}"
# to determine this, as there's no guarantee of a sane rpm database within
# the chroots created by our build system
#
# So we instead query the version from gcc's output.
#
# gcc.spec has:
#   Version: %%{gcc_version}
#   Release: %%{gcc_release}%%{?dist}
#   ...snip...
#   echo 'Red Hat %%{version}-%%{gcc_release}' > gcc/DEV-PHASE
#
# So, given this output:
#
#   $ gcc --version
#   gcc (GCC) 4.6.1 20110908 (Red Hat 4.6.1-9)
#   Copyright (C) 2011 Free Software Foundation, Inc.
#   This is free software; see the source for copying conditions.  There is NO
#   warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# we can scrape out the "4.6.1" from the version line.
#
# The following implements the above:
#
# Note - gawk will emit a warning message saying:
#
#  gawk: cmd. line:1: warning: escape sequence `\)' treated as plain `)'
#
# I have not been able to work out how to remove this message, but still provide
# sufficient escaping for the command line to survive intact as it is passed
# down through the sub-shell.

%global gcc_vr %(gcc --version | gawk 'match (\$0, ".*Red Hat \([^\\)-]*\)", a) { print a[1]; }')

# This is a gcc plugin, hence gcc is required.
%if %{with_hard_gcc_version_requirement}
Requires: gcc == %{gcc_vr}
BuildRequires: gcc == %{gcc_vr}
%else
Requires: gcc
%endif

#---------------------------------------------------------------------------------

%prep
%autosetup -p1

# The plugin has to be configured with the same arcane configure
# scripts used by gcc.  Hence we must not allow the Fedora build
# system to regenerate any of the configure files.
touch aclocal.m4 plugin/config.h.in
touch configure */configure Makefile.in */Makefile.in
# Similarly we do not want to rebuild the documentation.
touch doc/annobin.info

#---------------------------------------------------------------------------------

%build
%configure --quiet --with-gcc-plugin-dir=%{ANNOBIN_PLUGIN_DIR}
%make_build
# Rebuild the plugin, this time using the plugin itself!  This
# ensures that the plugin works, and that it contains annotations
# of its own.  This could mean that we end up with a plugin with
# double annotations in it.  (If the build system enables annotations
# for plugins by default).  I have not tested this yet, but I think
# that it should be OK.
cp plugin/.libs/annobin.so.0.0.0 %{_tmppath}/tmp-annobin.so
make -C plugin clean
make -C plugin CXXFLAGS="%{optflags} -fplugin=%{_tmppath}/tmp-annobin.so"
rm %{_tmppath}/tmp-annobin.so

#---------------------------------------------------------------------------------

%install
%make_install
%{__rm} -f %{buildroot}%{_infodir}/dir

#---------------------------------------------------------------------------------

%if %{with tests}
%check
make check
%endif

#---------------------------------------------------------------------------------

%post
/sbin/install-info %{_infodir}/annobin.info.gz %{_infodir} >/dev/null 2>&1 || :
exit 0

#---------------------------------------------------------------------------------

%preun
if [ $1 = 0 ]; then
   /sbin/install-info --delete %{_infodir}/annobin.info.gz %{_infodir} >/dev/null 2>&1|| :
fi
exit 0

#---------------------------------------------------------------------------------

%files
%{ANNOBIN_PLUGIN_DIR}
%{_bindir}/built-by
%{_bindir}/check-abi
%{_bindir}/hardened
%{_bindir}/run-on-binaries-in
%license COPYING3 LICENSE
%exclude %{_datadir}/doc/annobin-plugin/COPYING3
%exclude %{_datadir}/doc/annobin-plugin/LICENSE
%doc %{_datadir}/doc/annobin-plugin/annotation.proposal.txt
%doc %{_infodir}/annobin.info.gz
%doc %{_mandir}/man1/annobin.1.gz
%doc %{_mandir}/man1/built-by.1.gz
%doc %{_mandir}/man1/check-abi.1.gz
%doc %{_mandir}/man1/hardened.1.gz
%doc %{_mandir}/man1/run-on-binaries.1.gz

#---------------------------------------------------------------------------------

%changelog
* Fri Jun 01 2018 Nick Clifton <nickc@redhat.com> - 5.11-1
- Do not use the SHF_GNU_BUILD_NOTE section flag.

* Thu May 31 2018 Nick Clifton <nickc@redhat.com> - 5.10-1
- Remove .sh extension from shell scripts.

* Wed May 30 2018 Nick Clifton <nickc@redhat.com> - 5.9-1
- Record the setting of the -mstackrealign option for i686 binaries.

* Mon May 14 2018 Nick Clifton <nickc@redhat.com> - 5.8-1
- Hide the annobin start of file symbol.

* Tue May 08 2018 Nick Clifton <nickc@redhat.com> - 5.7-1
- Fix script bug in hardended.sh.  (Thanks to: Stefan Sørensen <stefan.sorensen@spectralink.com>)

* Thu May 03 2018 Nick Clifton <nickc@redhat.com> - 5.6-3
- Version number bump so that the plugin can be rebuilt with the latest version of GCC.

* Mon Apr 30 2018 Nick Clifton <nickc@redhat.com> - 5.6-2
- Rebuild the plugin with the newly created plugin enabled.  (#1573082)

* Mon Apr 30 2018 Nick Clifton <nickc@redhat.com> - 5.6-1
- Skip the isa_flags check in the ABI test because the crt[in].o files are compiled with different flags from the test files.

* Fri Apr 20 2018 Nick Clifton <nickc@redhat.com> - 5.3-1
- Add manual pages for annobin and the scripts.

* Tue Apr 03 2018 Nick Clifton <nickc@redhat.com> - 5.2-1
- Do not record a stack protection setting of -1.  (#1563141)

* Tue Mar 20 2018 Nick Clifton <nickc@redhat.com> - 5.1-1
- Do not complain about a dwarf_version value of -1.  (#1557511)

* Thu Mar 15 2018 Nick Clifton <nickc@redhat.com> - 5.0-1
- Bias file start symbols by 2 in order to avoid them confused with function symbols.  (#1554332)
- Version jump is to sync the version number with the annobin plugins internal version number.

* Mon Mar 12 2018 Nick Clifton <nickc@redhat.com> - 3.6-1
- Add --ignore-gaps option to check-abi.sh script.
- Use this option in the abi-test check.
- Tweak hardening test to skip pic and stack protection checks.

* Tue Mar 06 2018 Nick Clifton <nickc@redhat.com> - 3.5-1
- Handle functions with specific assembler names.  (#1552018)

* Fri Feb 23 2018 Nick Clifton <nickc@redhat.com> - 3.4-2
- Add an explicit requirement on the version of gcc used to built the plugin.  (#1547260)

* Fri Feb 09 2018 Nick Clifton <nickc@redhat.com> - 3.4-1
- Change type and size of symbols to STT_NOTYPE/0 so that they do not confuse GDB.  (#1539664)
- Add run-on-binaries-in.sh script to allow the other scripts to be run over a repository.

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Jan 30 2018 Nick Clifton <nickc@redhat.com> - 3.3-1
- Rebase on 3.3 release, which adds support for recording -mcet and -fcf-protection.

* Mon Jan 29 2018 Florian Weimer <fweimer@redhat.com> - 3.2-3
- Rebuild for GCC 8

* Fri Jan 26 2018 Nick Clifton <nickc@redhat.com> - 3.2-2
- Fix the installation of the annobin.info file.

* Fri Jan 26 2018 Nick Clifton <nickc@redhat.com> - 3.2-1
- Rebase on 3.2 release, which now contains documentation!

* Fri Jan 26 2018 Richard W.M. Jones <rjones@redhat.com> - 3.1-3
- Rebuild against GCC 7.3.1.

* Tue Jan 16 2018 Nick Clifton <nickc@redhat.com> - 3.1-2
- Add --with-gcc-plugin-dir option to the configure command line.

* Thu Jan 04 2018 Nick Clifton <nickc@redhat.com> - 3.1-1
- Rebase on version 3.1 sources.

* Mon Dec 11 2017 Nick Clifton <nickc@redhat.com> - 2.5.1-5
- Do not generate notes when there is no output file.  (#1523875)

* Fri Dec 08 2017 Nick Clifton <nickc@redhat.com> - 2.5.1-4
- Invent an input filename when reading from a pipe.  (#1523401)

* Thu Nov 30 2017 Florian Weimer <fweimer@redhat.com> - 2.5.1-3
- Use DECL_ASSEMBLER_NAME for symbol references (#1519165)

* Tue Oct 03 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 2.5.1-2
- Cleanups in spec

* Tue Sep 26 2017 Nick Clifton <nickc@redhat.com> - 2.5.1-1
- Touch the auto-generated files in order to stop them from being regenerated.

* Tue Sep 26 2017 Nick Clifton <nickc@redhat.com> - 2.5-2
- Stop the plugin complaining about compiler datestamp mismatches.

* Thu Sep 21 2017 Nick Clifton <nickc@redhat.com> - 2.4-1
- Tweak tests so that they will run on older machines.

* Thu Sep 21 2017 Nick Clifton <nickc@redhat.com> - 2.3-1
- Add annobin-tests subpackage containing some preliminary tests.
- Remove link-time test for unsuported targets.

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Mon Jul 31 2017 Florian Weimer <fweimer@redhat.com> - 2.0-2
- Rebuild with binutils fix for ppc64le (#1475636)

* Wed Jun 28 2017 Nick Clifton <nickc@redhat.com> - 2.0-1
- Fixes for problems reported by the package submission review:
   * Add %%license entry to %%file section.
   * Update License and BuildRequires tags.
   * Add Requires tag.
   * Remove %%clean.
   * Add %%check.
   * Clean up the %%changelog.
- Update to use version 2 of the specification and sources.

* Thu May 11 2017 Nick Clifton <nickc@redhat.com> - 1.0-1
- Initial submission.
