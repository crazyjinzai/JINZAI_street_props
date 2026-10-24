/*
 * 本模组由"Crzay津仔"提供美术与资金支持，"QiZhang"提供技术实现与制作。
 * 发布署名仅为"Crzay津仔"，美术素材版权归 "Crzay津仔"所有，模组代码/配置版权归"QiZhang"所有。
 */
package cn.crazyjinzai.streetprops.client;

import cn.crazyjinzai.streetprops.JinzaiStreetProps;
import dev.architectury.registry.client.rendering.RenderTypeRegistry;
import net.minecraft.client.render.RenderLayer;
import net.minecraft.block.Block;

public final class JinzaiStreetPropsClient {
    private static boolean initialized;

    private JinzaiStreetPropsClient() {
    }

    public static synchronized void init() {
        if (initialized) {
            return;
        }
        Block[] blocks = JinzaiStreetProps.getRegisteredBlocks().stream()
            .map(supplier -> supplier.get())
            .toArray(Block[]::new);
        RenderTypeRegistry.register(RenderLayer.getCutout(), blocks);
        initialized = true;
    }
}
