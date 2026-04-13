# Initial Findings - Prospect Blob Structure

## File Format
ProspectBlob = base64-encoded, zlib-compressed UE4 binary (1.6MB compressed -> 34.4MB)

## Top-Level Properties
1. StateRecorderBlobs (ArrayProperty) - 4,826 elements
2. Version (IntProperty)
3. LobbyPrivacy (EnumProperty)
4. ProspectInfo (StructProperty)
5. ProspectMapName (StrProperty) - e.g. "Terrain_016"
6. LastSavedDateTime (StructProperty/DateTime)

## Actor Types (4,826 total)
2056 VoxelRecorder, 898 Deployable, 644 ResourceDeposit, 320 Spline, 
161 BuildingGrid, 142 CaveAI, 128 CaveEntrance, 125 SpawnedVoxel, 
106 FLODTile, 69 CropPlot, 30 IcarusMountCharacter, 28 Bed, 
21 EnzymeGeyser, 17 Drill, etc.
