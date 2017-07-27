Name:    annobin
Summary: Binary annotation plugin for GCC
Version: 2.0
Release: 1%{?dist}

License: GPLv3, MIT/X11 (config/libcutl.m4, install-sh)
Group:   Development/Tools
URL:     https://fedoraproject.org/wiki/Toolchain/Watermark

Source:  https://nickc.fedorapeople.org/annobin-2.0.tar.xz

# This is a gcc plugin, hence gcc is required.
Requires: gcc

BuildRequires: gcc-plugin-devel pkgconfig

%description
A plugin for GCC that records extra information in the files that it compiles.
This information can be used to analyze the files, and provide the loader
with extra information about the requirements of the loaded file.

%global ANNOBIN_PLUGIN_DIR %(g++ -print-file-name=plugin)

%prep
%autosetup -p1

%build
%configure
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

%files
%{ANNOBIN_PLUGIN_DIR}
%{_bindir}/built-by.sh
%{_bindir}/check-abi.sh
%{_bindir}/hardened.sh
%license COPYING3 LICENSE
%exclude %{_datadir}/doc/annobin-plugin/COPYING3
%exclude %{_datadir}/doc/annobin-plugin/LICENSE
%doc %{_datadir}/doc/annobin-plugin/annotation.proposal.txt

%changelog
* Wed Jun 28 2017 Nick Clifton <nickc@redhat.com> - annobin-2.0-1.fc25
- Fixes for problems reported by the package submission review:
   * Add %%license entry to %%file section.
   * Update License and BuildRequires tags.
   * Add Requires tag.
   * Remove %%clean.
   * Add %%check.
   * Clean up the %%changelog.
- Update to use version 2 of the specification and sources.

* Thu May 11 2017 Nick Clifton <nickc@redhat.com> - annobin-1.0-1.fc25
- Initial submission.
