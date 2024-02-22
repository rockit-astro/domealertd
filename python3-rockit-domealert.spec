Name:           python3-rockit-domealert
Version:        %{_version}
Release:        1
License:        GPL3
Summary:        Common backend code for the Domealert daemons.
Url:            https://github.com/rockit-astro/vaisalad
BuildArch:      noarch
BuildRequires:  python3-devel
Requires:       python3-jsonschema python3-rpi.gpio python3-serial

%description

%prep
rsync -av --exclude=build --exclude=.git --exclude=.github .. .

%generate_buildrequires
%pyproject_buildrequires -R

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files rockit

%files -f %{pyproject_files}
