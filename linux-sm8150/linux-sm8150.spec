%undefine        _debugsource_packages
%global tag      6.16
Version:         6.16.0
Release:         0.sm8150%{?dist}
ExclusiveArch:   aarch64
Name:            kernel
Summary:         linux-sm8150 kernel
License:         GPLv2
URL:             https://gitlab.com/sm8150-mainline/linux
Source0:         %{url}/-/archive/sm8150/%{tag}/linux-sm8150-%{tag}.tar.gz
Source1:         extra-sm8150.config

BuildRequires:   bc bison dwarves diffutils elfutils-devel findutils gcc gcc-c++ git-core hmaccalc hostname make openssl-devel perl-interpreter rsync tar which flex bzip2 xz zstd python3 python3-devel python3-pyyaml rust rust-src bindgen rustfmt clippy opencsd-devel net-tools

Provides:        kernel               = %{version}-%{release}
Provides:        kernel-core          = %{version}-%{release}
Provides:        kernel-devel         = %{version}-%{release}
Provides:        kernel-headers       = %{version}-%{release}
Provides:        kernel-modules       = %{version}-%{release}
Provides:        kernel-modules-core  = %{version}-%{release}

%global uname_r %{version}-%{release}.%{_target_cpu}

%description
Mainline kernel for sm8150 (qcom snapdragon 855/860) devices.

%prep
%autosetup -n linux-sm8150-%{tag}

make defconfig sm8150.config

%build
sed -i '/^CONFIG_LOCALVERSION=/d' .config
cat %{SOURCE1} >> .config
rm -f localversion*

make olddefconfig
make EXTRAVERSION="-%{release}.%{_target_cpu}" LOCALVERSION= -j%{?_smp_build_ncpus} Image.gz modules dtbs

%install
make EXTRAVERSION="-%{release}.%{_target_cpu}" LOCALVERSION= \
     INSTALL_PATH=%{buildroot}/usr/lib/modules/%{uname_r} \
     INSTALL_MOD_PATH=%{buildroot}/usr \
     INSTALL_HDR_PATH=%{buildroot}/usr \
     modules_install headers_install install

install -Dm644 System.map %{buildroot}/usr/lib/modules/%{uname_r}/System.map
install -Dm644 .config    %{buildroot}/usr/lib/modules/%{uname_r}/config

install -d %{buildroot}/usr/lib/modules/%{uname_r}/dtb/qcom
install -Dm644 arch/arm64/boot/dts/qcom/sm8150-xiaomi-nabu.dtb %{buildroot}/usr/lib/modules/%{uname_r}/devicetree
install -d %{buildroot}/usr/lib/kernel

install -Dm644 arch/arm64/boot/Image %{buildroot}/usr/lib/modules/%{uname_r}/vmlinuz
install -d %{buildroot}/boot
ln -sr %{buildroot}/usr/lib/modules/%{uname_r}/vmlinuz %{buildroot}/boot/vmlinuz-%{uname_r}
install -d %{buildroot}/usr/lib/ostree-boot
ln -s ../modules/%{uname_r}/vmlinuz %{buildroot}/usr/lib/ostree-boot/vmlinuz-%{uname_r}
ln -s ../modules/%{uname_r}/initramfs.img %{buildroot}/usr/lib/ostree-boot/initramfs-%{uname_r}.img

%files
/boot/vmlinuz-%{uname_r}
/usr/include
/usr/lib/modules/%{uname_r}
/usr/lib/ostree-boot/vmlinuz-%{uname_r}
/usr/lib/ostree-boot/initramfs-%{uname_r}.img
/usr/lib/modules/%{uname_r}/devicetree

%posttrans
set -e
uname_r=%{uname_r}

depmod -a "${uname_r}"

dracut -v --force "/usr/lib/modules/${uname_r}/initramfs.img" "${uname_r}"

ln -sf "../modules/${uname_r}/initramfs.img" "/usr/lib/ostree-boot/initramfs-${uname_r}.img"

kernel-install add "${uname_r}" "/usr/lib/modules/${uname_r}/vmlinuz" "/usr/lib/modules/${uname_r}/initramfs.img"

%postun
if [ "$1" -eq 0 ] ; then
    kernel-install remove %{uname_r}
fi

%changelog
* Fri Jul 25 2025 gmanka 6.16.0
- update to 6.16.0
