# 📚 Find My Book – Smart Book Search Tool

Find My Book is a desktop application designed to help users search for books using various methods, including a cover image, title, or ISBN number. It leverages Tesseract OCR for image-to-text extraction, fuzzy text matching for handling typos or unclear OCR results, and the Open Library API to fetch book details. The graphical user interface (GUI) is built with Python's Tkinter library, and it includes MySQL integration for user authentication and management.

## 🚀 Features

* **🔍 OCR-Based Search:** Upload a book cover image. The application extracts text (like the title) using Tesseract OCR (powered by OpenCV for image processing) and searches for matching books.
* **🖊️ Fuzzy Matching:** Intelligently handles potential spelling mistakes from OCR output or manual input using fuzzy search algorithms to find the most relevant book matches.
* **📚 Search by Name or ISBN:** Allows users to directly search for books by typing the title or the 10/13-digit ISBN.
* **👤 Login/Signup System:** Provides secure, authenticated access. User credentials and data are stored in a MySQL database.
* **💡 User Dashboard:** Features an intuitive dashboard with clear sections for initiating searches, viewing user information, accessing help guides, and adjusting settings.
* **📊 Loading Progress Bar:** Enhances the user experience by showing a progress bar during potentially long operations, like initial loading or complex searches, transitioning smoothly to the dashboard.

## 🧰 Technologies Used

* **Python 3**
* **Tkinter:** For building the graphical user interface.
* **Tesseract OCR:** For optical character recognition from images.
* **OpenCV (`opencv-python`):** For image processing tasks required before OCR.
* **FuzzyWuzzy (`fuzzywuzzy`, `python-Levenshtein`):** For approximate string matching.
* **PySpellChecker (`pyspellchecker`):** For correcting spelling errors.
* **Pillow (`pillow`):** For image handling within the Python application.
* **MySQL (`mysql-connector-python`):** For database interactions (user authentication, etc.).
* **Open Library API:** For fetching comprehensive book data.
* **(Potentially) `requests`:** Often used for making API calls (like to Open Library). Ensure it's installed if needed (`pip install requests`).

## 🔧 Setup Instructions

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/omtiwari17/Find_My_Book.git](https://github.com/omtiwari17/Find_My_Book.git)
    cd find-my-book
    ```

2.  **Install Required Python Libraries**
    ```bash
    pip install opencv-python pytesseract fuzzywuzzy python-Levenshtein pyspellchecker pillow mysql-connector-python requests
    ```
    *(Note: Added `requests` as it's commonly needed for API interaction. Remove if not used.)*

3.  **Install Tesseract OCR Engine**
    * **Windows:** Download the installer from the [Tesseract at UB Mannheim page](https://github.com/UB-Mannheim/tesseract/wiki) or other official sources. **Crucially, add the Tesseract installation directory (e.g., `C:\Program Files\Tesseract-OCR`) to your system's `PATH` environment variable** so the command line and Python can find `tesseract.exe`.
    * **macOS:** Use Homebrew: `brew install tesseract`
    * **Linux (Debian/Ubuntu):** `sudo apt update && sudo apt install tesseract-ocr`
    * **Language Data:** Ensure you have the necessary language data installed (e.g., English). For Linux: `sudo apt install tesseract-ocr-eng`. Windows installers usually provide an option during setup.

4.  **Configure Tesseract Path (If Necessary)**
    If `pytesseract` cannot automatically find your Tesseract installation (especially on Windows), you might need to specify the path in your Python code:
    ```python
    import pytesseract
    # Example path for Windows, adjust as necessary
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    ```

5.  **Set Up MySQL Database**
    * Ensure you have a MySQL server installed and running.
    * Connect to your MySQL server (using a tool like MySQL Workbench, phpMyAdmin, or the command line).
    * Create a new database, preferably named `booklens`:
        ```sql
        CREATE DATABASE booklens;
        ```
    * Use the database:
        ```sql
        USE booklens;
        ```
    * Create the required table `user_detail`. Define columns appropriate for storing user information (e.g., `id`, `username`, `password_hash`, `email`, `created_at`). Example:
        ```sql
        CREATE TABLE user_detail (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            -- Add other fields as needed
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ```
    * **Crucially:** Update the database connection credentials (host, username, password, database name) in your Python project, likely within a configuration file or a dedicated module (e.g., `database_utils.py`). **Do not commit sensitive credentials directly into your Git repository.** Use environment variables or a configuration file listed in `.gitignore`.

6.  **Run the Application**
    Execute the main Python script (assuming `ProgressBar.py` is the entry point that loads the application):
    ```bash
    python ProgressBar.py
    ```

## ✍️ Authors

* **Om Tiwari**

## 📌 License

This project is open-source and available for use and modification.

*(It's recommended to add a specific open-source license file (e.g., `LICENSE.md`) to your repository, such as the MIT License or Apache License 2.0, to clarify usage rights and limitations.)*
