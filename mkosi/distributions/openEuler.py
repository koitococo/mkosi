# SPDX-License-Identifier: LGPL-2.1-or-later

from collections.abc import Iterable

from mkosi.config import Architecture
from mkosi.context import Context
from mkosi.distributions import centos, join_mirror
from mkosi.installer.dnf import Dnf
from mkosi.installer.rpm import RpmRepository, find_rpm_gpgkey, setup_rpm
from mkosi.log import die


class Installer(centos.Installer):
    @classmethod
    def pretty_name(cls) -> str:
        return "openEuler"

    @classmethod
    def default_release(cls) -> str:
        return "openEuler-24.03-LTS"

    @classmethod
    def filesystem(cls) -> str:
        return "ext4"

    @classmethod
    def setup(cls, context: Context) -> None:
        setup_rpm(context)
        Dnf.setup(
            context,
            list(cls.repositories(context)),
            filelists=False,
        )

    @classmethod
    def gpgurls(cls, context: Context) -> tuple[str, ...]:
        return (
            find_rpm_gpgkey(
                context,
                "RPM-GPG-KEY-openEuler",
                f"https://dl-cdn.openeuler.openatom.cn/openEuler-{context.config.release}/everything/{Installer.architecture(context.config.architecture)}/RPM-GPG-KEY-openEuler",
            ),
        )

    @classmethod
    def repositories(cls, context: Context) -> Iterable[RpmRepository]:
        gpgurls = cls.gpgurls(context)
        if context.config.local_mirror:
            yield RpmRepository("openEuler", f"baseurl={context.config.local_mirror}", gpgurls)
            return

        mirror = context.config.mirror or "https://dl-cdn.openeuler.openatom.cn"

        yield RpmRepository(
            "openEuler",
            f"baseurl={join_mirror(mirror, '$releasever/everything/$basearch/')}",
            gpgurls,
        )
        yield RpmRepository(
            "openEuler-update",
            f"baseurl={join_mirror(mirror, '$releasever/update/$basearch/')}",
            gpgurls,
        )

    @classmethod
    def architecture(cls, arch: Architecture) -> str:
        a = {
            Architecture.arm64:     "aarch64",
            Architecture.riscv64:   "riscv64",
            Architecture.x86_64:    "x86_64",
        }.get(arch)  # fmt: skip

        if not a:
            die(f"Architecture {a} is not supported by openEuler")
        return a

