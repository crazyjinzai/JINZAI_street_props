/*
 * 本模组由"Crzay津仔"提供美术与资金支持，"QiZhang"提供技术实现与制作。
 * 发布署名仅为"Crzay津仔"，美术素材版权归 "Crzay津仔"所有，模组代码/配置版权归"QiZhang"所有。
 */
package cn.crazyjinzai.streetprops.forge;

import cn.crazyjinzai.streetprops.JinzaiStreetProps;
import dev.architectury.platform.forge.EventBuses;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;

@Mod(JinzaiStreetProps.MOD_ID)
public final class JinzaiStreetPropsForge {
    public JinzaiStreetPropsForge() {
        EventBuses.registerModEventBus(
            JinzaiStreetProps.MOD_ID,
            FMLJavaModLoadingContext.get().getModEventBus()
        );
        JinzaiStreetProps.init();
    }
}
