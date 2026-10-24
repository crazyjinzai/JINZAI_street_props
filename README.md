# JINZAI Street Props / 津仔的街道设施

## English

JINZAI Street Props 1.1.4 adds 370 city-building blocks to Minecraft 1.20.1
(Fabric / Forge) and Minecraft 1.21.1 (Fabric / NeoForge). All four variants
share the mod ID `jinzai_street_props`, version, models, textures and block IDs.
Vehicle parts are static decorative blocks. MTR is not a required dependency.

### Content

Phase three added 157 blocks: 32 street-light parts, one passenger stop sign,
27 municipal props, 59 vehicle parts and 38 guardrail parts. It also updates
the collision of the existing corner cone crossbar and 25 poles. All 213 existing
IDs, world models, textures and names remain compatible.

Five creative tabs contain Street Lights (149), Road Signs (30), Bus Stop
Signs (21), Municipal Facilities (71, including guardrails), and Vehicles (99).
Block and tab names support 13 locales. Items have no custom tooltip notes.

- 47 light heads and two branches with attached light heads emit light level 15.
- 67 street-light branches and white/blue accessories attach to horizontal block faces; three complete
  assemblies require a top face. Other blocks retain horizontal rotation.
- 11 corner blocks, including corner guardrails, the orange construction
  fence corner, inner/outer curb corners and the corner cone crossbar, use
  model-aligned collision, preserving gaps. Rotated cuboids use at most one
  model-unit steps in the rotation plane (1/16 of a block).
- The remaining 359 blocks, including both white guardrail 3 corner variants and all street-light and sign poles, use one
  enclosing collision box per placed model.
- White guardrail 3 (low corner) now uses one box instead of 196. The tall
  corner retains its previous single-box fix. All eight white/blue street-light
  accessories use the newly supplied models and one recomputed enclosing box,
  facing the clicked pole side. Customer inventory transforms are preserved.
  Remove and replace previously misoriented accessories from the side of the pole;
  saved block orientations are preserved.
- The mod icon uses the approved full 1024×1024 artwork, converted to PNG with
  no crop, repainting or resampling.
- Textures use the supplied standalone PNGs, with the three approved replacement
  textures taking priority. The blue truck cab uses remapped UVs on the supplied
  combined texture. Customer PS blur and colors are preserved.
- Ten new models that supplied only inventory display now have fitted first-
  and third-person hand transforms so holding a complete vehicle does not cover
  the camera. Placed dimensions and collisions remain unchanged.
- There are no animated textures or driving controls.

### Requirements and installation

Choose exactly one JAR matching both the Minecraft version and loader.
Dependencies are installed separately.

| Minecraft | Loader | Java | Required dependencies |
|---|---|---|---|
| 1.20.1 | Fabric | 17 | Fabric API; Architectury API >=9.0.6 <10.0.0 |
| 1.20.1 | Forge 47.x | 17 | Architectury API >=9.0.6 <10.0.0 |
| 1.21.1 | Fabric | 21 | Fabric API; Architectury API >=13.0.8 <14.0.0 |
| 1.21.1 | NeoForge 21.1.x | 21 | Architectury API >=13.0.8 <14.0.0 |

Dependency set used for local validation: Fabric Loader 0.17.2;
Fabric API 0.92.6+1.20.1 / 0.116.15+1.21.1; Forge 47.4.23;
NeoForge 21.1.248; Architectury API 9.2.14 / 13.0.8.

### Build and regenerate

Build the root project with JDK 17 using `gradlew clean build` for 1.20.1.
Build `versions/1.21.1` with JDK 21 using its `gradlew clean build` for 1.21.1.
Keep the complete source tree: the 1.21.1 project reads the root shared resources
and converts data paths and pack formats for Minecraft 1.21.1.

Each loader's distributable JAR is in its `build/libs` directory. Use the regular
JAR, not the `dev`, `sources` or `shadow` variants.

Generated resources and original artwork are included. To regenerate:

```text
python tools/generate_resources.py
python tools/generate_icon.py
python tools/verify_release.py
```

The public `tools/block_manifest.json` and localization files contain all names
and placement metadata; private spreadsheets are not needed. The Blockbench
project resolution defines UV units independently of PNG size. Original art
is retained; fitted inventory transforms do not change world geometry.

### License and credits

Project code, configuration, models and textures use the [MIT License](LICENSE).
Third-party components retain their own licenses. Art and financial support:
**Crzay津仔**. Technical implementation: **QiZhang**. Published author: **Crzay津仔**.

## 中文

津仔的街道设施 1.1.4 同时支持 Minecraft 1.20.1 Fabric/Forge 和
Minecraft 1.21.1 Fabric/NeoForge。四端使用相同模组 ID、版本号及完整的 370 个方块。

### 本期内容

第三期累计新增 157 个方块：32 个路灯部件、1 个客运停靠牌、27 个市政设施、59 个载具部件、
38 个护栏部件；另调整已有交通锥拐角横杆和25个杆件的碰撞箱。原 213 个 ID、世界模型、
贴图和名称保持兼容。载具是静态装饰方块，不包含驾驶功能；本模组无动态贴图。

保留五个创造分类：路灯149、路牌30、公交站牌21、市政设施71（含护栏）、汽车载具99。
方块名称与分类标题支持13种语言，物品不添加自定义 Tooltip 备注。

47个灯头与2个带灯头分支提供15级亮度。67个分支及白色、蓝色配件采用侧面安装，3个成品路灯沿用顶部安装。
11个拐角方块（拐角护栏、橙色施工围栏拐角、路肩内外拐角、交通锥拐角横杆）按模型贴合，
保留空隙；旋转杆件以旋转平面内不超过1模型单位（1/16格）的分段逼近。其余359个方块
使用包住放置后完整体积的一个大碰撞箱，碰撞随四向朝向同步旋转。
其中“白色护栏3（矮款拐角）”由196个碰撞盒合并为单箱；高款拐角保留上次的单箱修复。
全部8种白色、蓝色路灯配件使用客户补发的新模型和物品栏变换，并重新计算整体单箱；
统一按所点击的灯杆侧面确定朝向，使安装端接合灯杆。8张贴图与原版一致。
此前已放歪的配件需要拆下后从灯杆侧面重新放置，已有存档朝向不会自动改变。
原18个路灯杆、7个路牌杆也按此规则改为整体大箱。模组图标使用客户确认的完整1024×1024
原图直接转PNG，保留画面和像素，不裁切、不重绘、不缩放。

贴图以客户原素材与补发三张PNG为准，保留PS处理造成的模糊和色彩；蓝色货车头调整
贴图坐标以使用客户合并后的原图。物品栏尺寸修正只影响GUI，不改变世界模型。
10个原来只设置物品栏显示的新增模型补齐第一、第三人称手持变换，避免完整车辆拿在手中
挡住视线；放置后的模型尺寸与碰撞保持不变。

### 安装与构建

按上方表格安装对应Minecraft、加载器、Java和依赖，只使用相应端的一份JAR。
根工程用JDK17构建1.20.1，`versions/1.21.1`子工程用JDK21构建1.21.1，均运行
`gradlew clean build`。子工程依赖根目录公共资源，必须完整保留源码树。

源码包含生成资源和原始美术；运行 `python tools/generate_resources.py` 可重新生成，
运行 `python tools/verify_release.py` 可静态校验。公开方块清单和翻译词库已包含生成所需
名称及配置，不需要私有工作表。实际实机验证范围与限制见本次交付报告。

### 署名与版权

本模组由"Crzay津仔"提供美术与资金支持，"QiZhang"提供技术实现与制作。
发布署名仅为"Crzay津仔"，美术素材版权归 "Crzay津仔"所有，模组代码/配置版权归"QiZhang"所有。

本项目自身代码、配置、模型和贴图使用 [MIT许可证](LICENSE)，第三方组件保留各自许可证。
