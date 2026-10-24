# Resource tooling

`generate_resources.py` uses the public `block_manifest.json`, the 13-language
name data and the supplied model/PNG folders. It needs Python 3.10 or newer and
no private spreadsheets. The optional `phase_three_gui.json` changes only the
inventory transform of the listed model. `phase_three_hand.json` supplies
centered first/third-person hand transforms for ten new models that originally
defined only GUI display. Neither override changes placed geometry or textures.

Image verification and icon tooling need Pillow:

```text
python -m pip install -r tools/requirements.txt
python tools/generate_resources.py
python tools/verify_release.py
```

Run the commands from the repository root. Java/Gradle builds use the already
generated resources and do not require Python or Pillow.

`verify_phase_three.py` additionally accepts a 1.1.2 source archive and the
customer source/patch inputs for a complete compatibility and provenance audit;
run it with `--help` for these optional paths. The private customer documents
are not needed for ordinary source verification or building the mod.

For Minecraft 1.21.1 artifacts, use the JAR verifier in
`versions/1.21.1/tools/verify_port.py`.

所有工具均保留客户提供的贴图像素。货车头使用单张合并图的UV适配，原始输入和本次
UV取色证明保存在项目的本地制作记录中，不作为模组运行依赖或公开构建前置条件。
