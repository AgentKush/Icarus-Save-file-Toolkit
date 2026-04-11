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
    private ObservableCollection<int> selectedCharacterFlags = [];

    [ObservableProperty]
    private int selectedFlagIndex = -1;

    [ObservableProperty]
    private int newFlagId;

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
    private string? profileUserId;

    [ObservableProperty]
    private int profileDataVersion;

    #endregion

    #region MetaInventory (Workshop Items)

    private MetaInventoryExplorer? metaInventoryExplorerHandle;

    [ObservableProperty]
    private bool hasMetaInventory;

    [ObservableProperty]
    private ObservableCollection<InventoryItem> metaInventoryItems = [];

    [ObservableProperty]
    private int selectedInventoryItemIndex = -1;

    [ObservableProperty]
    private string? newInventoryItemName;

    [ObservableProperty]
    private int newInventoryItemCount = 1;

    [ObservableProperty]
    private string? metaInventoryId;

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

        var savedPath = SettingsManager.GetSetting("GameDataPath") ?? "";
        if (GameData.ValidateGamePath(savedPath))
        {
            GamePath = savedPath;
        }
        else
        {
            var selectedPath = await GetFolderFromUser("Select Game Data Folder");
            if (selectedPath == null) return;
            GamePath = selectedPath;
            SettingsManager.SetSetting("GameDataPath", GamePath);
        }

        ReloadGameData();
    }

    [RelayCommand]
    private async Task ChangeGameFolder()
    {
        ValidGamePath = false;
        IsCharacterLoaded = false;

        var selectedPath = await GetFolderFromUser("Select Game Data Folder");
        if (selectedPath == null) return;
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

        // Load flags
        SelectedCharacterFlags.Clear();
        if (SelectedCharacter.UnlockedFlags != null)
        {
            foreach (var flag in SelectedCharacter.UnlockedFlags)
                SelectedCharacterFlags.Add(flag);
        }

        // Load profile (all MetaResources dynamically)
        LoadProfileData();

        // Load meta inventory
        LoadMetaInventoryData();

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
                // Non-critical: continue with reload
            }
        }
        Progress = 75;

        // Reload to verify
        LoadSelectedCharacter();
        ShowInfo($"Saved — {charName} | User #{userId}");

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
        if (!SelectedCharacterFlags.Contains(NewFlagId))
        {
            SelectedCharacterFlags.Add(NewFlagId);
            NewFlagId = 0;
        }
        else
        {
            ShowInfo($"Flag {NewFlagId} already exists");
        }
    }

    [RelayCommand]
    private void RemoveFlag()
    {
        if (SelectedFlagIndex >= 0 && SelectedFlagIndex < SelectedCharacterFlags.Count)
        {
            SelectedCharacterFlags.RemoveAt(SelectedFlagIndex);
        }
    }

    [RelayCommand]
    private void AddInventoryItem()
    {
        if (string.IsNullOrWhiteSpace(NewInventoryItemName)) return;
        MetaInventoryItems.Add(new InventoryItem
        {
            MetaRow = NewInventoryItemName,
            Count = NewInventoryItemCount
        });
        NewInventoryItemName = "";
        NewInventoryItemCount = 1;
    }

    [RelayCommand]
    private void RemoveInventoryItem()
    {
        if (SelectedInventoryItemIndex >= 0 && SelectedInventoryItemIndex < MetaInventoryItems.Count)
        {
            MetaInventoryItems.RemoveAt(SelectedInventoryItemIndex);
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
                    MetaInventoryItems.Add(item);
            }
        }
        else
        {
            MetaInventoryId = null;
        }
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

        // Apply flags
        SelectedCharacter.UnlockedFlags = [.. SelectedCharacterFlags];

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

        Log.Information("Set profile values");
    }

    private void SetMetaInventoryValues()
    {
        if (metaInventoryExplorerHandle?.Inventory == null) return;

        metaInventoryExplorerHandle.Inventory.Items = [.. MetaInventoryItems];

        Log.Information("Set meta inventory values ({ItemCount} items)", MetaInventoryItems.Count);
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
