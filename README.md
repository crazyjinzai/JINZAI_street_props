# JINZAI Street Props / 津仔的街道设施

## English

JINZAI Street Props is a Minecraft 1.20.1 decorative expansion for Fabric and
Forge. It adds 213 city-building blocks: street-light heads, side branches,
complete top-mounted assemblies, street-light poles, road signs, sign poles,
parking signage, bus-stop structures, municipal facilities, and decorative vehicle parts. It can be installed alongside JINZAI
Traffic Lights and MTR; no hard MTR API dependency is required.

The mod uses an Architectury `common + fabric + forge` project so content and
behavior are implemented once and packaged for both loaders. The two release
artifacts use the same mod ID (`jinzai_street_props`) and version (`1.1.2`).

### Content and behavior

- 41 street-light heads emit a constant light level of 15.
- 46 street-light branches can only be placed against one of the four
  horizontal faces of a supporting block.
- Three completed street-light assemblies can only be placed on a top face.
- The original 18 street-light poles and seven road-sign poles retain their
  detailed model-aligned collision.
- Every other model (188 blocks), including all 94 additions, uses exactly one
  bounding collision box around
  the complete placed model. This avoids the aiming/outline frame drops caused
  by hundreds of tiny boxes and makes adjacent block placement practical.
- Road signs are decorative and do not provide editable text.
- Electrical poles are not included because their art is not complete.
- Items intentionally display names only. No custom tooltip notes are added.

Creative inventory content is divided into Street Lights, Road Signs, Bus
Stop Signs, Municipal Facilities, and Vehicles. Names and creative-tab titles automatically follow the Minecraft
language setting in 13 locales: Simplified Chinese, English, Arabic, German,
Spanish, French, Hindi, Indonesian, Japanese, Korean, Brazilian Portuguese,
Russian, and Turkish.

### Version 1.1.2

Adds 94 blocks: 35 street-light parts, 13 bus-stop parts, six municipal props,
and 40 decorative vehicle parts. All 119 existing block IDs and world models
are preserved. Three road signs receive only updated inventory display transforms.
Vehicle parts are static decorative blocks. The ten new light heads emit level 15;
the 16 new branches attach to horizontal faces. All new models, including the
nine new poles, use one bounding collision box around their placed geometry.
The October 1 recheck also centers and scales nine oversized inventory icons
to fit their slots, retaining their viewing angles and the police pickup icon
fix. Customer models/textures, world geometry and collision boxes are unchanged.

### Requirements

- Minecraft 1.20.1
- Java 17 bytecode
- Fabric: Fabric Loader, Fabric API, and Architectury API 9.0.6 or newer but
  earlier than 10.0.0; testing used Architectury API 9.2.14
- Forge: Forge 47.x and Architectury API 9.0.6 or newer but earlier than 10.0.0;
  testing used Architectury API 9.2.14

Install these dependencies separately; they are not bundled in the release JARs.

### Build

Run `gradlew clean build` using JDK 17. The committed generated resources are
complete, so the public source package does not need private design inputs to
build. `tools/generate_icon.py` can optionally regenerate the icon with Pillow.

The distributable files are generated as:

- `fabric/build/libs/JINZAI_Street_props-Fabric-1.20.1-1.1.2.jar`
- `forge/build/libs/JINZAI_Street_props-Forge-1.20.1-1.1.2.jar`

The source model folders, source textures, icon artwork, resource generator,
icon renderer, verification tool, and generated runtime resources are retained
in this source package. Private non-build documents and naming workbooks are
excluded. The resource generator requires separately maintained private inputs
and is retained for the complete private-source workflow; it is not required to
build the public package. Regeneration uses:

```text
python tools/generate_resources.py --private-input-root <phase-one-inputs> --phase-two-input-root <phase-two-inputs>
python tools/verify_release.py
```

The input paths point to the private naming workbooks; they are never copied
into the public source tree. Supplied standalone PNG files are used as textures.
The Blockbench project resolution defines the UV units independently of PNG size.

### Credit and copyright

Art and financial support are provided by **Crzay津仔**. Technical
implementation and production are provided by **QiZhang**. The published author
is **Crzay津仔** only. Copyright in the art assets belongs to Crzay津仔;
copyright in the mod code and configuration belongs to QiZhang.

### License

The project's own code, configuration, models, textures, and other assets use
the [MIT License](LICENSE). The copyright ownership stated above is unchanged.
Third-party components and their assets retain their respective licenses and
copyright notices.

## 中文

津仔的街道设施是适用于 Minecraft 1.20.1 Fabric 与 Forge 的城市装饰模组，
共加入213个城建方块，包括路灯头、路灯分支、顶部路灯成品、路灯杆、路牌、
路牌杆、停车场标志牌、公交站牌、市政设施和装饰载具部件。模组可与津仔的交通灯及 MTR 一同安装，
不强制依赖 MTR API。

工程采用 Architectury `common + fabric + forge` 多模块结构，内容和行为仅在
公共模块实现一次，再同步打包为两个加载器版本。两端使用相同模组ID
（`jinzai_street_props`）与版本号（`1.1.2`）。

### 内容与行为

- 41个路灯头持续提供15级亮度。
- 46个路灯分支只能贴在支撑方块的东、西、南、北四个侧面。
- 3个路灯成品只能放在方块顶部。
- 原有18个路灯杆和7个路牌杆保留按模型对齐的精细碰撞箱。
- 其余188个模型（包含全部94个新增模型）使用一个覆盖放置后整体体积的大碰撞箱，避免瞄准
  复杂模型时因大量碎片碰撞箱造成严重掉帧，同时方便在模型侧边继续放方块。
- 路牌仅作装饰，不支持编辑文字。
- 电线杆美术尚未完成，本期不加入。
- 所有物品只显示名称，不添加任何自定义红框备注或 Tooltip。

创造模式物品分为“路灯”“路牌”“公交站牌”“市政设施”“汽车载具”五个标签页。方块名称与标签页
标题会按照游戏语言自动切换，包含简体中文、英语、阿拉伯语、德语、西班牙语、
法语、印地语、印度尼西亚语、日语、韩语、巴西葡萄牙语、俄语和土耳其语，
共13种语言。

### 1.1.2 更新

新增94个方块：35个路灯部件、13个公交站部件、6个市政设施和40个装饰载具部件。
保留原有119个方块ID及世界模型，3个路牌仅更新物品栏显示变换。载具部件是静态装饰方块。
新增10个灯头提供15级照明，16个路灯分支沿用侧面放置规则；全部新增模型（含9个灯杆）
均使用一个包住放置后完整模型的大碰撞箱。
10月1日复检另外修正9个超出物品栏槽位的图标，仅等比缩小、居中并保留原观察角度，
同时保留警用皮卡图标修复；客户原模型与贴图、世界模型和碰撞箱不变。

### 运行依赖

- Minecraft 1.20.1
- Java 17 字节码
- Fabric：Fabric Loader、Fabric API、Architectury API 兼容9.0.6至低于10.0.0；
  测试使用Architectury API 9.2.14
- Forge：Forge 47.x、Architectury API 兼容9.0.6至低于10.0.0；
  测试使用Architectury API 9.2.14

这些依赖需要另行安装，Release JAR不内置依赖。

### 构建方式

使用 JDK 17运行 `gradlew clean build`。公开源码已包含完整的生成资源，构建时不需要
私有设计输入；安装 Pillow 后可按需运行 `tools/generate_icon.py`重新生成图标。

最终可分发文件位于：

- `fabric/build/libs/JINZAI_Street_props-Fabric-1.20.1-1.1.2.jar`
- `forge/build/libs/JINZAI_Street_props-Forge-1.20.1-1.1.2.jar`

源码包保留原始模型文件夹、原始贴图、图标素材、资源生成器、图标渲染脚本、
验证工具和已生成运行资源；私有且不参与构建的说明文档与命名工作表不随包发布。
资源生成器需要另行维护私有输入，仅供完整私有源码流程使用，不影响公开源码构建。
重新生成时，使用上方命令分别指定一期、二期命名表目录；不要把私有工作表加入公开源码。
贴图采用客户提供的独立PNG，UV按Blockbench项目分辨率归一化，不按PNG像素尺寸修改。

### 署名与版权

本模组由"Crzay津仔"提供美术与资金支持，"QiZhang"提供技术实现与制作。
发布署名仅为"Crzay津仔"，美术素材版权归 "Crzay津仔"所有，模组代码/配置版权归"QiZhang"所有。

### 许可证

本项目自身的代码、配置、模型、贴图及其他素材统一采用 [MIT 许可证](LICENSE)，
上述版权归属保持不变。第三方组件及其素材保留各自的许可证和版权声明。
