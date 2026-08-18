from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"


def main() -> None:
    flutter = shutil.which("flutter")
    if flutter is None:
        raise SystemExit("Flutter SDK was not found in PATH")

    subprocess.run(
        [
            flutter,
            "create",
            str(FRONTEND),
            "--platforms=android,windows",
            "--project-name=school_inventory_frontend",
            "--org=com.lisovcoff",
        ],
        check=True,
    )

    generated_widget_test = FRONTEND / "test/widget_test.dart"
    if generated_widget_test.exists() and "MyApp" in generated_widget_test.read_text(
        encoding="utf-8"
    ):
        generated_widget_test.unlink()

    manifest = FRONTEND / "android/app/src/main/AndroidManifest.xml"
    text = manifest.read_text(encoding="utf-8")
    permission = '<uses-permission android:name="android.permission.CAMERA" />'
    if permission not in text:
        marker = ">"
        index = text.find(marker)
        text = text[: index + 1] + f"\n    {permission}" + text[index + 1 :]
        manifest.write_text(text, encoding="utf-8")

    print("Flutter Android and Windows runner files are ready.")


if __name__ == "__main__":
    main()
