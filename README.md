# JINZAI Street Props / 津仔的街道设施

## English

JINZAI Street Props is a Minecraft 1.20.1 decorative expansion for Fabric and
Forge. It adds 119 city-building blocks: street-light heads, side branches,
complete top-mounted assemblies, street-light poles, road signs, sign poles,
parking signage, and bus-stop signs. It can be installed alongside JINZAI
Traffic Lights and MTR; no hard MTR API dependency is required.

The mod uses an Architectury `common + fabric + forge` project so content and
behavior are implemented once and packaged for both loaders. The two release
artifacts use the same mod ID (`jinzai_street_props`) and version (`1.0.0`).

### Content and behavior

- 31 street-light heads emit a constant light level of 15.
- 30 street-light branches can only be placed against one of the four
  horizontal faces of a supporting block.
- Three completed street-light assemblies can only be placed on a top face.
- 18 street-light poles and seven road-sign poles use detailed model-aligned
  collision.
- Every other model (94 blocks) uses exactly one bounding collision box around
  the complete placed model. This avoids the aiming/outline frame drops caused
  by hundreds of tiny boxes and makes adjacent block placement practical.
- Road signs are decorative and do not provide editable text.
- Electrical poles are not included because their art is not complete.
- Items intentionally display names only. No custom tooltip notes are added.

Creative inventory content is divided into Street Lights, Road Signs, and Bus
Stop Signs. Names and creative-tab titles automatically follow the Minecraft
language setting in 13 locales: Simplified Chinese, English, Arabic, German,
Spanish, French, Hindi, Indonesian, Japanese, Korean, Brazilian Portuguese,
Russian, and Turkish.

### Requirements

- Minecraft 1.20.1
- Java 17 bytecode
- Fabric: Fabric Loader, Fabric API, and Architectury API 9.0.6 or newer but
  earlier than 10.0.0; the bundled and verified recommended version is 9.2.14
- Forge: Forge 47.x and Architectury API 9.0.6 or newer but earlier than 10.0.0;
  the bundled and verified recommended version is 9.2.14

### Build

1. Run `tools/generate_resources.py` with Python 3.11 or newer.
2. Run `tools/generate_icon.py` with Pillow installed.
3. Run `gradlew clean build` using JDK 17.

The distributable files are generated as:

- `fabric/build/libs/JINZAI_Street_props-Fabric-1.20.1-1.0.0.jar`
- `forge/build/libs/JINZAI_Street_props-Forge-1.20.1-1.0.0.jar`

The source model folders, naming workbooks, original design document, resource
generator, icon renderer, and verification tool are retained in this source
package. Generated resources must not be edited by hand; correct the source or
generator and regenerate so both loaders remain synchronized.

### Credit and copyright

Art and financial support are provided by **Crzay津仔**. Technical
implementation and production are provided by **QiZhang**. The published author
is **Crzay津仔** only. Copyright in the art assets belongs to Crzay津仔;
copyright in the mod code and configuration belongs to QiZhang.

## 中文

津仔的街道设施是适用于 Minecraft 1.20.1 Fabric 与 Forge 的城市装饰模组，
共加入119个城建方块，包括路灯头、路灯分支、顶部路灯成品、路灯杆、路牌、
路牌杆、停车场标志牌与公交站牌。模组可与津仔的交通灯及 MTR 一同安装，
不强制依赖 MTR API。

工程采用 Architectury `common + fabric + forge` 多模块结构，内容和行为仅在
公共模块实现一次，再同步打包为两个加载器版本。两端使用相同模组ID
（`jinzai_street_props`）与版本号（`1.0.0`）。

### 内容与行为

- 31个路灯头持续提供15级亮度。
- 30个路灯分支只能贴在支撑方块的东、西、南、北四个侧面。
- 3个路灯成品只能放在方块顶部。
- 18个路灯杆和7个路牌杆使用按模型对齐的精细碰撞箱。
- 其余94个模型均严格使用一个覆盖模型放置后整体体积的大碰撞箱，避免瞄准
  复杂模型时因大量碎片碰撞箱造成严重掉帧，同时方便在模型侧边继续放方块。
- 路牌仅作装饰，不支持编辑文字。
- 电线杆美术尚未完成，本期不加入。
- 所有物品只显示名称，不添加任何自定义红框备注或 Tooltip。

创造模式物品分为“路灯”“路牌”“公交站牌”三个标签页。方块名称与标签页
标题会按照游戏语言自动切换，包含简体中文、英语、阿拉伯语、德语、西班牙语、
法语、印地语、印度尼西亚语、日语、韩语、巴西葡萄牙语、俄语和土耳其语，
共13种语言。

### 运行依赖

- Minecraft 1.20.1
- Java 17 字节码
- Fabric：Fabric Loader、Fabric API、Architectury API 兼容9.0.6至低于10.0.0；
  随包并已验证的推荐版本为9.2.14
- Forge：Forge 47.x、Architectury API 兼容9.0.6至低于10.0.0；
  随包并已验证的推荐版本为9.2.14

### 构建方式

1. 使用 Python 3.11或更高版本运行 `tools/generate_resources.py`。
2. 安装 Pillow 后运行 `tools/generate_icon.py`。
3. 使用 JDK 17运行 `gradlew clean build`。

最终可分发文件位于：

- `fabric/build/libs/JINZAI_Street_props-Fabric-1.20.1-1.0.0.jar`
- `forge/build/libs/JINZAI_Street_props-Forge-1.20.1-1.0.0.jar`

源码包保留原始模型文件夹、命名表格、设计文档、资源生成器、图标渲染脚本和
验证工具。生成资源不应手工修改；新增内容时应修改源文件或生成器后重新生成，
从而保证 Fabric 与 Forge 同步。

### 署名与版权

本模组由"Crzay津仔"提供美术与资金支持，"QiZhang"提供技术实现与制作。
发布署名仅为"Crzay津仔"，美术素材版权归 "Crzay津仔"所有，模组代码/配置版权归"QiZhang"所有。
