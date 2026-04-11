using Avalonia.Controls;
using Serilog;

namespace Icarus_Toolkit.Views;

public partial class MainWindow : Window
{
    public static MainWindow? MainWindowHandle { get; private set; }

    public MainWindow()
    {
        InitializeComponent();
        MainWindowHandle = this;
        Log.Information("Application start");
    }
}
