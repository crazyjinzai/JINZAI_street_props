# JINZAI Street Props 1.1.4 — Minecraft 1.21.1

This independent Architectury project builds the Fabric and NeoForge adapters
with Java 21. Run `gradlew clean build` from this directory. Minecraft 1.20.1
Fabric and Forge are built from the repository root with Java 17.

The shared block catalog registers 370 decorative blocks in five creative tabs:
street lights, road signs, bus stops, municipal facilities and vehicles. Vehicle
parts are static decorative blocks. Placement restrictions for side branches and
top assemblies, cardinal facing, outlines, collision and illumination preserve
the shared catalog behavior.

Models, textures, translations, blockstates, loot tables and the icon are read
directly from the root `common/src/main/resources` directory. No independent art
copy is maintained here. Resource processing only converts Minecraft 1.21 data
directory names and pack formats: resource format 34 and data format 48, accepted
through `supported_formats`.

Requires Minecraft 1.21.1, Java 21 and Architectury 13.0.8 (13.x). Fabric uses
Loader 0.17.2 and Fabric API 0.116.15+1.21.1. NeoForge uses 21.1.248. Install the
corresponding dependencies separately and select only the JAR for your loader.

- `fabric/build/libs/JINZAI_Street_props-Fabric-1.21.1-1.1.4.jar`
- `neoforge/build/libs/JINZAI_Street_props-NeoForge-1.21.1-1.1.4.jar`

本目录为 Minecraft 1.21.1 / Java 21 独立工程，提供 Fabric 与 NeoForge 适配。
在本目录运行 `gradlew clean build`；1.20.1 的 Fabric / Forge 工程位于仓库根目录。
四端共用 370 个方块及五个创造分类，模型、贴图与语言只有根目录一套权威资源。
移植保持路灯分支侧面放置、顶部组件仅顶面放置、水平朝向、碰撞和发光行为。
汽车载具为静态装饰方块，不包含驾驶功能。

本模组由 "Crzay津仔" 提供美术与资金支持，"QiZhang" 提供技术实现与制作。
发布署名仅为 "Crzay津仔"；美术版权归 Crzay津仔，代码与配置版权归 QiZhang。
项目自身内容采用根目录 MIT 许可证，第三方内容保留各自许可证。
