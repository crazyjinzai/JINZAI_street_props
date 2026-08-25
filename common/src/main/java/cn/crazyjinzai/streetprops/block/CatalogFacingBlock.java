/*
 * 本模组由"Crzay津仔"提供美术与资金支持，"QiZhang"提供技术实现与制作。
 * 发布署名仅为"Crzay津仔"，美术素材版权归 "Crzay津仔"所有，模组代码/配置版权归"QiZhang"所有。
 */
package cn.crazyjinzai.streetprops.block;

import cn.crazyjinzai.streetprops.JinzaiStreetProps.ModelBox;
import cn.crazyjinzai.streetprops.JinzaiStreetProps.PlacementMode;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.EnumMap;
import java.util.List;

@SuppressWarnings("deprecation")
public final class CatalogFacingBlock extends HorizontalDirectionalBlock {
    private final EnumMap<Direction, VoxelShape> directionalShapes;
    private final PlacementMode placementMode;

    public CatalogFacingBlock(
        Properties properties,
        List<ModelBox> northBoxes,
        PlacementMode placementMode
    ) {
        super(properties);
        this.directionalShapes = createDirectionalShapes(northBoxes);
        this.placementMode = placementMode;
        registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH));
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        Direction clickedFace = context.getClickedFace();
        if (placementMode == PlacementMode.SIDE_ONLY) {
            if (!clickedFace.getAxis().isHorizontal()) {
                return null;
            }
            // The supplied north-state branch geometry extends toward +Z.
            // Store the support-facing direction so the rendered arm extends
            // away from the clicked pole face rather than back through it.
            return defaultBlockState().setValue(FACING, clickedFace.getOpposite());
        }
        if (placementMode == PlacementMode.TOP_ONLY && clickedFace != Direction.UP) {
            return null;
        }
        return defaultBlockState().setValue(
            FACING,
            context.getHorizontalDirection().getOpposite()
        );
    }

    @Override
    public BlockState rotate(BlockState state, Rotation rotation) {
        return state.setValue(FACING, rotation.rotate(state.getValue(FACING)));
    }

    @Override
    public BlockState mirror(BlockState state, Mirror mirror) {
        return state.rotate(mirror.getRotation(state.getValue(FACING)));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING);
    }

    @Override
    public VoxelShape getShape(
        BlockState state,
        BlockGetter world,
        BlockPos position,
        CollisionContext context
    ) {
        return shapeFor(state);
    }

    @Override
    public VoxelShape getCollisionShape(
        BlockState state,
        BlockGetter world,
        BlockPos position,
        CollisionContext context
    ) {
        return shapeFor(state);
    }

    private VoxelShape shapeFor(BlockState state) {
        return directionalShapes.getOrDefault(
            state.getValue(FACING),
            directionalShapes.get(Direction.NORTH)
        );
    }

    private static EnumMap<Direction, VoxelShape> createDirectionalShapes(
        List<ModelBox> northBoxes
    ) {
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
        VoxelShape shape = Shapes.empty();
        for (ModelBox box : boxes) {
            shape = Shapes.or(shape, Block.box(
                box.minX(), box.minY(), box.minZ(),
                box.maxX(), box.maxY(), box.maxZ()
            ));
        }
        return shape.optimize();
    }

    private static List<ModelBox> rotateClockwise(List<ModelBox> boxes) {
        return boxes.stream().map(box -> new ModelBox(
            16.0D - box.maxZ(),
            box.minY(),
            box.minX(),
            16.0D - box.minZ(),
            box.maxY(),
            box.maxX()
        )).toList();
    }
}
