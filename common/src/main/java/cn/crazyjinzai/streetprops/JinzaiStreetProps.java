/*
 * 本模组由"Crzay津仔"提供美术与资金支持，"QiZhang"提供技术实现与制作。
 * 发布署名仅为"Crzay津仔"，美术素材版权归 "Crzay津仔"所有，模组代码/配置版权归"QiZhang"所有。
 */
package cn.crazyjinzai.streetprops;

import cn.crazyjinzai.streetprops.block.CatalogFacingBlock;
import com.google.gson.Gson;
import com.google.gson.JsonParseException;
import dev.architectury.registry.CreativeTabRegistry;
import dev.architectury.registry.registries.DeferredRegister;
import dev.architectury.registry.registries.RegistrySupplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

public final class JinzaiStreetProps {
    public static final String MOD_ID = "jinzai_street_props";
    public static final String VERSION = "1.1.2";

    private static final String CATALOG_RESOURCE =
        "assets/" + MOD_ID + "/block_catalog.json";
    private static final int CATALOG_SCHEMA = 1;
    private static final Gson GSON = new Gson();

    private static final List<BlockDefinition> DEFINITIONS = loadCatalog();
    private static final DeferredRegister<CreativeModeTab> TABS =
        DeferredRegister.create(MOD_ID, Registries.CREATIVE_MODE_TAB);
    private static final DeferredRegister<Block> BLOCKS =
        DeferredRegister.create(MOD_ID, Registries.BLOCK);
    private static final DeferredRegister<Item> ITEMS =
        DeferredRegister.create(MOD_ID, Registries.ITEM);

    private static final EnumMap<Category, List<RegistrySupplier<Block>>> BLOCKS_BY_CATEGORY =
        emptyCategoryMap();
    private static final List<RegistrySupplier<Block>> ALL_BLOCKS = new ArrayList<>();
    private static final EnumMap<Category, RegistrySupplier<CreativeModeTab>> CATEGORY_TABS =
        registerTabs();

    private static volatile boolean initialized;

    static {
        for (BlockDefinition definition : DEFINITIONS) {
            RegistrySupplier<Block> block = BLOCKS.register(
                definition.id(),
                () -> createBlock(definition)
            );
            ITEMS.register(
                definition.id(),
                () -> new BlockItem(
                    block.get(),
                    new Item.Properties().arch$tab(CATEGORY_TABS.get(definition.category()))
                )
            );
            ALL_BLOCKS.add(block);
            BLOCKS_BY_CATEGORY.get(definition.category()).add(block);
        }
    }

    private JinzaiStreetProps() {
    }

    public static synchronized void init() {
        if (initialized) {
            return;
        }
        TABS.register();
        BLOCKS.register();
        ITEMS.register();
        initialized = true;
    }

    public static List<RegistrySupplier<Block>> getRegisteredBlocks() {
        return Collections.unmodifiableList(ALL_BLOCKS);
    }

    public static List<BlockDefinition> getDefinitions() {
        return DEFINITIONS;
    }

    public static ResourceLocation id(String path) {
        return new ResourceLocation(MOD_ID, path);
    }

    private static EnumMap<Category, RegistrySupplier<CreativeModeTab>> registerTabs() {
        EnumMap<Category, RegistrySupplier<CreativeModeTab>> tabs = new EnumMap<>(Category.class);
        for (Category category : Category.values()) {
            RegistrySupplier<CreativeModeTab> tab = TABS.register(
                category.serializedName,
                () -> CreativeTabRegistry.create(
                    Component.translatable(category.translationKey()),
                    () -> new ItemStack(BLOCKS_BY_CATEGORY.get(category).get(0).get())
                )
            );
            tabs.put(category, tab);
        }
        return tabs;
    }

    private static Block createBlock(BlockDefinition definition) {
        BlockBehaviour.Properties properties = BlockBehaviour.Properties.of()
            .strength(definition.kind() == Kind.LIGHT_HEAD ? 0.6F : 1.5F, 6.0F)
            .sound(definition.kind() == Kind.LIGHT_HEAD ? SoundType.GLASS : SoundType.METAL)
            .noOcclusion();
        if (definition.lightLevel() > 0) {
            properties.lightLevel(state -> definition.lightLevel());
        }
        return new CatalogFacingBlock(
            properties,
            definition.collisionBoxes(),
            definition.placementMode()
        );
    }

    private static List<BlockDefinition> loadCatalog() {
        InputStream input = JinzaiStreetProps.class.getClassLoader()
            .getResourceAsStream(CATALOG_RESOURCE);
        if (input == null) {
            throw new IllegalStateException("Missing block catalog: " + CATALOG_RESOURCE);
        }
        CatalogDocument document;
        try (InputStream stream = input;
             Reader reader = new InputStreamReader(stream, StandardCharsets.UTF_8)) {
            document = GSON.fromJson(reader, CatalogDocument.class);
        } catch (JsonParseException | IOException exception) {
            throw new IllegalStateException("Could not parse block catalog", exception);
        }
        if (document == null || document.schema != CATALOG_SCHEMA || document.blocks == null) {
            throw new IllegalStateException("Unsupported or incomplete block catalog");
        }

        List<BlockDefinition> result = new ArrayList<>(document.blocks.size());
        Set<String> ids = new HashSet<>();
        EnumMap<Category, Integer> categoryCounts = new EnumMap<>(Category.class);
        EnumMap<Kind, Integer> kindCounts = new EnumMap<>(Kind.class);
        for (Category category : Category.values()) {
            categoryCounts.put(category, 0);
        }
        for (Kind kind : Kind.values()) {
            kindCounts.put(kind, 0);
        }

        for (int index = 0; index < document.blocks.size(); index++) {
            CatalogEntry entry = document.blocks.get(index);
            if (entry == null || entry.id == null || entry.id.isBlank()) {
                throw catalogError(index, "missing id");
            }
            if (!ids.add(entry.id)) {
                throw catalogError(index, "duplicate id " + entry.id);
            }
            ResourceLocation parsedId = id(entry.id);
            if (!parsedId.getPath().equals(entry.id)) {
                throw catalogError(index, "invalid normalized id " + entry.id);
            }
            Category category = Category.parse(entry.category, index);
            Kind kind = Kind.parse(entry.kind, index);
            PlacementMode placement = PlacementMode.parse(entry.placement, index);
            CollisionMode collisionMode = CollisionMode.parse(entry.collision_mode, index);
            if (entry.light_level < 0 || entry.light_level > 15) {
                throw catalogError(index, "light_level outside 0..15");
            }
            if ((kind == Kind.LIGHT_HEAD) != (entry.light_level == 15)) {
                throw catalogError(index, "only light heads must use light level 15");
            }
            if (kind.expectedPlacement != placement) {
                throw catalogError(index, "kind/placement mismatch for " + entry.id);
            }
            // Phase-two poles follow the same single-box policy as all new props.
            // Detailed collision is retained only for the existing pole assets.
            if (collisionMode == CollisionMode.DETAILED && !kind.isPole()) {
                throw catalogError(index, "kind/collision_mode mismatch for " + entry.id);
            }
            List<ModelBox> boxes = validateBoxes(entry.collision_boxes, index);
            if (collisionMode == CollisionMode.BOUNDING && boxes.size() != 1) {
                throw catalogError(index, "bounding collision must contain one box");
            }
            result.add(new BlockDefinition(
                entry.id,
                category,
                kind,
                placement,
                collisionMode,
                entry.light_level,
                boxes
            ));
            categoryCounts.put(category, categoryCounts.get(category) + 1);
            kindCounts.put(kind, kindCounts.get(kind) + 1);
        }

        assertCount("all blocks", result.size(), 213);
        assertCount("street lights", categoryCounts.get(Category.STREET_LIGHTS), 117);
        assertCount("road signs", categoryCounts.get(Category.ROAD_SIGNS), 30);
        assertCount("bus stops", categoryCounts.get(Category.BUS_STOPS), 20);
        assertCount("municipal facilities", categoryCounts.get(Category.MUNICIPAL), 6);
        assertCount("vehicles", categoryCounts.get(Category.VEHICLES), 40);
        assertCount("light heads", kindCounts.get(Kind.LIGHT_HEAD), 41);
        assertCount("side branches", kindCounts.get(Kind.SIDE_BRANCH), 46);
        assertCount("top assemblies", kindCounts.get(Kind.TOP_ASSEMBLY), 3);
        assertCount("street-light poles", kindCounts.get(Kind.STREET_POLE), 27);
        assertCount("sign poles", kindCounts.get(Kind.SIGN_POLE), 7);
        assertCount("other decorations", kindCounts.get(Kind.DECORATION), 89);
        return Collections.unmodifiableList(result);
    }

    private static List<ModelBox> validateBoxes(
        List<List<Double>> rawBoxes,
        int entryIndex
    ) {
        if (rawBoxes == null || rawBoxes.isEmpty()) {
            throw catalogError(entryIndex, "missing collision_boxes");
        }
        List<ModelBox> result = new ArrayList<>(rawBoxes.size());
        for (int boxIndex = 0; boxIndex < rawBoxes.size(); boxIndex++) {
            List<Double> raw = rawBoxes.get(boxIndex);
            if (raw == null || raw.size() != 6) {
                throw catalogError(entryIndex, "collision box must have six coordinates");
            }
            double[] value = new double[6];
            for (int coordinate = 0; coordinate < value.length; coordinate++) {
                Double number = raw.get(coordinate);
                if (number == null || !Double.isFinite(number)) {
                    throw catalogError(entryIndex, "non-finite collision coordinate");
                }
                value[coordinate] = number;
            }
            if (value[0] >= value[3] || value[1] >= value[4] || value[2] >= value[5]) {
                throw catalogError(entryIndex, "collision box has non-positive size");
            }
            result.add(new ModelBox(
                value[0], value[1], value[2], value[3], value[4], value[5]
            ));
        }
        return Collections.unmodifiableList(result);
    }

    private static void assertCount(String label, int actual, int expected) {
        if (actual != expected) {
            throw new IllegalStateException(
                "Catalog contains " + actual + " " + label + "; expected " + expected
            );
        }
    }

    private static IllegalStateException catalogError(int index, String message) {
        return new IllegalStateException("Invalid block catalog entry " + index + ": " + message);
    }

    private static EnumMap<Category, List<RegistrySupplier<Block>>> emptyCategoryMap() {
        EnumMap<Category, List<RegistrySupplier<Block>>> map = new EnumMap<>(Category.class);
        for (Category category : Category.values()) {
            map.put(category, new ArrayList<>());
        }
        return map;
    }

    public enum Category {
        STREET_LIGHTS("street_lights"),
        ROAD_SIGNS("road_signs"),
        BUS_STOPS("bus_stops"),
        MUNICIPAL("municipal"),
        VEHICLES("vehicles");

        private final String serializedName;

        Category(String serializedName) {
            this.serializedName = serializedName;
        }

        private String translationKey() {
            return "itemGroup." + MOD_ID + "." + serializedName;
        }

        private static Category parse(String raw, int index) {
            if (raw != null) {
                String normalized = raw.toLowerCase(Locale.ROOT);
                for (Category category : values()) {
                    if (category.serializedName.equals(normalized)) {
                        return category;
                    }
                }
            }
            throw catalogError(index, "unknown category " + raw);
        }
    }

    public enum PlacementMode {
        HORIZONTAL("horizontal"),
        SIDE_ONLY("side_only"),
        TOP_ONLY("top_only");

        private final String serializedName;

        PlacementMode(String serializedName) {
            this.serializedName = serializedName;
        }

        private static PlacementMode parse(String raw, int index) {
            if (raw != null) {
                String normalized = raw.toLowerCase(Locale.ROOT);
                for (PlacementMode mode : values()) {
                    if (mode.serializedName.equals(normalized)) {
                        return mode;
                    }
                }
            }
            throw catalogError(index, "unknown placement " + raw);
        }
    }

    public enum CollisionMode {
        DETAILED("detailed"),
        BOUNDING("bounding");

        private final String serializedName;

        CollisionMode(String serializedName) {
            this.serializedName = serializedName;
        }

        private static CollisionMode parse(String raw, int index) {
            if (raw != null) {
                String normalized = raw.toLowerCase(Locale.ROOT);
                for (CollisionMode mode : values()) {
                    if (mode.serializedName.equals(normalized)) {
                        return mode;
                    }
                }
            }
            throw catalogError(index, "unknown collision_mode " + raw);
        }
    }

    public enum Kind {
        LIGHT_HEAD("light_head", PlacementMode.HORIZONTAL),
        SIDE_BRANCH("side_branch", PlacementMode.SIDE_ONLY),
        TOP_ASSEMBLY("top_assembly", PlacementMode.TOP_ONLY),
        STREET_POLE("street_pole", PlacementMode.HORIZONTAL),
        SIGN_POLE("sign_pole", PlacementMode.HORIZONTAL),
        DECORATION("decoration", PlacementMode.HORIZONTAL);

        private final String serializedName;
        private final PlacementMode expectedPlacement;

        Kind(String serializedName, PlacementMode expectedPlacement) {
            this.serializedName = serializedName;
            this.expectedPlacement = expectedPlacement;
        }

        private boolean isPole() {
            return this == STREET_POLE || this == SIGN_POLE;
        }

        private static Kind parse(String raw, int index) {
            if (raw != null) {
                String normalized = raw.toLowerCase(Locale.ROOT);
                for (Kind kind : values()) {
                    if (kind.serializedName.equals(normalized)) {
                        return kind;
                    }
                }
            }
            throw catalogError(index, "unknown kind " + raw);
        }
    }

    public record ModelBox(
        double minX,
        double minY,
        double minZ,
        double maxX,
        double maxY,
        double maxZ
    ) {
    }

    public record BlockDefinition(
        String id,
        Category category,
        Kind kind,
        PlacementMode placementMode,
        CollisionMode collisionMode,
        int lightLevel,
        List<ModelBox> collisionBoxes
    ) {
    }

    private static final class CatalogDocument {
        private int schema;
        private List<CatalogEntry> blocks;
    }

    private static final class CatalogEntry {
        private String id;
        private String category;
        private String kind;
        private String placement;
        private String collision_mode;
        private int light_level;
        private List<List<Double>> collision_boxes;
    }
}
