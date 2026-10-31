"""Mount-table inspection: what is really mounted, not its autofs trigger."""

from __future__ import annotations

import errno
import sys
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from handrolled.mounts import (  # noqa: E402
    decode_mount_field,
    describe_path,
    is_unc,
    mount_for,
    parse_mounts,
    stale_hint,
)

MOUNTS = textwrap.dedent(
    """\
    /dev/sda2 / ext4 rw,relatime 0 0
    //192.0.2.10/kb /mnt/kb cifs rw,relatime,vers=3.0,username=me 0 0
    //192.0.2.10/kb/outbox /mnt/kb-out cifs rw,relatime,vers=3.0 0 0
    //192.0.2.10/archive /mnt/archive cifs ro,relatime,vers=3.0 0 0
    192.0.2.20:/export /mnt/nfs nfs4 rw,relatime 0 0
    /dev/sdb1 /mnt/with\\040space ext4 rw,relatime 0 0
    """
)


class TestMountTable(unittest.TestCase):
    def test_octal_escapes_are_decoded(self):
        self.assertEqual(decode_mount_field(r"/mnt/with\040space"), "/mnt/with space")
        self.assertEqual(decode_mount_field(r"a\134b"), "a\\b")
        self.assertEqual(decode_mount_field("plain"), "plain")

    def test_parse_reads_all_rows(self):
        rows = parse_mounts(MOUNTS)
        self.assertEqual(len(rows), 6)
        self.assertIn("cifs", {r.fstype for r in rows})

    def test_longest_mount_point_wins(self):
        inside = mount_for("/mnt/kb-out/reports", mounts_text=MOUNTS)
        self.assertIsNotNone(inside)
        self.assertEqual(inside.mountpoint, "/mnt/kb-out")
        outer = mount_for("/mnt/kb/other", mounts_text=MOUNTS)
        self.assertEqual(outer.mountpoint, "/mnt/kb")

    def test_network_and_readonly_flags(self):
        self.assertTrue(mount_for("/mnt/kb/x", mounts_text=MOUNTS).is_network)
        self.assertTrue(mount_for("/mnt/nfs/x", mounts_text=MOUNTS).is_network)
        self.assertFalse(mount_for("/etc/hosts", mounts_text=MOUNTS).is_network)
        self.assertTrue(mount_for("/mnt/archive/x", mounts_text=MOUNTS).readonly)
        self.assertFalse(mount_for("/mnt/kb/x", mounts_text=MOUNTS).readonly)

    def test_device_reported_for_cifs(self):
        self.assertEqual(mount_for("/mnt/kb/x", mounts_text=MOUNTS).server, "//192.0.2.10/kb")

    def test_autofs_trigger_does_not_shadow_the_real_mount(self):
        """`/proc/mounts` lists an autofs trigger and the cifs mount on the same
        mount point; the real filesystem must win."""
        table = textwrap.dedent(
            """\
            systemd-1 /mnt/nas/kb autofs rw,relatime,fd=63,pgrp=1 0 0
            //192.0.2.10/kb /mnt/nas/kb cifs rw,relatime,vers=3.0 0 0
            """
        )
        info = mount_for("/mnt/nas/kb/knowledge", mounts_text=table)
        self.assertEqual(info.fstype, "cifs")
        self.assertTrue(info.is_network)

    def test_describe_path_marks_unc_and_local(self):
        self.assertTrue(describe_path(r"\\nas\share\kb")["unc"])
        self.assertTrue(is_unc("//nas/share"))
        self.assertFalse(is_unc("/mnt/kb"))
        described = describe_path("/mnt/archive/x", mounts_text=MOUNTS)
        self.assertTrue(described["network"])
        self.assertTrue(described["readonly"])
        self.assertEqual(described["fstype"], "cifs")

    def test_stale_hint_is_actionable(self):
        stale = stale_hint(OSError(errno.ESTALE, "Stale file handle"))
        self.assertIn("stale", stale)
        self.assertIn("mount -a", stale)
        denied = stale_hint(OSError(errno.EACCES, "Permission denied"))
        self.assertIn("read-only", denied)
        gone = stale_hint(OSError(errno.ENOENT, "No such file or directory"))
        self.assertIn("not reachable", gone)


if __name__ == "__main__":
    unittest.main()
