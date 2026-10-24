/*
 * 本模组由"Crzay津仔"提供美术与资金支持，"QiZhang"提供技术实现与制作。
 * 发布署名仅为"Crzay津仔"，美术素材版权归 "Crzay津仔"所有，模组代码/配置版权归"QiZhang"所有。
 */
package cn.crazyjinzai.streetprops.block;

import cn.crazyjinzai.streetprops.JinzaiStreetProps.ModelBox;
import cn.crazyjinzai.streetprops.JinzaiStreetProps.PlacementMode;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.block.Block;
import net.minecraft.block.BlockState;
import net.minecraft.block.HorizontalFacingBlock;
import net.minecraft.block.ShapeContext;
import net.minecraft.item.ItemPlacementContext;
import net.minecraft.state.StateManager;
import net.minecraft.util.BlockMirror;
import net.minecraft.util.BlockRotation;
import net.minecraft.util.function.BooleanBiFunction;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Direction;
import net.minecraft.util.shape.VoxelShape;
import net.minecraft.util.shape.VoxelShapes;
import net.minecraft.world.BlockView;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Locale;

@SuppressWarnings("deprecation")
public final class CatalogFacingBlock extends HorizontalFacingBlock {
    private static final Codec<ModelBox> BOX_CODEC = Codec.DOUBLE.listOf().comapFlatMap(values -> {
        if (values.size() != 6 || values.stream().anyMatch(value -> !Double.isFinite(value))
            || values.get(0) >= values.get(3) || values.get(1) >= values.get(4)
            || values.get(2) >= values.get(5)) {
            return DataResult.error(() -> "A catalog collision box needs six finite ordered coordinates");
        }
        return DataResult.success(new ModelBox(values.get(0), values.get(1), values.get(2),
            values.get(3), values.get(4), values.get(5)));
    }, box -> List.of(box.minX(), box.minY(), box.minZ(), box.maxX(), box.maxY(), box.maxZ()));
    private static final Codec<PlacementMode> PLACEMENT_CODEC = Codec.STRING.comapFlatMap(value -> {
        for (PlacementMode mode : PlacementMode.values()) {
            if (mode.name().toLowerCase(Locale.ROOT).equals(value)) {
                return DataResult.success(mode);
            }
        }
        return DataResult.error(() -> "Unknown catalog placement mode: " + value);
    }, mode -> mode.name().toLowerCase(Locale.ROOT));
    public static final MapCodec<CatalogFacingBlock> CODEC = RecordCodecBuilder.mapCodec(instance ->
        instance.group(
            CatalogFacingBlock.<CatalogFacingBlock>createSettingsCodec(),
            BOX_CODEC.listOf().fieldOf("collision_boxes").forGetter(block -> block.northBoxes),
            PLACEMENT_CODEC.fieldOf("placement").forGetter(block -> block.placementMode)
        ).apply(instance, CatalogFacingBlock::new)
    );

    private final List<ModelBox> northBoxes;
    private final EnumMap<Direction, VoxelShape> directionalShapes;
    private final PlacementMode placementMode;

    public CatalogFacingBlock(
        Settings settings,
        List<ModelBox> northBoxes,
        PlacementMode placementMode
    ) {
        super(settings);
        this.northBoxes = List.copyOf(northBoxes);
        this.directionalShapes = createDirectionalShapes(this.northBoxes);
        this.placementMode = placementMode;
        setDefaultState(getStateManager().getDefaultState().with(FACING, Direction.NORTH));
    }

    @Override
    protected MapCodec<? extends HorizontalFacingBlock> getCodec() {
        return CODEC;
    }

    @Override
    public BlockState getPlacementState(ItemPlacementContext context) {
        Direction clickedFace = context.getSide();
        if (placementMode == PlacementMode.SIDE_ONLY) {
            if (!clickedFace.getAxis().isHorizontal()) {
                return null;
            }
            // The supplied north-state branch geometry extends toward +Z.
            // Keep the support-facing direction so the arm extends away from
            // the clicked pole face, matching the Minecraft 1.20.1 behavior.
            return getDefaultState().with(FACING, clickedFace.getOpposite());
        }
        if (placementMode == PlacementMode.TOP_ONLY && clickedFace != Direction.UP) {
            return null;
        }
        return getDefaultState().with(FACING, context.getHorizontalPlayerFacing().getOpposite());
    }

    @Override
    public BlockState rotate(BlockState state, BlockRotation rotation) {
        return state.with(FACING, rotation.rotate(state.get(FACING)));
    }

    @Override
    public BlockState mirror(BlockState state, BlockMirror mirror) {
        return state.rotate(mirror.getRotation(state.get(FACING)));
    }

    @Override
    protected void appendProperties(StateManager.Builder<Block, BlockState> builder) {
        builder.add(FACING);
    }

    @Override
    public VoxelShape getOutlineShape(
        BlockState state,
        BlockView world,
        BlockPos position,
        ShapeContext context
    ) {
        return shapeFor(state);
    }

    @Override
    public VoxelShape getCollisionShape(
        BlockState state,
        BlockView world,
        BlockPos position,
        ShapeContext context
    ) {
        return shapeFor(state);
    }

    private VoxelShape shapeFor(BlockState state) {
        return directionalShapes.getOrDefault(
            state.get(FACING),
            directionalShapes.get(Direction.NORTH)
        );
    }

    private static EnumMap<Direction, VoxelShape> createDirectionalShapes(List<ModelBox> northBoxes) {
        if (northBoxes.isEmpty()) {
            throw new IllegalArgumentException("A catalog block cannot have an empty shape");
        }
        EnumMap<Direction, VoxelShape> shapes = new EnumMap<>(Direction.class);
        List<ModelBox> boxes = List.copyOf(northBoxes);
        shapes.put(Direction.NORTH, union(boxes));
        boxes = rotateClockwise(boxes);
        shapes.put(Direction.EAST, union(boxes));
        boxes = rotateClockwise(boxes);
        shapes.put(Direction.SOUTH, union(boxes));
        boxes = rotateClockwise(boxes);
        shapes.put(Direction.WEST, union(boxes));
        return shapes;
    }

    private static VoxelShape union(List<ModelBox> boxes) {
        List<VoxelShape> level = new ArrayList<>(boxes.size());
        for (ModelBox box : boxes) {
            level.add(Block.createCuboidShape(
                box.minX(), box.minY(), box.minZ(), box.maxX(), box.maxY(), box.maxZ()
            ));
        }
        // Keep the exact union, combining a balanced tree without repeatedly
        // simplifying the growing voxel grid. Simplify only the final result.
        while (level.size() > 1) {
            List<VoxelShape> next = new ArrayList<>((level.size() + 1) / 2);
            for (int index = 0; index < level.size(); index += 2) {
                next.add(index + 1 < level.size()
                    ? VoxelShapes.combine(level.get(index), level.get(index + 1), BooleanBiFunction.OR)
                    : level.get(index));
            }
            level = next;
        }
        return level.getFirst().simplify();
    }

    private static List<ModelBox> rotateClockwise(List<ModelBox> boxes) {
        return boxes.stream().map(box -> new ModelBox(
            16.0D - box.maxZ(), box.minY(), box.minX(),
            16.0D - box.minZ(), box.maxY(), box.maxX()
        )).toList();
    }
}
