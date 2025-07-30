class ChromeDriverSetup:
    """
    Automates the download and setup of a specific Chrome and Chromedriver version
    for use with Selenium.

    This utility checks for the existence of binaries in the target directory and
    downloads them if missing. It also handles permissions on Unix-based systems
    by setting the executable bit.

    Attributes:
        version (str): The specific Chrome version to download (e.g., '138.0.7204.94').
        arch (str): System architecture (default is 'win64').
        download_dir (str): Base directory where Chrome and Chromedriver will be stored.
        base_uri (str): The base URL to fetch Chrome and Chromedriver archives.
    """

    def __init__(self, version: str, arch: str = 'win64', download_dir: str = '/mnt/mls/selenium'):
        """
        Initializes the setup with a given version, architecture, and target directory.

        Args:
            version (str): Chrome version to set up.
            arch (str): System architecture (e.g., 'linux64', 'mac-arm64').
            download_dir (str): Directory to store the downloaded binaries.
        """
        self.version = version
        self.arch = arch
        self.download_dir = download_dir
        self.base_uri = 'https://storage.googleapis.com/chrome-for-testing-public'

    def setup(self):
        """
        Sets up both Chrome and Chromedriver for the given version and architecture.
        Downloads and extracts archives if they don't already exist, and sets permissions on Unix.
        """
        version_dir = f"{self.download_dir}/{self.version}"
        os.makedirs(version_dir, exist_ok=True)

        if not self._chrome_exists(version_dir):
            print(f'{Fore.GREEN}Setting up Chrome version {self.version}!{Style.RESET_ALL}')
            self.chrome_download_and_extract(version_dir)
            if os.name != 'nt':
                self.make_all_files_executable(version_dir)
        else:
            print(f'{Fore.CYAN}Chrome already exists at {version_dir}, skipping.{Style.RESET_ALL}')

        if not self._chromedriver_exists(version_dir):
            print(f'{Fore.GREEN}Setting up Chromedriver version {self.version}!{Style.RESET_ALL}')
            self.chromedriver_download_and_extract(version_dir)
            if os.name != 'nt':
                self.make_all_files_executable(version_dir)
        else:
            print(f'{Fore.CYAN}Chromedriver already exists at {version_dir}, skipping.{Style.RESET_ALL}')

    @staticmethod
    def make_all_files_executable(path: str):
        """
        Recursively sets executable permissions on all files in the provided path.
        Intended for Unix-based systems only.

        Args:
            path (str): Directory path to apply executable permissions.
        """
        if os.name != 'nt':
            print(f'{Fore.MAGENTA}{Style.BRIGHT}Setting permissions on: {path}{Style.RESET_ALL}')
            for root, _, files in os.walk(path):
                for file in files:
                    full_path = os.path.join(root, file)
                    os.chmod(full_path, os.stat(full_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def _chrome_exists(self, version_dir: str) -> bool:
        """
        Checks if the Chrome binary folder exists for the given version.

        Args:
            version_dir (str): Base directory for the specific Chrome version.

        Returns:
            bool: True if Chrome directory exists, False otherwise.
        """
        expected_dir = os.path.join(version_dir, f"chrome-{self.arch}")
        return os.path.exists(expected_dir)

    def _chromedriver_exists(self, version_dir: str) -> bool:
        """
        Checks if the Chromedriver folder exists for the given version.

        Args:
            version_dir (str): Base directory for the specific Chrome version.

        Returns:
            bool: True if Chromedriver directory exists, False otherwise.
        """
        expected_dir = os.path.join(version_dir, f"chromedriver-{self.arch}")
        return os.path.exists(expected_dir)

    def chrome_download_and_extract(self, base_path: str):
        """
        Downloads and extracts the Chrome archive into the target directory.

        Args:
            base_path (str): The directory where the archive will be extracted.
        """
        zip_filename = f"chrome-{self.arch}.zip"
        zip_url = f"{self.base_uri}/{self.version}/{self.arch}/{zip_filename}"
        zip_path = os.path.join(base_path, zip_filename)

        print(f"Downloading Chrome from {zip_url} to {zip_path}")
        resp = requests.get(zip_url, verify=certifi.where())
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to download Chrome zip (HTTP {resp.status_code})")
        with open(zip_path, 'wb') as f:
            f.write(resp.content)

        print(f"Extracting Chrome to {base_path}")
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(base_path)

        os.remove(zip_path)
        print(f"{Fore.YELLOW}Removed zip: {zip_path}{Style.RESET_ALL}")

    def chromedriver_download_and_extract(self, base_path: str):
        """
        Downloads and extracts the Chromedriver archive into the target directory.

        Args:
            base_path (str): The directory where the archive will be extracted.
        """
        zip_filename = f"chromedriver-{self.arch}.zip"
        zip_url = f"{self.base_uri}/{self.version}/{self.arch}/{zip_filename}"
        zip_path = os.path.join(base_path, zip_filename)

        print(f"Downloading ChromeDriver from {zip_url} to {zip_path}")
        resp = requests.get(zip_url, verify=certifi.where())
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to download ChromeDriver zip (HTTP {resp.status_code})")
        with open(zip_path, 'wb') as f:
            f.write(resp.content)

        print(f"Extracting ChromeDriver to {base_path}")
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(base_path)

        os.remove(zip_path)
        print(f"{Fore.YELLOW}Removed zip: {zip_path}{Style.RESET_ALL}")
