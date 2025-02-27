#!/usr/bin/env python3
import argparse
import subprocess
from abc import ABCMeta, abstractmethod
import sys

from pyfastogt import system_info, build_utils
from check_plugins import check_plugins

# Script for building environment on clean machine

if sys.version_info < (3, 5, 0):  # meson limitations
    print('Tried to start script with an unsupported version of Python. build_env requires Python 3.5.0 or greater')
    sys.exit(1)

GLIB_SRC_ROOT = "http://ftp.acc.umu.se/pub/gnome/sources/glib"
GLIB_ARCH_COMP = "xz"
GLIB_ARCH_EXT = "tar." + GLIB_ARCH_COMP

GSTREAMER_SRC_ROOT = "https://gstreamer.freedesktop.org/src/"
GSTREAMER_ARCH_COMP = "xz"
GSTREAMER_ARCH_EXT = "tar." + GSTREAMER_ARCH_COMP

GST_PLUGINS_BASE_SRC_ROOT = GSTREAMER_SRC_ROOT
GST_PLUGINS_BASE_ARCH_COMP = "xz"
GST_PLUGINS_BASE_ARCH_EXT = "tar." + GST_PLUGINS_BASE_ARCH_COMP

GST_PLUGINS_GOOD_SRC_ROOT = GSTREAMER_SRC_ROOT
GST_PLUGINS_GOOD_ARCH_COMP = "xz"
GST_PLUGINS_GOOD_ARCH_EXT = "tar." + GST_PLUGINS_GOOD_ARCH_COMP

GST_PLUGINS_BAD_SRC_ROOT = GSTREAMER_SRC_ROOT
GST_PLUGINS_BAD_ARCH_COMP = 'xz'
GST_PLUGINS_BAD_ARCH_EXT = 'tar.' + GST_PLUGINS_BAD_ARCH_COMP

GST_PLUGINS_UGLY_SRC_ROOT = GSTREAMER_SRC_ROOT
GST_PLUGINS_UGLY_ARCH_COMP = 'xz'
GST_PLUGINS_UGLY_ARCH_EXT = 'tar.' + GST_PLUGINS_UGLY_ARCH_COMP

GST_LIBAV_SRC_ROOT = GSTREAMER_SRC_ROOT
GST_LIBAV_ARCH_COMP = 'xz'
GST_LIBAV_ARCH_EXT = 'tar.' + GST_LIBAV_ARCH_COMP

GLIB_NETWORKING_SRC_ROOT = 'https://ftp.gnome.org/pub/GNOME/sources/glib-networking'
GLIB_NETWORKING_ARCH_COMP = 'xz'
GLIB_NETWORKING_ARCH_EXT = 'tar.' + GLIB_NETWORKING_ARCH_COMP

FAAC_URL = 'https://github.com/knik0/faac/archive/1_30.tar.gz'
OPENH264_URL = 'https://github.com/cisco/openh264'
LIBVA_URL = 'https://github.com/intel/libva'
LIBVA_UTILS_URL = 'https://github.com/intel/libva-utils'
INTEL_VAAPI_DRIVER_URL = 'https://github.com/intel/intel-vaapi-driver'
MEDIA_SDK_URL = 'https://github.com/Intel-Media-SDK/MediaSDK'
GSTREAMER_MFX_URL = 'https://github.com/intel/gstreamer-media-SDK'
OPENCV_URL = 'https://github.com/opencv/opencv'

SRT_SRC_URL = 'https://github.com/Haivision/srt/archive/'
SRT_ARCH_COMP = 'gz'
SRT_ARCH_EXT = 'tar.' + SRT_ARCH_COMP


class OperationSystem(metaclass=ABCMeta):
    @abstractmethod
    def get_required_exec(self) -> list:
        pass

    @abstractmethod
    def get_build_exec(self) -> list:
        pass

    @abstractmethod
    def get_gst_build_libs(self):
        pass

    def get_gst_repo_libs(self):
        pass


class Debian(OperationSystem):
    def get_required_exec(self) -> list:
        return ['git', 'yasm', 'nasm', 'gcc', 'g++', 'make', 'ninja-build', 'cmake', 'python3-pip']

    def get_build_exec(self) -> list:
        return ['autoconf', 'automake', 'libtool', 'pkg-config', 'gettext', 'bison', 'flex', 'libcairo2-dev',
                'libudev-dev']

    def get_gst_build_libs(self):
        return ['libmount-dev', 'libssl-dev',
                'libdrm-dev', 'libproxy-dev',
                'libblkid-dev', 'libsoup2.4-dev', 'libjpeg-dev',
                'librtmp-dev', 'libasound2-dev', 'libx264-dev', 'libfaad-dev', 'libmp3lame-dev',
                'libgdk-pixbuf2.0-dev', 'libpango1.0-dev',
                # 'freeglut3-dev', # 'libegl1-mesa-dev',
                'zlib1g-dev', 'libbz2-dev'  # 'libffi-dev', 'libxrandr-dev', 'intltool', 'liborc-0.4-dev', 'libxml2-dev'
                ]  # libgstreamer-plugins-base1.0-dev

    def get_gst_repo_libs(self):
        return ['libglib2.0-dev', 'glib-networking', 'libgstreamer1.0-dev', 'libgstreamer-plugins-base1.0-dev',
                'libgstreamer-plugins-good1.0-dev', 'libgstreamer-plugins-bad1.0-dev',
                'gstreamer1.0-tools', 'gstreamer1.0-plugins-base', 'gstreamer1.0-plugins-good',
                'gstreamer1.0-plugins-bad',
                'gstreamer1.0-plugins-ugly', 'gstreamer1.0-libav']


class RedHat(OperationSystem):
    def get_required_exec(self) -> list:
        return ['git', 'yasm', 'nasm', 'gcc', 'gcc-c++', 'make', 'ninja-build', 'cmake', 'python3-pip']

    def get_build_exec(self) -> list:
        return ['autoconf', 'automake', 'libtool', 'pkgconfig', 'gettext', 'bison', 'flex', 'cairo-gobject-devel',
                'libudev-devel']

    def get_gst_build_libs(self):
        return ['libmount-devel', 'openssl-devel',
                'libdrm-devel', 'libproxy-devel',
                'librtmp-devel', 'libsoup-devel', 'libx264-devel', 'alsa-lib-devel', 'lame-devel',
                'libjpeg-turbo-devel', 'gdk-pixbuf2-devel', 'libpango-devel',  # 'libpciaccess-devel',
                'libxcb-devel', 'zlib-devel'  # 'libffi-devel', 'pcre-devel'
                ]

    def get_gst_repo_libs(self):
        return ['glib2-devel', 'glib-networking', 'gstreamer1', 'gstreamer1-plugins-base',
                'gstreamer1-plugins-good',
                'gstreamer1-plugins-bad-free', 'gstreamer1-plugins-ugly-free', 'gstreamer1-libav']


class Arch(OperationSystem):
    def get_required_exec(self) -> list:
        return ['git', 'yasm', 'nasm', 'gcc', 'make', 'ninja', 'cmake', 'python3-pip']

    def get_build_exec(self) -> list:
        return ['autoconf', 'automake', 'libtool', 'pkgconfig', 'gettext', 'bison', 'flex', 'cairo', 'udev']

    def get_gst_build_libs(self) -> list:
        return ['libutil-linux', 'openssl',
                'libdrm', 'libproxy',
                'rtmpdump', 'libsoup', 'x264', 'x265', 'alsa-lib', 'lame', 'libjpeg', 'gdk-pixbuf2',
                'zlib'  # 'libffi', 'pcre'
                ]

    def get_gst_repo_libs(self):
        return ['glibc', 'glib-networking', 'gstreamer', 'gstreamer-plugins-base', 'gstreamer-plugins-good',
                'gstreamer-plugins-bad', 'gstreamer-plugins-ugly', 'gstreamer-libav']


class FreeBSD(OperationSystem):
    def get_required_exec(self) -> list:
        return ['git', 'yasm', 'nasm', 'gcc', 'make', 'ninja', 'cmake', 'python3-pip', 'dbus']

    def get_build_exec(self) -> list:
        return ['autoconf', 'automake', 'libtool', 'pkgconf', 'gettext', 'bison', 'flex', 'cairo', 'libudev-devd']

    def get_gst_build_libs(self):
        return ['openssl',
                'libdrm', 'libproxy',
                'librtmp', 'libsoup', 'libx264', 'alsa-lib', 'libjpeg-turbo',
                'libxcb', 'lzlib', 'gdk-pixbuf2',  # 'libffi', 'pcre'
                ]

    def get_gst_repo_libs(self):
        return ['glib2-devel', 'glib-networking', 'gstreamer1', 'gstreamer1-plugins-base', 'gstreamer1-plugins-good',
                'gstreamer1-plugins-bad', 'gstreamer1-plugins-ugly', 'gstreamer1-libav']


class Windows64(OperationSystem):
    def get_required_exec(self) -> list:
        return ['git', 'mingw-w64-x86_64-yasm', 'mingw-w64-x86_64-nasm', 'mingw-w64-x86_64-gcc', 'make',
                'mingw-w64-x86_64-ninja', 'mingw-w64-x86_64-cmake', 'mingw-w64-x86_64-python3-pip']

    def get_build_exec(self) -> list:
        return []

    def get_gst_build_libs(self):
        return []

    def get_gst_repo_libs(self):
        return ['mingw-w64-x86_64-glib2', 'mingw-w64-x86_64-glib-networking', 'mingw-w64-x86_64-gstreamer',
                'mingw-w64-x86_64-gst-plugins-base', 'mingw-w64-x86_64-gst-plugins-good',
                'mingw-w64-x86_64-gst-plugins-bad', 'mingw-w64-x86_64-gst-plugins-ugly', 'mingw-w64-x86_64-gst-libav']


class Windows32(OperationSystem):
    def get_required_exec(self) -> list:
        return ['git', 'mingw-w64-i686-yasm', 'mingw-w64-i686-nasm', 'mingw-w64-i686-gcc', 'make',
                'mingw-w64-i686-ninja', 'mingw-w64-i686-cmake', 'mingw-w64-i686-python3-pip']

    def get_build_exec(self) -> list:
        return []

    def get_gst_build_libs(self):
        return []

    def get_gst_repo_libs(self):
        return ['mingw-w64-i686-glib2', 'mingw-w64-i686-glib-networking', 'mingw-w64-i686-gstreamer',
                'mingw-w64-i686-gst-plugins-base', 'mingw-w64-i686-gst-plugins-good',
                'mingw-w64-i686-gst-plugins-bad', 'mingw-w64-i686-gst-plugins-ugly', 'mingw-w64-i686-gst-libav']


class MacOSX(OperationSystem):
    def get_required_exec(self) -> list:
        return ['git', 'yasm', 'nasm', 'make', 'ninja', 'cmake', 'python3-pip']

    def get_build_exec(self) -> list:
        return ['autoconf', 'automake', 'libtool', 'pkgconfig', 'gettext', 'bison', 'flex', 'cairo']

    def get_gst_build_libs(self):
        return []

    def get_gst_repo_libs(self):
        return ['glib2-devel', 'glib-networking', 'gstreamer1', 'gstreamer1-plugins-base', 'gstreamer1-plugins-good',
                'gstreamer1-plugins-bad', 'gstreamer1-plugins-ugly', 'gstreamer1-libav']


class BuildRequest(build_utils.BuildRequest):
    def __init__(self, platform, arch_name, dir_path, prefix_path):
        build_utils.BuildRequest.__init__(self, platform, arch_name, dir_path, prefix_path)

    def get_system_libs(self, repo_build=False):
        platform = self.platform_
        platform_name = platform.name()
        ar = platform.architecture()
        dep_libs = []

        current_system = None
        if platform_name == 'linux':
            distribution = system_info.linux_get_dist()
            if distribution == 'DEBIAN':
                current_system = Debian()
                dep_libs.extend(current_system.get_required_exec())
                dep_libs.extend(current_system.get_build_exec())
            elif distribution == 'RHEL':
                current_system = RedHat()
                dep_libs.extend(current_system.get_required_exec())
                dep_libs.extend(current_system.get_build_exec())
            elif distribution == 'ARCH':
                current_system = Arch()
                dep_libs.extend(current_system.get_required_exec())
                dep_libs.extend(current_system.get_build_exec())
        elif platform_name == 'freebsd':
            current_system = FreeBSD()
            dep_libs.extend(current_system.get_required_exec())
            dep_libs.extend(current_system.get_build_exec())
        elif platform_name == 'macosx':
            current_system = MacOSX()
            dep_libs.extend(current_system.get_required_exec())
            dep_libs.extend(current_system.get_build_exec())
        elif platform_name == 'windows':
            if ar.bit() == 64:
                current_system = Windows64()
                dep_libs.extend(current_system.get_required_exec())
            elif ar.bit() == 32:
                current_system = Windows32()
                dep_libs.extend(current_system.get_required_exec())

        if not current_system:
            raise NotImplementedError("Unknown platform '%s'" % platform_name)

        if repo_build:
            dep_libs.extend(current_system.get_gst_repo_libs())
        else:
            dep_libs.extend(current_system.get_gst_build_libs())

        return dep_libs

    def install_system(self):
        dep_libs = self.get_system_libs()
        for lib in dep_libs:
            self._install_package(lib)

        # post install step
        platform = self.platform()
        platform_name = platform.name()
        if platform_name == 'linux':
            distribution = system_info.linux_get_dist()
            if distribution == 'RHEL':
                subprocess.call(['ln', '-sf', '/usr/bin/ninja-build', '/usr/bin/ninja'])
        elif platform_name == 'freebsd':
            subprocess.call(['dbus-uuidgen', '--ensure'])

    def install_tools(self):
        self._install_via_python3('streamlink')
        self._install_via_python3('speedtest-cli')

    def build_faac(self):
        compiler_flags = []
        self._download_and_build_via_bootstrap(FAAC_URL, compiler_flags)

    def build_libva(self):
        compiler_flags = ['--buildtype=release']
        self._clone_and_build_via_meson(LIBVA_URL, compiler_flags)
        self._clone_and_build_via_meson(LIBVA_UTILS_URL, compiler_flags)

    def build_vaapi(self):
        compiler_flags = ['--buildtype=release']
        self._clone_and_build_via_meson(INTEL_VAAPI_DRIVER_URL, compiler_flags)

    def build_mfx(self):
        compiler_flags = []
        self._clone_and_build_via_cmake(MEDIA_SDK_URL, compiler_flags)

    def build_openh264(self):
        compiler_flags = ['--buildtype=release']
        self._clone_and_build_via_meson(OPENH264_URL, compiler_flags)

    def build_srt(self, version):
        compiler_flags = []
        url = '{0}/v{1}.{2}'.format(SRT_SRC_URL, version, SRT_ARCH_EXT)
        self._download_and_build_via_cmake(url, compiler_flags)

    def build_opencv(self):
        compiler_flags = ['-DBUILD_JAVA=OFF', '-DBUILD_TESTS=OFF', '-DWITH_GSTREAMER=OFF',
                          '-DOPENCV_GENERATE_PKGCONFIG=ON']
        self._clone_and_build_via_cmake(OPENCV_URL, compiler_flags)

    def build_fastoml(self):
        cmake_flags = []
        self._clone_and_build_via_cmake(build_utils.generate_fastogt_git_path('fastoml'), cmake_flags)

    def build_glib(self, version):
        compiler_flags = ['--buildtype=release', '-Dgtk_doc=false']
        glib_version_short = version[:version.rfind('.')]
        url = '{0}/{1}/glib-{2}.{3}'.format(GLIB_SRC_ROOT, glib_version_short,
                                            version, GLIB_ARCH_EXT)
        self._download_and_build_via_meson(url, compiler_flags)

    def build_glib_networking(self, version):
        glib_version_short = version[:version.rfind('.')]
        compiler_flags = ['--buildtype=release', '-Dopenssl=enabled']
        url = '{0}/{1}/glib-networking-{2}.{3}'.format(GLIB_NETWORKING_SRC_ROOT, glib_version_short,
                                                       version, GLIB_NETWORKING_ARCH_EXT)
        self._download_and_build_via_meson(url, compiler_flags)

    def build_gstreamer(self, version):
        compiler_flags = ['--buildtype=release', '-Dgst_debug=false', '-Dgtk_doc=disabled']
        url = '{0}gstreamer/gstreamer-{1}.{2}'.format(GSTREAMER_SRC_ROOT, version, GSTREAMER_ARCH_EXT)
        self._download_and_build_via_meson(url, compiler_flags)

    def build_gst_plugins_base(self, version):
        compiler_flags = ['--buildtype=release', '-Dgtk_doc=disabled']
        url = '{0}gst-plugins-base/gst-plugins-base-{1}.{2}'.format(GST_PLUGINS_BASE_SRC_ROOT, version,
                                                                    GST_PLUGINS_BASE_ARCH_EXT)
        self._download_and_build_via_meson(url, compiler_flags)

    def build_gst_plugins_good(self, version):
        compiler_flags = ['--buildtype=release']
        url = '{0}gst-plugins-good/gst-plugins-good-{1}.{2}'.format(GST_PLUGINS_GOOD_SRC_ROOT, version,
                                                                    GST_PLUGINS_GOOD_ARCH_EXT)
        self._download_and_build_via_meson(url, compiler_flags)

    def build_gst_plugins_bad(self, version, build_mfx: bool, build_vaapi: bool):
        compiler_flags = ['--buildtype=release']
        url = build_utils.generate_fastogt_git_path('gst-plugins-bad')
        self._clone_and_build_via_meson(url, compiler_flags)
        if build_mfx:
            compiler_flags_mfx = ['-DWITH_WAYLAND=OFF', '-DMFX_SINK=OFF']
            self._clone_and_build_via_cmake(GSTREAMER_MFX_URL, compiler_flags_mfx)
        if build_vaapi:
            compiler_flags_vaapi = ['--buildtype=release']
            url = '{0}gstreamer-vaapi/gstreamer-vaapi-{1}.{2}'.format(GSTREAMER_SRC_ROOT, version, GSTREAMER_ARCH_EXT)
            self._clone_and_build_via_meson(url, compiler_flags_vaapi)

    def build_gst_plugins_ugly(self, version):
        compiler_flags = ['--buildtype=release']
        url = '{0}gst-plugins-ugly/gst-plugins-ugly-{1}.{2}'.format(GST_PLUGINS_UGLY_SRC_ROOT, version,
                                                                    GST_PLUGINS_UGLY_ARCH_EXT)
        self._download_and_build_via_meson(url, compiler_flags)

    def build_gst_fastoml(self):
        compiler_flags = ['--buildtype=release']
        url = build_utils.generate_fastogt_git_path('gst-fastoml')
        self._clone_and_build_via_meson(url, compiler_flags)

    def build_gst_libav(self, version):
        compiler_flags = []
        url = build_utils.generate_fastogt_git_path('gst-libav')
        self._clone_and_build_via_autogen(url, compiler_flags)


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


if __name__ == "__main__":
    # openssl_default_version = '1.1.1b'
    glib_default_version = '2.60.2'
    # cmake_default_version = '3.4.0'
    meson_default_version = '0.49.2'
    srt_default_version = '1.4.0'
    gstreamer_default_version = '1.16.0'
    gst_plugins_base_default_version = gstreamer_default_version
    gst_plugins_good_default_version = gstreamer_default_version
    gst_plugins_bad_default_version = gstreamer_default_version
    gst_plugins_ugly_default_version = gstreamer_default_version
    gst_libav_default_version = gstreamer_default_version

    host_os = system_info.get_os()
    arch_host_os = system_info.get_arch_name()

    parser = argparse.ArgumentParser(prog='build_env', usage='%(prog)s [options]')
    # system
    system_grp = parser.add_mutually_exclusive_group()
    system_grp.add_argument('--with-system', help='build with system dependencies (default)', dest='with_system',
                            action='store_true', default=True)
    system_grp.add_argument('--without-system', help='build without system dependencies', dest='with_system',
                            action='store_false', default=False)

    # tools
    tools_grp = parser.add_mutually_exclusive_group()
    tools_grp.add_argument('--with-tools', help='build with tools dependencies (default)', dest='with_tools',
                           action='store_true', default=True)
    tools_grp.add_argument('--without-tools', help='build without tools dependencies', dest='with_tools',
                           action='store_false', default=False)

    # cmake
    # cmake_grp = parser.add_mutually_exclusive_group()
    # cmake_grp.add_argument('--with-cmake', help='build cmake (default, version:{0})'.format(meson_default_version),
    #                       dest='with_cmake', action='store_true', default=True)
    # cmake_grp.add_argument('--without-cmake', help='build without cmake', dest='with_cmake', action='store_false',
    #                       default=False)
    # parser.add_argument('--cmake-version', help='cmake version (default: {0})'.format(cmake_default_version),
    #                    default=cmake_default_version)

    # faac
    faac_grp = parser.add_mutually_exclusive_group()
    faac_grp.add_argument('--with-faac', help='build faac (default, version: git master)', dest='with_faac',
                          action='store_true', default=True)
    faac_grp.add_argument('--without-faac', help='build without faac', dest='with_faac', action='store_false',
                          default=False)

    # meson
    meson_grp = parser.add_mutually_exclusive_group()
    meson_grp.add_argument('--with-meson', help='build meson (default, version:{0})'.format(meson_default_version),
                           dest='with_meson', action='store_true', default=True)
    meson_grp.add_argument('--without-meson', help='build without meson', dest='with_meson', action='store_false',
                           default=False)
    parser.add_argument('--meson-version', help='meson version (default: {0})'.format(meson_default_version),
                        default=meson_default_version)

    # openh264
    openh264_grp = parser.add_mutually_exclusive_group()
    openh264_grp.add_argument('--with-openh264', help='build openh264 (default, version: git master)',
                              dest='with_openh264',
                              action='store_true', default=True)
    openh264_grp.add_argument('--without-openh264', help='build without openh264', dest='with_openh264',
                              action='store_false',
                              default=False)

    # libva
    libva_grp = parser.add_mutually_exclusive_group()
    libva_grp.add_argument('--with-libva', help='build libva (default, version: git master)',
                           dest='with_libva',
                           action='store_true', default=False)
    libva_grp.add_argument('--without-libva', help='build without libva', dest='with_libva',
                           action='store_false',
                           default=True)

    # vaapi
    vaapi_grp = parser.add_mutually_exclusive_group()
    vaapi_grp.add_argument('--with-vaapi', help='build vaapi (default, version: git master)',
                           dest='with_vaapi',
                           action='store_true', default=False)
    vaapi_grp.add_argument('--without-vaapi', help='build without vaapi', dest='with_vaapi',
                           action='store_false',
                           default=True)

    # mfx
    mfx_grp = parser.add_mutually_exclusive_group()
    mfx_grp.add_argument('--with-mfx', help='build mfx (default, version: git master)',
                         dest='with_mfx',
                         action='store_true', default=False)
    mfx_grp.add_argument('--without-mfx', help='build without mfx', dest='with_mfx',
                         action='store_false',
                         default=True)

    # srt
    srt_grp = parser.add_mutually_exclusive_group()
    srt_grp.add_argument('--with-srt', help='build srt (default, version:{0})'.format(srt_default_version),
                         dest='with_srt', action='store_true', default=True)
    srt_grp.add_argument('--without-srt', help='build without srt', dest='with_srt', action='store_false',
                         default=False)
    parser.add_argument('--srt-version', help='srt version (default: {0})'.format(srt_default_version),
                        default=srt_default_version)

    # opencv
    opencv_grp = parser.add_mutually_exclusive_group()
    opencv_grp.add_argument('--with-opencv', help='build opencv (default, version: git master)',
                            dest='with_opencv',
                            action='store_true', default=False)
    opencv_grp.add_argument('--without-opencv', help='build without opencv', dest='with_opencv',
                            action='store_false',
                            default=True)

    # json-c
    jsonc_grp = parser.add_mutually_exclusive_group()
    jsonc_grp.add_argument('--with-json-c', help='build json-c (default, version: git master)', dest='with_jsonc',
                           action='store_true', default=True)
    jsonc_grp.add_argument('--without-json-c', help='build without json-c', dest='with_jsonc', action='store_false',
                           default=False)

    # libev
    libev_grp = parser.add_mutually_exclusive_group()
    libev_grp.add_argument('--with-libev', help='build libev (default, version: git master)', dest='with_libev',
                           action='store_true', default=True)
    libev_grp.add_argument('--without-libev', help='build without libev', dest='with_libev', action='store_false',
                           default=False)

    # common
    common_grp = parser.add_mutually_exclusive_group()
    common_grp.add_argument('--with-common', help='build common (default, version: git master)', dest='with_common',
                            action='store_true', default=True)
    common_grp.add_argument('--without-common', help='build without common', dest='with_common',
                            action='store_false',
                            default=False)

    # fastotv_protocol
    fastotv_protocol_grp = parser.add_mutually_exclusive_group()
    fastotv_protocol_grp.add_argument('--with-fastotv-protocol',
                                      help='build fastotv_protocol (default, version: git master)',
                                      dest='with_fastotv_protocol',
                                      action='store_true', default=True)
    fastotv_protocol_grp.add_argument('--without-fastotv-protocol', help='build without fastotv_protocol',
                                      dest='with_fastotv_protocol',
                                      action='store_false',
                                      default=False)

    # fastoml
    fastoml_grp = parser.add_mutually_exclusive_group()
    fastoml_grp.add_argument('--with-fastoml', help='build fastoml (default, version: git master)',
                             dest='with_fastoml',
                             action='store_true', default=False)
    fastoml_grp.add_argument('--without-fastoml', help='build without fastoml', dest='with_fastoml',
                             action='store_false',
                             default=True)

    # glib
    glib_grp = parser.add_mutually_exclusive_group()
    glib_grp.add_argument('--with-glib', help='build glib (default, version:{0})'.format(glib_default_version),
                          dest='with_glib', action='store_true', default=True)
    glib_grp.add_argument('--without-glib', help='build without glib', dest='with_glib', action='store_false',
                          default=False)
    parser.add_argument('--glib-version', help='glib version (default: {0})'.format(glib_default_version),
                        default=glib_default_version)

    # glib-networking
    glib_networking_grp = parser.add_mutually_exclusive_group()
    glib_networking_grp.add_argument('--with-glib-networking',
                                     help='build glib-networking (default, version:{0})'.format(glib_default_version),
                                     dest='with_glib_networking', action='store_true', default=True)
    glib_networking_grp.add_argument('--without-glib-networking', help='build without glib-networking',
                                     dest='with_glib_networking',
                                     action='store_false',
                                     default=False)
    parser.add_argument('--glib-networking-version',
                        help='glib networking version (default: {0})'.format(glib_default_version),
                        default=glib_default_version)

    # openssl
    # openssl_grp = parser.add_mutually_exclusive_group()
    # openssl_grp.add_argument('--with-openssl',
    #                         help='build openssl (default, version:{0})'.format(openssl_default_version),
    #                         dest='with_openssl', action='store_true', default=True)
    # openssl_grp.add_argument('--without-openssl', help='build without openssl', dest='with_openssl',
    #                         action='store_false',
    #                         default=False)
    # parser.add_argument('--openssl-version', help='openssl version (default: {0})'.format(openssl_default_version),
    #                    default=openssl_default_version)

    # gstreamer
    gstreamer_grp = parser.add_mutually_exclusive_group()
    gstreamer_grp.add_argument('--with-gstreamer',
                               help='build gstreamer (default, version:{0})'.format(gstreamer_default_version),
                               dest='with_gstreamer', action='store_true', default=True)
    gstreamer_grp.add_argument('--without-gstreamer', help='build without gstreamer', dest='with_gstreamer',
                               action='store_false',
                               default=False)
    parser.add_argument('--gstreamer-version',
                        help='gstreamer version (default: {0})'.format(gstreamer_default_version),
                        default=gstreamer_default_version)

    # gst-plugins-base
    gst_plugins_base_grp = parser.add_mutually_exclusive_group()
    gst_plugins_base_grp.add_argument('--with-gst-plugins-base',
                                      help='build gst-plugins-base (default, version:{0})'.format(
                                          gst_plugins_base_default_version),
                                      dest='with_gst_plugins_base', action='store_true', default=True)
    gst_plugins_base_grp.add_argument('--without-gst-plugins-base', help='build without gst-plugins-base',
                                      dest='with_gst_plugins_base',
                                      action='store_false',
                                      default=False)
    parser.add_argument('--gst-plugins-base-version',
                        help='gst-plugins-base version (default: {0})'.format(gst_plugins_base_default_version),
                        default=gst_plugins_base_default_version)

    # gst-plugins-good
    gst_plugins_good_grp = parser.add_mutually_exclusive_group()
    gst_plugins_good_grp.add_argument('--with-gst-plugins-good',
                                      help='build gst-plugins-good (default, version:{0})'.format(
                                          gst_plugins_good_default_version),
                                      dest='with_gst_plugins_good', action='store_true', default=True)
    gst_plugins_good_grp.add_argument('--without-gst-plugins-good', help='build without gst-plugins-good',
                                      dest='with_gst_plugins_good',
                                      action='store_false',
                                      default=False)
    parser.add_argument('--gst-plugins-good-version',
                        help='gst-plugins-good version (default: {0})'.format(gst_plugins_good_default_version),
                        default=gst_plugins_good_default_version)

    # gst-plugins-bad
    gst_plugins_bad_grp = parser.add_mutually_exclusive_group()
    gst_plugins_bad_grp.add_argument('--with-gst-plugins-bad',
                                     help='build gst-plugins-bad (default, version:{0})'.format(
                                         gst_plugins_bad_default_version),
                                     dest='with_gst_plugins_bad', action='store_true', default=True)
    gst_plugins_bad_grp.add_argument('--without-gst-plugins-bad', help='build without gst-plugins-bad',
                                     dest='with_gst_plugins_bad',
                                     action='store_false',
                                     default=False)
    parser.add_argument('--gst-plugins-bad-version',
                        help='gst-plugins-bad version (default: {0})'.format(gst_plugins_bad_default_version),
                        default=gst_plugins_bad_default_version)

    # gst-plugins-ugly
    gst_plugins_ugly_grp = parser.add_mutually_exclusive_group()
    gst_plugins_ugly_grp.add_argument('--with-gst-plugins-ugly',
                                      help='build gst-plugins-ugly (default, version:{0})'.format(
                                          gst_plugins_ugly_default_version),
                                      dest='with_gst_plugins_ugly', action='store_true', default=True)
    gst_plugins_ugly_grp.add_argument('--without-gst-plugins-ugly', help='build without gst-plugins-ugly',
                                      dest='with_gst_plugins_ugly',
                                      action='store_false',
                                      default=False)
    parser.add_argument('--gst-plugins-ugly-version',
                        help='gst-plugins-ugly version (default: {0})'.format(gst_plugins_ugly_default_version),
                        default=gst_plugins_ugly_default_version)

    # gst-fastoml
    gst_fastoml_grp = parser.add_mutually_exclusive_group()
    gst_fastoml_grp.add_argument('--with-gst-fastoml', help='build gst-fastoml (default, version: git master)',
                                 dest='with_gst_fastoml',
                                 action='store_true', default=False)
    gst_fastoml_grp.add_argument('--without-gst-fastoml', help='build without gst-fastoml', dest='with_gst_fastoml',
                                 action='store_false',
                                 default=True)

    # gst-libav
    gst_libav_grp = parser.add_mutually_exclusive_group()
    gst_libav_grp.add_argument('--with-gst-libav',
                               help='build gst-libav (default, version:{0})'.format(
                                   gst_libav_default_version),
                               dest='with_gst_libav', action='store_true', default=True)
    gst_libav_grp.add_argument('--without-gst-libav', help='build without gst-libav',
                               dest='with_gst_libav',
                               action='store_false',
                               default=False)
    parser.add_argument('--gst-libav-version',
                        help='gst-libav version (default: {0})'.format(gst_libav_default_version),
                        default=gst_libav_default_version)

    # other
    parser.add_argument('--platform', help='build for platform (default: {0})'.format(host_os), default=host_os)
    parser.add_argument('--architecture', help='architecture (default: {0})'.format(arch_host_os),
                        default=arch_host_os)
    parser.add_argument('--prefix', help='prefix path (default: None)', default=None)

    parser.add_argument('--install-other-packages',
                        help='install other packages (--with-system, --with-tools --with-meson --with-jsonc --with-libev) (default: True)',
                        dest='install_other_packages', type=str2bool, default=True)
    parser.add_argument('--install-fastogt-packages',
                        help='install FastoGT packages (--with-common --with-fastotv-protocol) (default: True)',
                        dest='install_fastogt_packages', type=str2bool, default=True)
    parser.add_argument('--install-gstreamer-packages',
                        help='install FastoGT packages  (--with-glib --with-glib-networking --with-gstreamer --with-gst-plugins-base --with-gst-plugins-good --with-gst-plugins-bad --with-gst-plugins-ugly --gst-libav) (default: True)',
                        dest='install_gstreamer_packages', type=str2bool, default=True)

    argv = parser.parse_args()

    arg_platform = argv.platform
    arg_prefix_path = argv.prefix
    arg_architecture = argv.architecture
    arg_install_other_packages = argv.install_other_packages
    arg_install_fastogt_packages = argv.install_fastogt_packages
    arg_install_gstreamer_packages = argv.install_gstreamer_packages

    request = BuildRequest(arg_platform, arg_architecture, 'build_' + arg_platform + '_env', arg_prefix_path)
    if argv.with_system and arg_install_other_packages:
        request.install_system()

    if argv.with_tools and arg_install_other_packages:
        request.install_tools()

    if argv.with_faac and arg_install_other_packages:
        request.build_faac()

    # if argv.with_cmake:
    #    request.build_cmake(argv.cmake_version)

    if argv.with_meson and arg_install_other_packages:
        request.build_meson(argv.meson_version)

    # if argv.with_openh264 and arg_install_other_packages:
    #    request.build_openh264()

    if argv.with_libva and arg_install_other_packages:
        request.build_libva()

    build_vaapi = argv.with_vaapi and arg_install_other_packages
    if build_vaapi:
        request.build_vaapi()

    build_mfx = argv.with_mfx and arg_install_other_packages
    if build_mfx:
        request.build_mfx()

    if argv.with_srt and arg_install_other_packages:
        request.build_srt(argv.srt_version)

    if argv.with_opencv and arg_install_other_packages:
        request.build_opencv()

    if argv.with_jsonc and arg_install_other_packages:
        request.build_jsonc()
    if argv.with_libev and arg_install_other_packages:
        request.build_libev()
    if argv.with_common and arg_install_fastogt_packages:
        request.build_common()

    if argv.with_fastotv_protocol and arg_install_fastogt_packages:
        request.build_fastotv_protocol()

    if argv.with_fastoml and arg_install_fastogt_packages:
        request.build_fastoml()

    # if argv.with_openssl:
    #    request.build_openssl(argv.openssl_version, True)
    if argv.with_glib and arg_install_gstreamer_packages:
        request.build_glib(argv.glib_version)
    if argv.with_glib_networking and arg_install_gstreamer_packages:
        request.build_glib_networking(argv.glib_version)

    if argv.with_gstreamer and arg_install_gstreamer_packages:
        request.build_gstreamer(argv.gstreamer_version)

    if argv.with_gst_plugins_base and arg_install_gstreamer_packages:
        request.build_gst_plugins_base(argv.gst_plugins_base_version)

    if argv.with_gst_plugins_good and arg_install_gstreamer_packages:
        request.build_gst_plugins_good(argv.gst_plugins_good_version)

    if argv.with_gst_plugins_bad and arg_install_gstreamer_packages:
        request.build_gst_plugins_bad(argv.gst_plugins_bad_version, build_mfx, build_vaapi)

    if argv.with_gst_plugins_ugly and arg_install_gstreamer_packages:
        request.build_gst_plugins_ugly(argv.gst_plugins_ugly_version)

    if argv.with_gst_fastoml and arg_install_gstreamer_packages:
        request.build_gst_fastoml()

    if argv.with_gst_libav and arg_install_gstreamer_packages:
        request.build_gst_libav(argv.gst_libav_version)

    check_plugins()
