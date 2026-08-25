/*
 * 本模组由"Crzay津仔"提供美术与资金支持，"QiZhang"提供技术实现与制作。
 * 发布署名仅为"Crzay津仔"，美术素材版权归 "Crzay津仔"所有，模组代码/配置版权归"QiZhang"所有。
 */
package cn.crazyjinzai.streetprops.fabric;

import cn.crazyjinzai.streetprops.JinzaiStreetProps;
import net.fabricmc.api.ModInitializer;

public final class JinzaiStreetPropsFabric implements ModInitializer {
    @Override
    public void onInitialize() {
        JinzaiStreetProps.init();
    }
}
