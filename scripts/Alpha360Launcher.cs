using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Threading;

[assembly: AssemblyTitle("Alpha360 Terminal")]
[assembly: AssemblyDescription("Institutional Indian Equities Terminal & Live Signal Radar")]
[assembly: AssemblyCompany("Alpha360 Technologies")]
[assembly: AssemblyProduct("Alpha360 Terminal")]
[assembly: AssemblyCopyright("Copyright © 2026 Alpha360 Technologies")]
[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]

namespace Alpha360
{
    class Program
    {
        [DllImport("user32.dll")]
        private static extern bool SetForegroundWindow(IntPtr hWnd);

        [DllImport("user32.dll")]
        private static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);

        private const int SW_RESTORE = 9;
        private const string SERVER_HEALTH_URL = "http://127.0.0.1:8765/api/health";
        private const string APP_URL = "http://127.0.0.1:8765/app";

        [STAThread]
        static void Main(string[] args)
        {
            try
            {
                string appDir = AppDomain.CurrentDomain.BaseDirectory;
                
                // 1. Ensure backend server is running
                if (!IsServerResponsive(SERVER_HEALTH_URL))
                {
                    StartBackendServer(appDir);
                    
                    // Wait up to 6 seconds for server readiness
                    for (int i = 0; i < 30; i++)
                    {
                        Thread.Sleep(200);
                        if (IsServerResponsive(SERVER_HEALTH_URL))
                        {
                            break;
                        }
                    }
                }

                // 2. Determine target URL (default is Flutter terminal /app)
                string targetUrl = APP_URL;
                if (args.Length > 0 && args[0].ToLower() == "--dashboard")
                {
                    targetUrl = "http://127.0.0.1:8765/dashboards/Advance_Technical_Analysis_424_Stocks.html";
                }

                // 3. Launch dedicated standalone desktop window
                LaunchDesktopWindow(targetUrl);
            }
            catch (Exception ex)
            {
                // Fallback: log error if any
                try
                {
                    File.AppendAllText("launcher_error.log", DateTime.Now.ToString() + ": " + ex.ToString() + Environment.NewLine);
                }
                catch { }
            }
        }

        private static bool IsServerResponsive(string url)
        {
            try
            {
                HttpWebRequest request = (HttpWebRequest)WebRequest.Create(url);
                request.Timeout = 1200;
                request.Method = "GET";
                using (HttpWebResponse response = (HttpWebResponse)request.GetResponse())
                {
                    return response.StatusCode == HttpStatusCode.OK;
                }
            }
            catch
            {
                return false;
            }
        }

        private static void StartBackendServer(string baseDir)
        {
            string serverScript = Path.Combine(baseDir, "live_price_server.py");
            if (!File.Exists(serverScript))
            {
                return;
            }

            ProcessStartInfo startInfo = new ProcessStartInfo();
            startInfo.FileName = "python.exe";
            startInfo.Arguments = "\"" + serverScript + "\"";
            startInfo.WorkingDirectory = baseDir;
            startInfo.WindowStyle = ProcessWindowStyle.Hidden;
            startInfo.CreateNoWindow = true;
            startInfo.UseShellExecute = false;

            try
            {
                Process.Start(startInfo);
            }
            catch
            {
                // Try py launcher fallback
                startInfo.FileName = "py.exe";
                try { Process.Start(startInfo); } catch { }
            }
        }

        private static void LaunchDesktopWindow(string url)
        {
            // Edge in standalone app mode is the cleanest Windows native desktop experience
            string[] browserPaths = new string[]
            {
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), @"Microsoft\Edge\Application\msedge.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), @"Microsoft\Edge\Application\msedge.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), @"Google\Chrome\Application\chrome.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), @"Google\Chrome\Application\chrome.exe")
            };

            foreach (string path in browserPaths)
            {
                if (File.Exists(path))
                {
                    ProcessStartInfo appWindowInfo = new ProcessStartInfo();
                    appWindowInfo.FileName = path;
                    appWindowInfo.Arguments = "--app=\"" + url + "\" --window-size=1440,900 --user-data-dir=\"" + Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Alpha360Terminal") + "\"";
                    Process.Start(appWindowInfo);
                    return;
                }
            }

            // Fallback: Default OS browser
            Process.Start(url);
        }
    }
}
