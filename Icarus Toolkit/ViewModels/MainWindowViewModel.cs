using System.Collections.ObjectModel;
using System.Diagnostics;
using Avalonia.Controls;
using Avalonia.Platform.Storage;
using Avalonia.Threading;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Icarus;
using Icarus_Toolkit.Utils;
using Icarus_Toolkit.Views;
using Serilog;

namespace Icarus_Toolkit.ViewModels;

public partial class MainWindowViewModel : ViewModelBase
{
    #region Core & UI

    [ObservableProperty]
    private string? gamePath;

    private GameData? gameData;

    [ObservableProperty]
    private bool validGamePath;

    [ObservableProperty]
    private bool isWorking;

    [ObservableProperty]
    private bool editMode;

    [ObservableProperty]
    private bool wasDataExported;

    [ObservableProperty]
    private string loadText = "Load Character Data";

    [ObservableProperty]
    private string? informationString;

    [ObservableProperty]
    private bool isInformationStringVisible;

    private DispatcherTimer? _informationStringTimer;

    [ObservableProperty]
    private int progress;

    [ObservableProperty]
    private bool isProgressVisible;

    [ObservableProperty]
    private bool isWarningIconVisible;

    [ObservableProperty]
    private bool isPathWarningVisible;

    [ObservableProperty]
    private string? pathWarningText;

    // Icon system — loads icons from GitHub on demand
    private readonly IconResolver _iconResolver = new();

    [ObservableProperty]
    private int iconCount;

    /// <summary>
    /// Initialize the icon resolver from the embedded manifest.
    /// Called once on startup; icons are fetched from GitHub when needed.
    /// </summary>
    private void InitializeIcons()
    {
        if (_iconResolver.IsInitialized) return;

        _iconResolver.BuildIndexFromManifest();
        IconCount = _iconResolver.IndexedCount;
        Log.Information("Icon system ready: {Count} icons indexed from manifest", IconCount);
    }

    #endregion

    #region Character

    private CharacterExplorer? characterExplorerHandle;

    [ObservableProperty]
    private List<Character>? characterList;

    [ObservableProperty]
    private int selectedCharacterIndex;

    [ObservableProperty]
    private Character? selectedCharacter;

    [ObservableProperty]
    private int selectedCharacterLevel;

    [ObservableProperty]
    private string? characterDisplayName;

    [ObservableProperty]
    private bool isCharacterLoaded;

    private int currentLoadedCharacterIndex;

    public int MaxXP => 5400001;

    [ObservableProperty]
    private int xPLevel;

    // Edited values
    private int editedXP;
    public int EditedXP
    {
        get => editedXP;
        set
        {
            var clamped = Math.Clamp(value, 0, MaxXP);
            if (SetProperty(ref editedXP, clamped))
                XPLevel = Core.GetPlayerLevel(editedXP);
        }
    }

    [ObservableProperty]
    private string? editedName;

    // Character status
    [ObservableProperty]
    private bool editedIsDead;

    [ObservableProperty]
    private bool editedIsAbandoned;

    [ObservableProperty]
    private string? editedLocation;

    [ObservableProperty]
    private string? editedLastProspectId;

    [ObservableProperty]
    private string? lastPlayedDisplay;

    #endregion

    #region Talents

    [ObservableProperty]
    private ObservableCollection<TalentData> selectedCharacterTalents = [];

    [ObservableProperty]
    private int selectedTalentIndex = -1;

    [ObservableProperty]
    private string? newTalentRowName;

    [ObservableProperty]
    private int newTalentRank = 1;

    #endregion

    #region Cosmetics

    [ObservableProperty]
    private int cosmeticHead;

    [ObservableProperty]
    private int cosmeticHair;

    [ObservableProperty]
    private int cosmeticHairColor;

    [ObservableProperty]
    private int cosmeticBody;

    [ObservableProperty]
    private int cosmeticBodyColor;

    [ObservableProperty]
    private int cosmeticSkinTone;

    [ObservableProperty]
    private int cosmeticHeadTattoo;

    [ObservableProperty]
    private int cosmeticHeadScar;

    [ObservableProperty]
    private int cosmeticHeadFacialHair;

    [ObservableProperty]
    private int cosmeticCapLogo;

    [ObservableProperty]
    private bool cosmeticIsMale;

    [ObservableProperty]
    private int cosmeticVoice;

    [ObservableProperty]
    private int cosmeticEyeColor;

    #endregion

    #region Flags

    [ObservableProperty]
    private ObservableCollection<FlagDisplayItem> selectedCharacterFlags = [];

    [ObservableProperty]
    private int selectedFlagIndex = -1;

    [ObservableProperty]
    private FlagDropdownItem? selectedNewFlag;

    /// <summary>
    /// Available character flags for the dropdown (excludes already-added flags).
    /// </summary>
    [ObservableProperty]
    private ObservableCollection<FlagDropdownItem> availableFlags = [];

    #endregion

    #region Profile

    private ProfileExplorer? profileExplorerHandle;

    [ObservableProperty]
    private Profile? playerProfile;

    [ObservableProperty]
    private ObservableCollection<MetaResource> profileMetaResources = [];

    [ObservableProperty]
    private int selectedMetaResourceIndex = -1;

    [ObservableProperty]
    private ObservableCollection<Talent> profileTalents = [];

    [ObservableProperty]
    private int selectedProfileTalentIndex = -1;

    [ObservableProperty]
    private string? newProfileTalentRowName;

    [ObservableProperty]
    private int newProfileTalentRank = 1;

    [ObservableProperty]
    private string? profileUserId;

    [ObservableProperty]
    private int profileDataVersion;

    // Profile (Account) Flags
    [ObservableProperty]
    private ObservableCollection<FlagDisplayItem> profileAccountFlags = [];

    [ObservableProperty]
    private int selectedAccountFlagIndex = -1;

    [ObservableProperty]
    private FlagDropdownItem? selectedNewAccountFlag;

    [ObservableProperty]
    private ObservableCollection<FlagDropdownItem> availableAccountFlags = [];

    #endregion

    #region Accolades

    private AccoladesExplorer? accoladesExplorerHandle;

    [ObservableProperty]
    private bool hasAccolades;

    [ObservableProperty]
    private ObservableCollection<AccoladeEntry> accoladeEntries = [];

    [ObservableProperty]
    private ObservableCollection<AccoladeDisplayItem> completedAccoladeItems = [];

    [ObservableProperty]
    private int completedAccoladeCount;

    [ObservableProperty]
    private int selectedAccoladeIndex = -1;

    [ObservableProperty]
    private int selectedCompletedAccoladeIndex = -1;

    [ObservableProperty]
    private string? newAccoladeRowName;

    [ObservableProperty]
    private int newAccoladePoints;

    #endregion

    #region Bestiary

    private BestiaryExplorer? bestiaryExplorerHandle;

    [ObservableProperty]
    private bool hasBestiary;

    [ObservableProperty]
    private ObservableCollection<BestiaryEntry> bestiaryEntries = [];

    [ObservableProperty]
    private int selectedBestiaryIndex = -1;

    [ObservableProperty]
    private string? newBestiaryRowName;

    [ObservableProperty]
    private int newBestiaryPoints;

    #endregion

    #region MetaInventory (Workshop Items)

    private MetaInventoryExplorer? metaInventoryExplorerHandle;

    [ObservableProperty]
    private bool hasMetaInventory;

    [ObservableProperty]
    private ObservableCollection<InventoryDisplayItem> metaInventoryItems = [];

    [ObservableProperty]
    private int selectedInventoryItemIndex = -1;

    [ObservableProperty]
    private string? newInventoryItemName;

    [ObservableProperty]
    private int newInventoryItemCount = 1;

    [ObservableProperty]
    private string? metaInventoryId;

    [ObservableProperty]
    private WorkshopItemPickerItem? selectedItemPicker;

    [ObservableProperty]
    private ObservableCollection<WorkshopItemPickerItem> workshopItemPickerList = [];

    [ObservableProperty]
    private int inventoryItemCount;

    #endregion

    #region Mounts (Pets)

    private MountsExplorer? mountsExplorerHandle;

    [ObservableProperty]
    private bool hasMounts;

    [ObservableProperty]
    private ObservableCollection<MountDisplayItem> mountDisplayItems = [];

    [ObservableProperty]
    private int selectedMountIndex = -1;

    [ObservableProperty]
    private MountDisplayItem? selectedMount;

    // Editable fields for selected mount
    [ObservableProperty]
    private string? editedMountName;

    [ObservableProperty]
    private int editedMountLevel;

    [ObservableProperty]
    private string? editedMountType;

    [ObservableProperty]
    private int mountCount;

    #endregion

    #region Loadouts

    private LoadoutsExplorer? loadoutsExplorerHandle;

    [ObservableProperty]
    private bool hasLoadouts;

    [ObservableProperty]
    private ObservableCollection<LoadoutDisplayItem> loadoutDisplayItems = [];

    [ObservableProperty]
    private int selectedLoadoutIndex = -1;

    [ObservableProperty]
    private string? newLoadoutName;

    [ObservableProperty]
    private LoadoutDisplayItem? selectedLoadout;

    [ObservableProperty]
    private ObservableCollection<LoadoutSlotDisplay> selectedLoadoutSlots = [];

    [ObservableProperty]
    private int selectedSlotIndex = -1;

    [ObservableProperty]
    private WorkshopItemPickerItem? selectedSlotItemPicker;

    [ObservableProperty]
    private int loadoutCount;

    #endregion

    #region Backup & Restore

    [ObservableProperty]
    private ObservableCollection<BackupEntry> backupList = [];

    [ObservableProperty]
    private int selectedBackupIndex = -1;

    [ObservableProperty]
    private int backupCount;

    #endregion

    #region Commands

    [RelayCommand]
    private async Task SelectGameFolderButtonClicked()
    {
        ValidGamePath = false;
        IsCharacterLoaded = false;

        // Initialize icon system from embedded manifest (idempotent)
        InitializeIcons();

        // 1. Try saved path first
        var savedPath = SettingsManager.GetSetting("GameDataPath") ?? "";
        if (GameData.ValidateGamePath(savedPath) && !GameData.IsGameInstallPath(savedPath))
        {
            GamePath = savedPath;
            ReloadGameData();
            return;
        }

        // 2. Try auto-detection from AppData
        var autoPath = GameData.AutoDetectSavePath();
        if (autoPath != null)
        {
            GamePath = autoPath;
            SettingsManager.SetSetting("GameDataPath", GamePath);
            ShowInfo("Auto-detected save folder");
            ReloadGameData();
            return;
        }

        // 3. Fall back to manual folder picker
        var selectedPath = await GetFolderFromUser("Select your Icarus PlayerData folder (AppData\\Local\\Icarus\\Saved\\PlayerData\\<SteamID>)");
        if (selectedPath == null) return;

        if (GameData.IsGameInstallPath(selectedPath))
        {
            ShowInfo("WARNING: That looks like the game install folder, not your save data! Check AppData\\Local\\Icarus\\Saved\\PlayerData\\");
            IsWarningIconVisible = true;
            Log.Warning("User selected game install path instead of save data: {Path}", selectedPath);
        }

        GamePath = selectedPath;
        SettingsManager.SetSetting("GameDataPath", GamePath);
        ReloadGameData();
    }

    [RelayCommand]
    private async Task ChangeGameFolder()
    {
        ValidGamePath = false;
        IsCharacterLoaded = false;

        var selectedPath = await GetFolderFromUser("Select your Icarus PlayerData folder (AppData\\Local\\Icarus\\Saved\\PlayerData\\<SteamID>)");
        if (selectedPath == null) return;

        if (GameData.IsGameInstallPath(selectedPath))
        {
            ShowInfo("WARNING: That looks like the game install folder, not your save data! Check AppData\\Local\\Icarus\\Saved\\PlayerData\\");
            IsWarningIconVisible = true;
            Log.Warning("User selected game install path instead of save data: {Path}", selectedPath);
        }

        GamePath = selectedPath;
        SettingsManager.SetSetting("GameDataPath", GamePath);
        ReloadGameData();
    }

    [RelayCommand]
    private void LoadSelectedCharacter()
    {
        if (CharacterList == null || SelectedCharacterIndex < 0 || SelectedCharacterIndex >= CharacterList.Count)
            return;

        IsWorking = true;
        WasDataExported = false;
        SelectedCharacter = CharacterList[SelectedCharacterIndex];
        Log.Information("Loading character: {CharacterName}", SelectedCharacter.CharacterName);

        SelectedCharacterLevel = Core.GetPlayerLevel(SelectedCharacter.XP);
        CharacterDisplayName = $"{SelectedCharacter.CharacterName} (Level {SelectedCharacterLevel})";

        // Load character values
        EditedXP = SelectedCharacter.XP;
        EditedName = SelectedCharacter.CharacterName;
        EditedIsDead = SelectedCharacter.IsDead;
        EditedIsAbandoned = SelectedCharacter.IsAbandoned;
        EditedLocation = SelectedCharacter.Location;
        EditedLastProspectId = SelectedCharacter.LastProspectId;

        // Format TimeLastPlayed (Unix timestamp)
        if (SelectedCharacter.TimeLastPlayed > 0)
        {
            try
            {
                var dt = DateTimeOffset.FromUnixTimeSeconds(SelectedCharacter.TimeLastPlayed).LocalDateTime;
                LastPlayedDisplay = dt.ToString("yyyy-MM-dd HH:mm:ss");
            }
            catch
            {
                LastPlayedDisplay = SelectedCharacter.TimeLastPlayed.ToString();
            }
        }
        else
        {
            LastPlayedDisplay = "Never";
        }

        // Load talents
        SelectedCharacterTalents.Clear();
        if (SelectedCharacter.Talents != null)
        {
            foreach (var talent in SelectedCharacter.Talents)
                SelectedCharacterTalents.Add(talent);
        }

        // Load cosmetics
        LoadCosmetics(SelectedCharacter.Cosmetic);

        // Load flags with display names
        SelectedCharacterFlags.Clear();
        if (SelectedCharacter.UnlockedFlags != null)
        {
            foreach (var flagId in SelectedCharacter.UnlockedFlags)
            {
                SelectedCharacterFlags.Add(new FlagDisplayItem
                {
                    Id = flagId,
                    Name = FlagDefinitions.GetCharacterFlagName(flagId)
                });
            }
        }
        RefreshAvailableFlags();

        // Load profile (all MetaResources dynamically + account flags)
        LoadProfileData();

        // Load meta inventory
        LoadMetaInventoryData();

        // Load accolades
        LoadAccoladesData();

        // Load bestiary
        LoadBestiaryData();

        // Load loadouts
        LoadLoadoutsData();

        // Load mounts/pets
        LoadMountsData();

        currentLoadedCharacterIndex = SelectedCharacterIndex;
        LoadText = "Load Character Data";
        IsCharacterLoaded = true;
        ShowInfo($"{CharacterDisplayName} loaded");
        Log.Information("{CharacterName} loaded", SelectedCharacter.CharacterName);
        IsWorking = false;
    }

    [RelayCommand]
    private void BackupData()
    {
        if (gameData == null) return;

        bool success = gameData.BackupData();
        if (success)
        {
            ShowInfo("Game data backed up");
            RefreshBackupList();
        }
        else
        {
            ShowInfo("Failed to backup data — check log for details");
            IsWarningIconVisible = true;
        }
    }

    [RelayCommand]
    private void RestoreBackup()
    {
        if (gameData == null || BackupList.Count == 0)
        {
            ShowInfo("No backups available to restore");
            return;
        }

        if (SelectedBackupIndex < 0 || SelectedBackupIndex >= BackupList.Count)
        {
            SelectedBackupIndex = 0;
        }

        var backupEntry = BackupList[SelectedBackupIndex];
        bool success = gameData.RestoreBackup(backupEntry.FullPath);

        if (success)
        {
            ShowInfo($"Restored backup: {backupEntry.DisplayName}");
            ReloadGameData();
        }
        else
        {
            ShowInfo("Failed to restore backup — check log for details");
            IsWarningIconVisible = true;
        }
    }

    [RelayCommand]
    private void DeleteBackup()
    {
        if (gameData == null || BackupList.Count == 0) return;
        if (SelectedBackupIndex < 0 || SelectedBackupIndex >= BackupList.Count) return;

        var backupEntry = BackupList[SelectedBackupIndex];
        try
        {
            Directory.Delete(backupEntry.FullPath, recursive: true);
            ShowInfo($"Deleted backup: {backupEntry.DisplayName}");
            RefreshBackupList();
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to delete backup {BackupPath}", backupEntry.FullPath);
            ShowInfo("Failed to delete backup — check log for details");
            IsWarningIconVisible = true;
        }
    }

    [RelayCommand]
    private void ExportData()
    {
        if (!IsCharacterLoaded) return;
        if (characterExplorerHandle == null || profileExplorerHandle == null ||
            CharacterList == null || SelectedCharacter == null || PlayerProfile == null)
            return;

        Log.Information("Exporting data");
        IsProgressVisible = true;
        IsWorking = true;

        var charName = SelectedCharacter.CharacterName ?? "Unknown";
        var userId = PlayerProfile.UserID ?? "Unknown";

        // Apply character edits
        SetCharacterValues();
        Progress = 15;

        // Export characters
        bool charSuccess = characterExplorerHandle.ExportCharacters(CharacterList);
        if (!charSuccess)
        {
            ShowInfo("Character data failed to export");
            IsWarningIconVisible = true;
            IsWorking = false;
            IsProgressVisible = false;
            return;
        }
        Progress = 35;

        // Apply and export profile
        SetProfileValues();
        bool profileSuccess = profileExplorerHandle.ExportProfile(PlayerProfile);
        if (!profileSuccess)
        {
            ShowInfo("Profile failed to export");
            IsWarningIconVisible = true;
            IsWorking = false;
            IsProgressVisible = false;
            return;
        }
        Progress = 55;

        // Export meta inventory if available
        if (metaInventoryExplorerHandle?.Inventory != null && HasMetaInventory)
        {
            SetMetaInventoryValues();
            bool invSuccess = metaInventoryExplorerHandle.ExportInventory(metaInventoryExplorerHandle.Inventory);
            if (!invSuccess)
            {
                ShowInfo("Meta inventory failed to export");
                IsWarningIconVisible = true;
            }
        }
        Progress = 65;

        // Export accolades if available
        if (accoladesExplorerHandle?.Accolades != null && HasAccolades)
        {
            SetAccoladesValues();
            bool accSuccess = accoladesExplorerHandle.ExportAccolades(accoladesExplorerHandle.Accolades);
            if (!accSuccess)
            {
                ShowInfo("Accolades failed to export");
                IsWarningIconVisible = true;
            }
        }
        Progress = 70;

        // Export bestiary if available
        if (bestiaryExplorerHandle?.Bestiary != null && HasBestiary)
        {
            SetBestiaryValues();
            bool besSuccess = bestiaryExplorerHandle.ExportBestiary(bestiaryExplorerHandle.Bestiary);
            if (!besSuccess)
            {
                ShowInfo("Bestiary data failed to export");
                IsWarningIconVisible = true;
            }
        }
        Progress = 72;

        // Export loadouts if available
        if (loadoutsExplorerHandle?.Loadouts != null && HasLoadouts)
        {
            SetLoadoutsValues();
            bool loadSuccess = loadoutsExplorerHandle.ExportLoadouts(loadoutsExplorerHandle.Loadouts);
            if (!loadSuccess)
            {
                ShowInfo("Loadouts failed to export");
                IsWarningIconVisible = true;
            }
        }
        Progress = 73;

        // Export mounts if available
        if (mountsExplorerHandle?.MountsData != null && HasMounts)
        {
            SetMountsValues();
            bool mountSuccess = mountsExplorerHandle.ExportMounts(mountsExplorerHandle.MountsData);
            if (!mountSuccess)
            {
                ShowInfo("Mounts failed to export");
                IsWarningIconVisible = true;
            }
        }
        Progress = 75;

        // Reload to verify
        LoadSelectedCharacter();
        Progress = 90;

        // Post-save verification — read back Profile.json and confirm flag count
        var verifyMsg = VerifySaveData();

        ShowInfo($"Saved — {charName} | {verifyMsg}");
        Log.Information("Post-save verification: {VerifyMsg}", verifyMsg);

        Progress = 100;
        WasDataExported = true;
        IsWorking = false;
        IsProgressVisible = false;
    }

    [RelayCommand]
    private void DuplicateCharacter()
    {
        if (characterExplorerHandle == null || CharacterList == null) return;
        characterExplorerHandle.AddCharacter(CharacterList, SelectedCharacterIndex);
        ReloadGameData();
        WasDataExported = true;
    }

    [RelayCommand]
    private void RemoveCharacter()
    {
        if (characterExplorerHandle == null || CharacterList == null) return;
        characterExplorerHandle.RemoveCharacter(CharacterList, SelectedCharacterIndex);
        ReloadGameData();
        WasDataExported = true;
    }

    [RelayCommand]
    private void AddTalent()
    {
        if (string.IsNullOrWhiteSpace(NewTalentRowName)) return;
        SelectedCharacterTalents.Add(new TalentData
        {
            RowName = NewTalentRowName,
            Rank = NewTalentRank
        });
        NewTalentRowName = "";
        NewTalentRank = 1;
    }

    [RelayCommand]
    private void RemoveTalent()
    {
        if (SelectedTalentIndex >= 0 && SelectedTalentIndex < SelectedCharacterTalents.Count)
        {
            SelectedCharacterTalents.RemoveAt(SelectedTalentIndex);
        }
    }

    [RelayCommand]
    private void AddFlag()
    {
        if (SelectedNewFlag == null) return;

        var flagId = SelectedNewFlag.Id;
        if (SelectedCharacterFlags.Any(f => f.Id == flagId))
        {
            ShowInfo($"Flag {SelectedNewFlag.DisplayName} already exists");
            return;
        }

        SelectedCharacterFlags.Add(new FlagDisplayItem
        {
            Id = flagId,
            Name = FlagDefinitions.GetCharacterFlagName(flagId)
        });
        RefreshAvailableFlags();
        SelectedNewFlag = null;
    }

    [RelayCommand]
    private void RemoveFlag()
    {
        if (SelectedFlagIndex >= 0 && SelectedFlagIndex < SelectedCharacterFlags.Count)
        {
            SelectedCharacterFlags.RemoveAt(SelectedFlagIndex);
            RefreshAvailableFlags();
        }
    }

    [RelayCommand]
    private void UnlockAllCharacterFlags()
    {
        SelectedCharacterFlags.Clear();
        foreach (var kvp in FlagDefinitions.CharacterFlags.OrderBy(k => k.Key))
        {
            SelectedCharacterFlags.Add(new FlagDisplayItem
            {
                Id = kvp.Key,
                Name = kvp.Value
            });
        }
        RefreshAvailableFlags();
        ShowInfo("All 45 character flags unlocked — save to apply");
    }

    [RelayCommand]
    private void AddInventoryItem()
    {
        // Prefer picker selection, fall back to manual text entry
        var metaRow = SelectedItemPicker?.MetaRow ?? NewInventoryItemName;
        if (string.IsNullOrWhiteSpace(metaRow)) return;

        // Check if item already exists (simple workshop items only) — if so, add to count
        var existing = MetaInventoryItems.FirstOrDefault(i =>
            string.Equals(i.RowName, metaRow, StringComparison.OrdinalIgnoreCase) &&
            i.SourceItem?.ItemStaticData == null); // Only stack simple items
        if (existing != null)
        {
            existing.Count += NewInventoryItemCount;
            if (existing.SourceItem != null)
                existing.SourceItem.Count = existing.Count;
            // Refresh display
            var idx = MetaInventoryItems.IndexOf(existing);
            MetaInventoryItems[idx] = existing;
        }
        else
        {
            var newItem = new InventoryItem
            {
                MetaRow = metaRow,
                Count = NewInventoryItemCount
            };

            MetaInventoryItems.Add(new InventoryDisplayItem
            {
                RowName = metaRow,
                DataTable = "D_WorkshopItems",
                Count = NewInventoryItemCount,
                DisplayName = WorkshopItemData.GetDisplayName(metaRow),
                SourceItem = newItem
            });
        }

        NewInventoryItemName = "";
        NewInventoryItemCount = 1;
        SelectedItemPicker = null;
        InventoryItemCount = MetaInventoryItems.Count;
    }

    [RelayCommand]
    private void RemoveInventoryItem()
    {
        if (SelectedInventoryItemIndex >= 0 && SelectedInventoryItemIndex < MetaInventoryItems.Count)
        {
            MetaInventoryItems.RemoveAt(SelectedInventoryItemIndex);
            InventoryItemCount = MetaInventoryItems.Count;
        }
    }

    [RelayCommand]
    private void AddMetaResource()
    {
        ProfileMetaResources.Add(new MetaResource { MetaRow = "NewResource", Count = 0 });
    }

    [RelayCommand]
    private void RemoveMetaResource()
    {
        if (SelectedMetaResourceIndex >= 0 && SelectedMetaResourceIndex < ProfileMetaResources.Count)
        {
            ProfileMetaResources.RemoveAt(SelectedMetaResourceIndex);
        }
    }

    [RelayCommand]
    private void AddAccountFlag()
    {
        if (SelectedNewAccountFlag == null) return;

        var flagId = SelectedNewAccountFlag.Id;
        if (ProfileAccountFlags.Any(f => f.Id == flagId))
        {
            ShowInfo($"Account flag {SelectedNewAccountFlag.DisplayName} already exists");
            return;
        }

        ProfileAccountFlags.Add(new FlagDisplayItem
        {
            Id = flagId,
            Name = FlagDefinitions.GetAccountFlagName(flagId)
        });
        RefreshAvailableAccountFlags();
        SelectedNewAccountFlag = null;
    }

    [RelayCommand]
    private void RemoveAccountFlag()
    {
        if (SelectedAccountFlagIndex >= 0 && SelectedAccountFlagIndex < ProfileAccountFlags.Count)
        {
            ProfileAccountFlags.RemoveAt(SelectedAccountFlagIndex);
            RefreshAvailableAccountFlags();
        }
    }

    [RelayCommand]
    private void UnlockAllAccountFlags()
    {
        ProfileAccountFlags.Clear();
        foreach (var kvp in FlagDefinitions.AccountFlags.OrderBy(k => k.Key))
        {
            ProfileAccountFlags.Add(new FlagDisplayItem
            {
                Id = kvp.Key,
                Name = kvp.Value
            });
        }
        RefreshAvailableAccountFlags();
        ShowInfo("All 100 account flags unlocked — save to apply");
    }

    [RelayCommand]
    private void AddProfileTalent()
    {
        if (string.IsNullOrWhiteSpace(NewProfileTalentRowName)) return;
        ProfileTalents.Add(new Talent
        {
            RowName = NewProfileTalentRowName,
            Rank = NewProfileTalentRank
        });
        NewProfileTalentRowName = "";
        NewProfileTalentRank = 1;
    }

    [RelayCommand]
    private void RemoveProfileTalent()
    {
        if (SelectedProfileTalentIndex >= 0 && SelectedProfileTalentIndex < ProfileTalents.Count)
        {
            ProfileTalents.RemoveAt(SelectedProfileTalentIndex);
        }
    }

    [RelayCommand]
    private void AddAccolade()
    {
        if (string.IsNullOrWhiteSpace(NewAccoladeRowName)) return;
        AccoladeEntries.Add(new AccoladeEntry
        {
            RowName = NewAccoladeRowName,
            NumPoints = NewAccoladePoints
        });
        NewAccoladeRowName = "";
        NewAccoladePoints = 0;
    }

    [RelayCommand]
    private void RemoveAccolade()
    {
        if (SelectedAccoladeIndex >= 0 && SelectedAccoladeIndex < AccoladeEntries.Count)
        {
            AccoladeEntries.RemoveAt(SelectedAccoladeIndex);
        }
    }

    [RelayCommand]
    private void AddBestiaryEntry()
    {
        if (string.IsNullOrWhiteSpace(NewBestiaryRowName)) return;
        BestiaryEntries.Add(new BestiaryEntry
        {
            RowName = NewBestiaryRowName,
            NumPoints = NewBestiaryPoints
        });
        NewBestiaryRowName = "";
        NewBestiaryPoints = 0;
    }

    [RelayCommand]
    private void SelectMount()
    {
        if (SelectedMountIndex < 0 || SelectedMountIndex >= MountDisplayItems.Count) return;

        SelectedMount = MountDisplayItems[SelectedMountIndex];
        EditedMountName = SelectedMount.Name;
        EditedMountLevel = SelectedMount.Level;
        EditedMountType = SelectedMount.TypeRaw;
    }

    [RelayCommand]
    private void ApplyMountEdits()
    {
        if (SelectedMount == null || SelectedMountIndex < 0) return;

        SelectedMount.Name = EditedMountName ?? "";
        SelectedMount.Level = EditedMountLevel;
        SelectedMount.TypeRaw = EditedMountType ?? "";
        SelectedMount.TypeDisplay = CreatureData.GetDisplayName(EditedMountType);
        SelectedMount.Category = CreatureData.GetCategoryLabel(EditedMountType);

        // Refresh the collection to update the DataGrid
        var idx = SelectedMountIndex;
        MountDisplayItems[idx] = SelectedMount;
        SelectedMountIndex = idx;

        ShowInfo($"Updated mount: {SelectedMount.Name}");
    }

    [RelayCommand]
    private void RemoveMount()
    {
        if (SelectedMountIndex >= 0 && SelectedMountIndex < MountDisplayItems.Count)
        {
            var name = MountDisplayItems[SelectedMountIndex].Name;
            MountDisplayItems.RemoveAt(SelectedMountIndex);
            MountCount = MountDisplayItems.Count;
            ShowInfo($"Removed mount: {name}");
        }
    }

    [RelayCommand]
    private void AddLoadout()
    {
        var name = string.IsNullOrWhiteSpace(NewLoadoutName) ? $"Loadout {LoadoutDisplayItems.Count + 1}" : NewLoadoutName;
        LoadoutDisplayItems.Add(new LoadoutDisplayItem
        {
            Name = name,
            SlotCount = 0,
            SourceEntry = new LoadoutEntry { LoadoutName = name, Slots = [] }
        });
        NewLoadoutName = "";
        LoadoutCount = LoadoutDisplayItems.Count;
    }

    [RelayCommand]
    private void RemoveLoadout()
    {
        if (SelectedLoadoutIndex >= 0 && SelectedLoadoutIndex < LoadoutDisplayItems.Count)
        {
            LoadoutDisplayItems.RemoveAt(SelectedLoadoutIndex);
            SelectedLoadoutSlots.Clear();
            SelectedSlotIndex = -1;
            SelectedLoadout = null;
            LoadoutCount = LoadoutDisplayItems.Count;
        }
    }

    partial void OnSelectedLoadoutIndexChanged(int value) => SelectLoadout();

    [RelayCommand]
    private void SelectLoadout()
    {
        if (SelectedLoadoutIndex < 0 || SelectedLoadoutIndex >= LoadoutDisplayItems.Count) return;

        SelectedLoadout = LoadoutDisplayItems[SelectedLoadoutIndex];
        SelectedLoadoutSlots.Clear();

        if (SelectedLoadout.SourceEntry?.Slots != null)
        {
            foreach (var slot in SelectedLoadout.SourceEntry.Slots)
            {
                SelectedLoadoutSlots.Add(new LoadoutSlotDisplay
                {
                    SlotIndex = slot.SlotIndex,
                    MetaRow = slot.MetaRow ?? "",
                    DisplayName = WorkshopItemData.GetDisplayName(slot.MetaRow),
                    SourceSlot = slot
                });
            }
        }
    }

    [RelayCommand]
    private void AddLoadoutSlot()
    {
        if (SelectedLoadout?.SourceEntry == null) return;

        var metaRow = SelectedSlotItemPicker?.MetaRow ?? "";
        if (string.IsNullOrWhiteSpace(metaRow)) return;

        var slotIndex = SelectedLoadoutSlots.Count;
        var newSlot = new LoadoutSlot { MetaRow = metaRow, SlotIndex = slotIndex };
        SelectedLoadout.SourceEntry.Slots ??= [];
        SelectedLoadout.SourceEntry.Slots.Add(newSlot);

        SelectedLoadoutSlots.Add(new LoadoutSlotDisplay
        {
            SlotIndex = slotIndex,
            MetaRow = metaRow,
            DisplayName = WorkshopItemData.GetDisplayName(metaRow),
            SourceSlot = newSlot
        });

        SelectedLoadout.SlotCount = SelectedLoadoutSlots.Count;
        SelectedSlotItemPicker = null;
    }

    [RelayCommand]
    private void RemoveLoadoutSlot()
    {
        if (SelectedSlotIndex < 0 || SelectedSlotIndex >= SelectedLoadoutSlots.Count) return;
        if (SelectedLoadout?.SourceEntry?.Slots == null) return;

        var slot = SelectedLoadoutSlots[SelectedSlotIndex];
        if (slot.SourceSlot != null)
            SelectedLoadout.SourceEntry.Slots.Remove(slot.SourceSlot);

        SelectedLoadoutSlots.RemoveAt(SelectedSlotIndex);
        SelectedSlotIndex = -1;
        SelectedLoadout.SlotCount = SelectedLoadoutSlots.Count;
    }

    [RelayCommand]
    private void RemoveBestiaryEntry()
    {
        if (SelectedBestiaryIndex >= 0 && SelectedBestiaryIndex < BestiaryEntries.Count)
        {
            BestiaryEntries.RemoveAt(SelectedBestiaryIndex);
        }
    }

    [RelayCommand]
    private void OpenLogFolder()
    {
        var logDir = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "IcarusToolkit", "logs");

        if (Directory.Exists(logDir))
        {
            Process.Start(new ProcessStartInfo
            {
                FileName = logDir,
                UseShellExecute = true
            });
        }
        IsWarningIconVisible = false;
    }

    #endregion

    #region Private Methods

    partial void OnSelectedCharacterIndexChanged(int value)
    {
        if (value != currentLoadedCharacterIndex)
            LoadText = "Load Character Data*";
        else
            LoadText = "Load Character Data";
    }

    partial void OnEditModeChanged(bool value)
    {
        if (!WasDataExported && value == false && IsCharacterLoaded)
        {
            LoadSelectedCharacter();
        }
    }

    private async Task<string?> GetFolderFromUser(string title)
    {
        if (MainWindow.MainWindowHandle == null) return null;

        var topLevel = TopLevel.GetTopLevel(MainWindow.MainWindowHandle);
        if (topLevel == null) return null;

        var folders = await topLevel.StorageProvider.OpenFolderPickerAsync(new FolderPickerOpenOptions
        {
            Title = title,
            AllowMultiple = false
        });

        if (folders.Count > 0)
        {
            return folders[0].Path.LocalPath;
        }

        ShowInfo("Folder not selected");
        return null;
    }

    private void ReloadGameData()
    {
        if (string.IsNullOrEmpty(GamePath)) return;

        IsWorking = true;
        Log.Information("Loading game data from {GamePath}", GamePath);

        // Check if path looks like game install instead of save data
        if (GameData.IsGameInstallPath(GamePath))
        {
            IsPathWarningVisible = true;
            PathWarningText = "WARNING: This path looks like the game installation folder, NOT your save data! " +
                              "Your saves are at: %LocalAppData%\\Icarus\\Saved\\PlayerData\\<YourSteamID>\\ " +
                              "Changes here won't affect your game. Click 'Change Folder' and navigate to the correct path. " +
                              "TIP: Disable Steam Cloud sync for Icarus to prevent saves being overwritten.";
        }
        else
        {
            IsPathWarningVisible = false;
            PathWarningText = null;
        }

        gameData = new GameData(GamePath);

        if (gameData.ValidGamePath)
        {
            characterExplorerHandle = gameData.GetCharacters();
            CharacterList = characterExplorerHandle.Characters;

            profileExplorerHandle = gameData.GetProfile();
            PlayerProfile = profileExplorerHandle.PlayerProfile;

            // Load meta inventory if available
            metaInventoryExplorerHandle = gameData.GetMetaInventory();
            HasMetaInventory = gameData.HasMetaInventory;

            // Load accolades if available
            accoladesExplorerHandle = gameData.GetAccolades();
            HasAccolades = gameData.HasAccolades;

            // Load bestiary if available
            bestiaryExplorerHandle = gameData.GetBestiary();
            HasBestiary = gameData.HasBestiary;

            // Load loadouts if available
            loadoutsExplorerHandle = gameData.GetLoadouts();
            HasLoadouts = gameData.HasLoadouts;

            // Load mounts/pets if available
            mountsExplorerHandle = gameData.GetMounts();
            HasMounts = gameData.HasMounts;

            SelectedCharacterIndex = 0;
            ValidGamePath = true;
            ShowInfo("Game data loaded");
            IsWorking = false;

            RefreshBackupList();
            LoadSelectedCharacter();
        }
        else
        {
            Log.Error("{GamePath} was not a valid game data path", GamePath);
            IsWorking = false;
            ShowInfo("Selected path was not a valid game data directory");
        }
    }

    private void LoadProfileData()
    {
        ProfileMetaResources.Clear();
        ProfileTalents.Clear();
        ProfileAccountFlags.Clear();

        if (PlayerProfile != null)
        {
            if (PlayerProfile.MetaResources != null)
            {
                foreach (var resource in PlayerProfile.MetaResources)
                    ProfileMetaResources.Add(resource);
            }

            ProfileUserId = PlayerProfile.UserID;
            ProfileDataVersion = PlayerProfile.DataVersion;

            if (PlayerProfile.Talents != null)
            {
                foreach (var talent in PlayerProfile.Talents)
                    ProfileTalents.Add(talent);
            }

            // Load account flags with display names
            if (PlayerProfile.UnlockedFlags != null)
            {
                foreach (var flagId in PlayerProfile.UnlockedFlags)
                {
                    ProfileAccountFlags.Add(new FlagDisplayItem
                    {
                        Id = flagId,
                        Name = FlagDefinitions.GetAccountFlagName(flagId)
                    });
                }
            }
            RefreshAvailableAccountFlags();
        }
        else
        {
            ProfileUserId = null;
            ProfileDataVersion = 0;
            Log.Warning("PlayerProfile was null during character load — profile fields reset");
        }
    }

    private void LoadMetaInventoryData()
    {
        MetaInventoryItems.Clear();

        if (metaInventoryExplorerHandle?.Inventory != null)
        {
            MetaInventoryId = metaInventoryExplorerHandle.Inventory.InventoryID;

            if (metaInventoryExplorerHandle.Inventory.Items != null)
            {
                foreach (var item in metaInventoryExplorerHandle.Inventory.Items)
                {
                    var rowName = item.DisplayRowName;
                    var dataTable = !string.IsNullOrEmpty(item.MetaRow)
                        ? "D_WorkshopItems"
                        : item.ItemStaticData?.DataTableName ?? "";

                    // Resolve display name: try WorkshopItemData first, then clean up the RowName
                    var displayName = !string.IsNullOrEmpty(item.MetaRow)
                        ? WorkshopItemData.GetDisplayName(item.MetaRow)
                        : CleanRowName(item.ItemStaticData?.RowName);

                    // Format durability as percentage (max is typically 12,700,000 for legendary)
                    var durStr = "";
                    if (item.Durability >= 0)
                    {
                        durStr = $"{item.Durability:N0}";
                    }

                    // Collect alteration names
                    var alterations = "";
                    if (item.CustomProperties?.Alterations is { Count: > 0 })
                    {
                        alterations = string.Join(", ",
                            item.CustomProperties.Alterations
                                .Where(a => !string.IsNullOrEmpty(a.Value))
                                .Select(a => a.Value));
                    }

                    MetaInventoryItems.Add(new InventoryDisplayItem
                    {
                        DisplayName = displayName,
                        RowName = rowName,
                        DataTable = dataTable,
                        Count = item.EffectiveCount,
                        Durability = durStr,
                        Alterations = alterations,
                        SourceItem = item
                    });
                }
            }
        }
        else
        {
            MetaInventoryId = null;
        }

        InventoryItemCount = MetaInventoryItems.Count;

        // Populate item picker
        WorkshopItemPickerList.Clear();
        foreach (var (metaRow, displayName, category) in WorkshopItemData.KnownItems)
        {
            WorkshopItemPickerList.Add(new WorkshopItemPickerItem
            {
                MetaRow = metaRow,
                DisplayText = $"[{category}] {displayName} ({metaRow})"
            });
        }

        // Fetch icons from GitHub in the background (non-blocking)
        if (_iconResolver.IsInitialized)
        {
            _ = LoadIconsAsync();
        }
    }

    /// <summary>
    /// Download icons from GitHub for all inventory items in the background.
    /// Updates each item's IconImage as downloads complete.
    /// </summary>
    private async Task LoadIconsAsync()
    {
        foreach (var item in MetaInventoryItems.ToList())
        {
            try
            {
                var icon = await _iconResolver.GetIconAsync(item.RowName);
                if (icon != null)
                {
                    await Dispatcher.UIThread.InvokeAsync(() => item.IconImage = icon);
                }
            }
            catch (Exception ex)
            {
                Log.Debug("Icon load failed for {RowName}: {Error}", item.RowName, ex.Message);
            }
        }
    }

    /// <summary>
    /// Cleans up a D_ItemsStatic RowName into a readable display name.
    /// e.g. "LegendaryWeapon_Sandworm_Crossbow" -> "Legendary Sandworm Crossbow"
    /// </summary>
    private static string CleanRowName(string? rowName)
    {
        if (string.IsNullOrEmpty(rowName)) return "Unknown";

        var name = rowName
            .Replace("LegendaryWeapon_", "Legendary ")
            .Replace("Dev_", "[Dev] ")
            .Replace("Test_", "[Test] ")
            .Replace("Proxy_", "")
            .Replace('_', ' ');

        return name;
    }

    private void RefreshBackupList()
    {
        BackupList.Clear();
        if (gameData == null) return;

        foreach (var backupPath in gameData.GetBackups())
        {
            var dirName = Path.GetFileName(backupPath);
            var fileCount = 0;
            try { fileCount = Directory.GetFiles(backupPath, "*.json").Length; }
            catch { /* ignore */ }

            BackupList.Add(new BackupEntry
            {
                FullPath = backupPath,
                DisplayName = dirName ?? backupPath,
                FileCount = fileCount
            });
        }

        BackupCount = BackupList.Count;
    }

    private void SetCharacterValues()
    {
        if (SelectedCharacter == null || CharacterList == null) return;
        if (SelectedCharacterIndex < 0 || SelectedCharacterIndex >= CharacterList.Count) return;

        SelectedCharacter.CharacterName = EditedName ?? "";
        SelectedCharacter.XP = EditedXP;
        SelectedCharacter.IsDead = EditedIsDead;
        SelectedCharacter.IsAbandoned = EditedIsAbandoned;
        SelectedCharacter.Location = EditedLocation ?? "";
        SelectedCharacter.LastProspectId = EditedLastProspectId ?? "";

        // Apply talents
        SelectedCharacter.Talents = [.. SelectedCharacterTalents];

        // Apply cosmetics
        SaveCosmetics(SelectedCharacter);

        // Apply flags (convert display items back to int list)
        SelectedCharacter.UnlockedFlags = SelectedCharacterFlags.Select(f => f.Id).ToList();

        Log.Information("Set character values for {CharacterName}", SelectedCharacter.CharacterName);
        CharacterList[SelectedCharacterIndex] = SelectedCharacter;
    }

    private void SetProfileValues()
    {
        if (PlayerProfile == null) return;

        // Apply all meta resources from the editable collection
        PlayerProfile.MetaResources = [.. ProfileMetaResources];

        // Apply profile talents
        PlayerProfile.Talents = [.. ProfileTalents];

        // Apply account flags (convert display items back to int list)
        PlayerProfile.UnlockedFlags = ProfileAccountFlags.Select(f => f.Id).ToList();

        Log.Information("Set profile values (flags: {FlagCount})", PlayerProfile.UnlockedFlags.Count);
    }

    private void SetMetaInventoryValues()
    {
        if (metaInventoryExplorerHandle?.Inventory == null) return;

        // Round-trip: use SourceItem references to preserve full item data.
        // Only update fields that the user can edit (count for simple items).
        var items = new List<InventoryItem>();
        foreach (var displayItem in MetaInventoryItems)
        {
            if (displayItem.SourceItem != null)
            {
                // Preserve the original item — it has all the complex data
                items.Add(displayItem.SourceItem);
            }
            else
            {
                // New item added via picker — create a simple workshop-style item
                items.Add(new InventoryItem
                {
                    MetaRow = displayItem.RowName,
                    Count = displayItem.Count
                });
            }
        }

        metaInventoryExplorerHandle.Inventory.Items = items;
        Log.Information("Set meta inventory values ({ItemCount} items)", items.Count);
    }

    private void LoadCosmetics(CosmeticData? cosmetic)
    {
        if (cosmetic == null)
        {
            CosmeticHead = 0;
            CosmeticHair = 0;
            CosmeticHairColor = 0;
            CosmeticBody = 0;
            CosmeticBodyColor = 0;
            CosmeticSkinTone = 0;
            CosmeticHeadTattoo = 0;
            CosmeticHeadScar = 0;
            CosmeticHeadFacialHair = 0;
            CosmeticCapLogo = 0;
            CosmeticIsMale = false;
            CosmeticVoice = 0;
            CosmeticEyeColor = 0;
            return;
        }

        CosmeticHead = cosmetic.Customization_Head;
        CosmeticHair = cosmetic.Customization_Hair;
        CosmeticHairColor = cosmetic.Customization_HairColor;
        CosmeticBody = cosmetic.Customization_Body;
        CosmeticBodyColor = cosmetic.Customization_BodyColor;
        CosmeticSkinTone = cosmetic.Customization_SkinTone;
        CosmeticHeadTattoo = cosmetic.Customization_HeadTattoo;
        CosmeticHeadScar = cosmetic.Customization_HeadScar;
        CosmeticHeadFacialHair = cosmetic.Customization_HeadFacialHair;
        CosmeticCapLogo = cosmetic.Customization_CapLogo;
        CosmeticIsMale = cosmetic.IsMale;
        CosmeticVoice = cosmetic.Customization_Voice;
        CosmeticEyeColor = cosmetic.Customization_EyeColor;
    }

    private void SaveCosmetics(Character character)
    {
        character.Cosmetic ??= new CosmeticData();
        character.Cosmetic.Customization_Head = CosmeticHead;
        character.Cosmetic.Customization_Hair = CosmeticHair;
        character.Cosmetic.Customization_HairColor = CosmeticHairColor;
        character.Cosmetic.Customization_Body = CosmeticBody;
        character.Cosmetic.Customization_BodyColor = CosmeticBodyColor;
        character.Cosmetic.Customization_SkinTone = CosmeticSkinTone;
        character.Cosmetic.Customization_HeadTattoo = CosmeticHeadTattoo;
        character.Cosmetic.Customization_HeadScar = CosmeticHeadScar;
        character.Cosmetic.Customization_HeadFacialHair = CosmeticHeadFacialHair;
        character.Cosmetic.Customization_CapLogo = CosmeticCapLogo;
        character.Cosmetic.IsMale = CosmeticIsMale;
        character.Cosmetic.Customization_Voice = CosmeticVoice;
        character.Cosmetic.Customization_EyeColor = CosmeticEyeColor;
    }

    private void RefreshAvailableFlags()
    {
        var existingIds = SelectedCharacterFlags.Select(f => f.Id).ToHashSet();
        AvailableFlags.Clear();
        foreach (var kvp in FlagDefinitions.CharacterFlags.OrderBy(k => k.Key))
        {
            if (!existingIds.Contains(kvp.Key))
            {
                AvailableFlags.Add(new FlagDropdownItem
                {
                    Id = kvp.Key,
                    DisplayName = $"{kvp.Key}: {kvp.Value}"
                });
            }
        }
    }

    private void RefreshAvailableAccountFlags()
    {
        var existingIds = ProfileAccountFlags.Select(f => f.Id).ToHashSet();
        AvailableAccountFlags.Clear();
        foreach (var kvp in FlagDefinitions.AccountFlags.OrderBy(k => k.Key))
        {
            if (!existingIds.Contains(kvp.Key))
            {
                AvailableAccountFlags.Add(new FlagDropdownItem
                {
                    Id = kvp.Key,
                    DisplayName = $"{kvp.Key}: {kvp.Value}"
                });
            }
        }
    }

    private void LoadAccoladesData()
    {
        AccoladeEntries.Clear();
        CompletedAccoladeItems.Clear();

        if (accoladesExplorerHandle?.Accolades == null) return;

        // In-progress accolades
        if (accoladesExplorerHandle.Accolades.Accolades != null)
        {
            foreach (var entry in accoladesExplorerHandle.Accolades.Accolades)
                AccoladeEntries.Add(entry);
        }

        // Completed accolades — build display models with names, descriptions, icons
        if (accoladesExplorerHandle.Accolades.CompletedAccolades != null)
        {
            foreach (var completed in accoladesExplorerHandle.Accolades.CompletedAccolades)
            {
                var rowName = completed.Accolade?.RowName ?? "Unknown";
                var info = AccoladeData.GetInfo(rowName);

                // Parse the timestamp "2023.01.03-06.27.38" → readable date
                var dateDisplay = FormatAccoladeDate(completed.TimeCompleted);

                CompletedAccoladeItems.Add(new AccoladeDisplayItem
                {
                    RowName = rowName,
                    DisplayName = info.DisplayName,
                    Description = info.Description,
                    Category = info.Category.ToString(),
                    CompletedDate = dateDisplay,
                    ProspectId = completed.ProspectID ?? "",
                    SourceEntry = completed
                });
            }
        }

        CompletedAccoladeCount = CompletedAccoladeItems.Count;
    }

    /// <summary>
    /// Parse "2023.01.03-06.27.38" → "Jan 3, 2023 6:27 AM"
    /// </summary>
    private static string FormatAccoladeDate(string? timestamp)
    {
        if (string.IsNullOrEmpty(timestamp)) return "";
        try
        {
            // Format: "2023.01.03-06.27.38"
            var parts = timestamp.Split('-');
            if (parts.Length >= 2)
            {
                var dateParts = parts[0].Split('.');
                var timeParts = parts[1].Split('.');
                if (dateParts.Length == 3 && timeParts.Length >= 2)
                {
                    var dt = new DateTime(
                        int.Parse(dateParts[0]), int.Parse(dateParts[1]), int.Parse(dateParts[2]),
                        int.Parse(timeParts[0]), int.Parse(timeParts[1]),
                        timeParts.Length > 2 ? int.Parse(timeParts[2]) : 0);
                    return dt.ToString("MMM d, yyyy");
                }
            }
        }
        catch { /* fall through */ }
        return timestamp;
    }

    private void LoadBestiaryData()
    {
        BestiaryEntries.Clear();

        if (bestiaryExplorerHandle?.Bestiary?.Entries != null)
        {
            foreach (var entry in bestiaryExplorerHandle.Bestiary.Entries)
                BestiaryEntries.Add(entry);
        }
    }

    private void SetAccoladesValues()
    {
        if (accoladesExplorerHandle?.Accolades == null) return;
        accoladesExplorerHandle.Accolades.Accolades = [.. AccoladeEntries];
        Log.Information("Set accolade values ({Count} entries)", AccoladeEntries.Count);
    }

    private void SetBestiaryValues()
    {
        if (bestiaryExplorerHandle?.Bestiary == null) return;
        bestiaryExplorerHandle.Bestiary.Entries = [.. BestiaryEntries];
        Log.Information("Set bestiary values ({Count} entries)", BestiaryEntries.Count);
    }

    private void LoadLoadoutsData()
    {
        LoadoutDisplayItems.Clear();
        SelectedLoadoutSlots.Clear();
        SelectedLoadout = null;

        if (loadoutsExplorerHandle?.Loadouts?.Loadouts != null)
        {
            foreach (var entry in loadoutsExplorerHandle.Loadouts.Loadouts)
            {
                LoadoutDisplayItems.Add(new LoadoutDisplayItem
                {
                    Name = entry.LoadoutName ?? "Unnamed",
                    SlotCount = entry.Slots?.Count ?? 0,
                    SourceEntry = entry
                });
            }
        }

        LoadoutCount = LoadoutDisplayItems.Count;
    }

    private void SetLoadoutsValues()
    {
        if (loadoutsExplorerHandle?.Loadouts == null) return;

        var entries = new List<LoadoutEntry>();
        foreach (var item in LoadoutDisplayItems)
        {
            if (item.SourceEntry != null)
            {
                item.SourceEntry.LoadoutName = item.Name;
                entries.Add(item.SourceEntry);
            }
        }

        loadoutsExplorerHandle.Loadouts.Loadouts = entries;
        Log.Information("Set loadout values ({Count} entries)", entries.Count);
    }

    private void LoadMountsData()
    {
        MountDisplayItems.Clear();
        SelectedMount = null;

        if (mountsExplorerHandle?.MountsData?.SavedMounts != null)
        {
            foreach (var mount in mountsExplorerHandle.MountsData.SavedMounts)
            {
                MountDisplayItems.Add(new MountDisplayItem
                {
                    Name = mount.MountName ?? "Unnamed",
                    Level = mount.MountLevel,
                    TypeRaw = mount.MountType ?? "Unknown",
                    TypeDisplay = CreatureData.GetDisplayName(mount.MountType),
                    Category = CreatureData.GetCategoryLabel(mount.MountType),
                    BlobSize = mount.RecorderBlob?.BinaryData?.Count ?? 0,
                    SourceEntry = mount
                });
            }
        }

        MountCount = MountDisplayItems.Count;
    }

    private void SetMountsValues()
    {
        if (mountsExplorerHandle?.MountsData == null) return;

        // Write display items back to mount entries
        var updatedMounts = new List<MountEntry>();
        foreach (var item in MountDisplayItems)
        {
            if (item.SourceEntry != null)
            {
                item.SourceEntry.MountName = item.Name;
                item.SourceEntry.MountLevel = item.Level;
                item.SourceEntry.MountType = item.TypeRaw;
                updatedMounts.Add(item.SourceEntry);
            }
        }

        mountsExplorerHandle.MountsData.SavedMounts = updatedMounts;
        Log.Information("Set mount values ({Count} entries)", updatedMounts.Count);
    }

    /// <summary>
    /// Reads back the saved Profile.json and Characters.json to verify the data was actually written.
    /// Returns a summary string for the status bar.
    /// </summary>
    private string VerifySaveData()
    {
        try
        {
            if (gameData == null) return "verification skipped";

            // Re-read profile to confirm flags
            var verifyProfile = gameData.GetProfile();
            var profileFlagCount = verifyProfile.PlayerProfile?.UnlockedFlags?.Count ?? 0;

            // Re-read characters to confirm character flags
            var verifyChars = gameData.GetCharacters();
            var charFlagCount = 0;
            if (verifyChars.Characters.Count > SelectedCharacterIndex && SelectedCharacterIndex >= 0)
            {
                charFlagCount = verifyChars.Characters[SelectedCharacterIndex].UnlockedFlags?.Count ?? 0;
            }

            return $"Account flags: {profileFlagCount} | Char flags: {charFlagCount}";
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Post-save verification failed");
            return "verification failed — check logs";
        }
    }

    private void ShowInfo(string message)
    {
        InformationString = message;
        IsInformationStringVisible = true;

        if (_informationStringTimer == null)
        {
            _informationStringTimer = new DispatcherTimer
            {
                Interval = TimeSpan.FromSeconds(5)
            };
            _informationStringTimer.Tick += OnInfoTimerTick;
        }

        _informationStringTimer.Stop();
        _informationStringTimer.Start();
    }

    private void OnInfoTimerTick(object? sender, EventArgs e)
    {
        IsInformationStringVisible = false;
        _informationStringTimer?.Stop();
    }

    #endregion
}

/// <summary>
/// Display model for backup entries shown in the UI.
/// </summary>
public class BackupEntry
{
    public string FullPath { get; set; } = "";
    public string DisplayName { get; set; } = "";
    public int FileCount { get; set; }
}

/// <summary>
/// Display model for completed accolades with resolved names, icons, and dates.
/// Uses ObservableObject so icons can load asynchronously from GitHub.
/// </summary>
public partial class AccoladeDisplayItem : ObservableObject
{
    public string RowName { get; set; } = "";
    public string DisplayName { get; set; } = "";
    public string Description { get; set; } = "";
    public string Category { get; set; } = "";
    public string CompletedDate { get; set; } = "";
    public string ProspectId { get; set; } = "";

    [ObservableProperty]
    private Avalonia.Media.Imaging.Bitmap? iconImage;

    /// <summary>Reference to original for round-trip preservation.</summary>
    public CompletedAccoladeEntry? SourceEntry { get; set; }
}

/// <summary>
/// Display model for flags in the DataGrid — shows ID and resolved name.
/// </summary>
public class FlagDisplayItem
{
    public int Id { get; set; }
    public string Name { get; set; } = "";
}

/// <summary>
/// Item for the flag selection dropdown.
/// </summary>
public class FlagDropdownItem
{
    public int Id { get; set; }
    public string DisplayName { get; set; } = "";

    public override string ToString() => DisplayName;
}

/// <summary>
/// Display model for workshop inventory items.
/// Handles both simple workshop items (MetaRow set) and full item instances (ItemStaticData).
/// Uses ObservableObject so IconImage can update after initial load.
/// </summary>
public partial class InventoryDisplayItem : ObservableObject
{
    /// <summary>Display name resolved from MetaRow or ItemStaticData.RowName.</summary>
    public string DisplayName { get; set; } = "";

    /// <summary>The row identifier — MetaRow for workshop items, RowName for full items.</summary>
    public string RowName { get; set; } = "";

    /// <summary>Source table — "D_WorkshopItems" or "D_ItemsStatic".</summary>
    public string DataTable { get; set; } = "";

    /// <summary>Stack count.</summary>
    public int Count { get; set; }

    /// <summary>Durability (displayed as percentage). -1 if not applicable.</summary>
    public string Durability { get; set; } = "";

    /// <summary>Alteration/upgrade names if any.</summary>
    public string Alterations { get; set; } = "";

    /// <summary>Item icon loaded from extracted game icons.</summary>
    [ObservableProperty]
    private Avalonia.Media.Imaging.Bitmap? iconImage;

    /// <summary>Reference to original item for preserving all data during round-trip.</summary>
    public InventoryItem? SourceItem { get; set; }
}

/// <summary>
/// Item for the workshop item picker dropdown.
/// </summary>
public class WorkshopItemPickerItem
{
    public string MetaRow { get; set; } = "";
    public string DisplayText { get; set; } = "";

    public override string ToString() => DisplayText;
}

/// <summary>
/// Display model for loadout entries.
/// </summary>
public class LoadoutDisplayItem
{
    public string Name { get; set; } = "";
    public int SlotCount { get; set; }
    public LoadoutEntry? SourceEntry { get; set; }
}

/// <summary>
/// Display model for a single slot within a loadout.
/// </summary>
public class LoadoutSlotDisplay
{
    public int SlotIndex { get; set; }
    public string MetaRow { get; set; } = "";
    public string DisplayName { get; set; } = "";
    public LoadoutSlot? SourceSlot { get; set; }
}

/// <summary>
/// Display model for pets/mounts in the DataGrid.
/// Maps between the raw MountEntry and human-friendly display values.
/// </summary>
public class MountDisplayItem
{
    public string Name { get; set; } = "";
    public int Level { get; set; }
    public string TypeRaw { get; set; } = "";
    public string TypeDisplay { get; set; } = "";
    public string Category { get; set; } = "";
    public int BlobSize { get; set; }

    /// <summary>
    /// Reference to the original MountEntry for round-trip serialization.
    /// This preserves the RecorderBlob binary data during edits.
    /// </summary>
    public MountEntry? SourceEntry { get; set; }
}
