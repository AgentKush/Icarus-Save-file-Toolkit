# Campaign State Research

## Key Components for Campaign State
1. WorldTalentManagerRecorderComponent (Actor 32) - WorldTalentRecords array
2. InstancedLevelRecorderComponent (Actor 22) - Cave slot state
3. IcarusQuestManagerRecorderComponent (Actor 31) - Faction mission state
4. IcarusQuestRecorderComponent (Actors 4810-4818) - Individual quest actors
5. GameModeStateRecorderComponent (Actor 24) - 14,582 bytes unparseable
6. WorldBossManagerRecorderComponent (Actor 28) - Boss spawn/kill state
7. Rock Golem Spawners (Actors 850, 3313-3315) - Cave encounter state

## Reset Requirements
1. WorldTalentRecords -> empty
2. InstancedLevel -> reset cave
3. QuestManager -> clear FactionMissionName, InitialQuestRecord, DynamicMissionProspectName
4. Quest actors -> remove or reset
5. Rock Golem Spawners -> reset RecordedNumSpawned, bGeneratedRewards
6. GameModeState -> needs investigation
