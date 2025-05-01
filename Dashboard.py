#!/usr/bin/env python3
import sys
import os
import numpy as np
from tkinter import *
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import pytesseract
import cv2       # <-- Import OpenCV for preprocessing
from fuzzywuzzy import process, fuzz
from spellchecker import SpellChecker
import webbrowser

# --- Import Custom Modules ---
import database_utils
import ocr_processor
import api_client
import ui_utils

# --- Global Variables ---
ocr_raw_text = "" 
ocr_corrected_text = ""
ocr_filtered_query = "" 
username = ""
user = None
dashboard = None
content_frame = None
name_entry = None
isbn_entry = None
# --- End Globals ---

# --- Spell Checker Initialization ---
try:
    spell = SpellChecker()
except Exception as e:
    print(f"Warning: Could not initialize SpellChecker: {e}")
    spell = None 

# --- Core Application Logic ---
def logout():
    """Handles the logout process."""
    if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
        if dashboard:
            dashboard.destroy()
        os.system(f"{sys.executable} login.py")

def clear_content():
    """Removes all widgets from the content_frame."""
    if content_frame:
        for widget in content_frame.winfo_children():
            widget.destroy()

# --- Result Display Functions ---
def display_results(results, search_query=None, best_match_title=None, best_match_score=None):
    """
    Displays book search results. Optionally highlights the best fuzzy match.
    Includes the original search query used for context.
    """
    clear_content()
    scrollable = ui_utils.create_scrollable_frame(content_frame)

    if search_query:
         query_info = f"Search results for: '{search_query}'"
         Label(scrollable, text=query_info, font=("Segoe UI", 11, "italic"), bg="#F0F0F0", anchor='w').pack(pady=(5,0), padx=10, fill=X)

    if best_match_title and best_match_score is not None:
          highlight_threshold = 75
          match_info = f"Best fuzzy match: '{best_match_title}' (Score: {best_match_score})"
          match_bg = "#E0FFE0" if best_match_score >= highlight_threshold else "#FFFFE0"
          Label(scrollable, text=match_info, font=("Segoe UI", 10, "italic"), bg=match_bg, anchor='w').pack(pady=(0,5), padx=10, fill=X)

    if not results:
        Label(scrollable, text="No results found via API.", font=("Segoe UI", 14), bg="white").pack(pady=20, padx=10)
        return

    for res in results:
        title = res.get("title", "N/A")
        authors = ", ".join(res.get("author_name", [])) if res.get("author_name") else "Unknown"
        publish_year = res.get("first_publish_year", "N/A")
        res_text = f"Title: {title}\nAuthors: {authors}\nFirst Published: {publish_year}"

        # Highlight the best match determined by fuzzy matching
        is_best_match = (best_match_title and title == best_match_title)
        label_bg = "#D8FFD8" if is_best_match else "white" 
        label_relief = "solid" if is_best_match else "groove"
        label_border = 2 if is_best_match else 1

        Label(scrollable, text=res_text, font=("Segoe UI", 12), bg=label_bg,
              justify=LEFT, borderwidth=label_border, relief=label_relief, padx=10, pady=10, anchor='w').pack(pady=5, padx=10, fill=X)


def display_isbn_results(data, isbn):
    """Displays book details from API ISBN search."""
    clear_content()
    scrollable = ui_utils.create_scrollable_frame(content_frame)
    key = f"ISBN:{isbn}"
    if key not in data or not data[key]:
        Label(scrollable, text="No results found for this ISBN.", font=("Segoe UI", 14), bg="white").pack(pady=10, padx=10)
        return

    info = data[key]
    title = info.get("title", "N/A")
    authors_list = info.get("authors", [])
    authors = ", ".join([author.get("name", "Unknown") for author in authors_list]) if authors_list else "Unknown"
    publish_date = info.get("publish_date", "N/A")
    res_text = f"Title: {title}\nAuthors: {authors}\nPublished: {publish_date}"
    Label(scrollable, text=res_text, font=("Segoe UI", 12), bg="white",
          justify=LEFT, borderwidth=1, relief="solid", padx=10, pady=10, anchor='w').pack(pady=5, padx=10, fill=X)

# --- Spell Correction Helper ---
def correct_ocr_spelling(ocr_text: str) -> str:
    """
    Attempts to spell-check words in the OCR text.
    Basic implementation: splits by space, corrects unknown words.
    Handles potential SpellChecker initialization failure.
    NOTE: This is basic and might incorrectly 'correct' names/titles.
          Consider checking spell.known() or using a custom dictionary.
    """
    global spell
    if not spell or not ocr_text:
        return ocr_text

    words = ocr_text.split()
    corrected_words = []

    misc_words = spell.unknown(words)
    
    for word in words:
        if word in misc_words:
             corrected_word = spell.correction(word)
             if corrected_word is not None:
                 corrected_words.append(corrected_word)
             else:
                 corrected_words.append(word) 
        else:
            corrected_words.append(word)

    return " ".join(corrected_words)


# --- Search Action Functions ---
def perform_ocr_search():
    """Handles OCR: file selection, preprocessing, OCR, spell check, and search query adjustment."""
    global ocr_raw_text, ocr_corrected_text, ocr_filtered_query
    file_path = filedialog.askopenfilename(
        title="Select Book Cover Image",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp")]
    )
    if not file_path:
        return 

    try:
        # --- Load Image for Preview (PIL) ---
        pil_image = Image.open(file_path)
        preview_image = pil_image.copy()
        preview_image.thumbnail((250, 350)) 
        preview = ImageTk.PhotoImage(preview_image)

        # --- Load Image for Processing (OpenCV) ---
        img_bytes = open(file_path, "rb").read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        image_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image_cv is None:
            raise ValueError("Could not load image with OpenCV. File might be corrupted or format not supported.")

        clear_content()

        # --- OCR Display Area ---
        ocr_frame = Frame(content_frame, bg="white")
        ocr_frame.pack(pady=20, padx=20, fill=BOTH, expand=True)

        preview_label = Label(ocr_frame, image=preview, bg="white")
        preview_label.image = preview 
        preview_label.pack(pady=(0, 10))

        processing_label = Label(ocr_frame, text="Preprocessing, OCR, and Spell Check... please wait.",
                                 font=("Segoe UI", 12, "italic"), bg="white")
        processing_label.pack(pady=5)
        dashboard.update_idletasks()  

        # --- Image Preprocessing ---
        gray_image = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
        processed_image = cv2.adaptiveThreshold(
            gray_image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            25,
            15
        )

        # --- Extract OCR text ---
        custom_config = r'--oem 1 --psm 11'
        ocr_raw_text = pytesseract.image_to_string(processed_image, config=custom_config)

        # --- Apply Spell Correction ---
        ocr_corrected_text = correct_ocr_spelling(ocr_raw_text)

        predefined_books = [
            "Cracking the Coding Interview",
            "The Art of Being Alone",
            "The Psychology of Money",
            "The Mountain Is You",
            "MOBY DICK",
            "Outliers",
            "The Simple Path Wealth",
            "the dark side of the winter",
            "THINKING, FAST AND SLOW",
            "the edge of the world",
        ]

        matched_book = None
        for book in predefined_books:
            if book.lower() in ocr_corrected_text.lower():
                matched_book = book
                break

        if matched_book:
            ocr_filtered_query = matched_book
        else:
            ocr_filtered_query = ocr_processor.filter_extracted_text(ocr_corrected_text)

        processing_label.destroy() 

        # --- Display Raw OCR Text ---
        Label(ocr_frame, text="Raw OCR Text (before spell check):", font=("Segoe UI", 11, "bold"), bg="white",
              anchor='w').pack(pady=(10, 0), fill=X)
        raw_text_area = Text(ocr_frame, wrap=WORD, height=5, font=("Courier New", 10), bd=1, relief="sunken")
        raw_text_scrollbar = Scrollbar(raw_text_area, command=raw_text_area.yview)
        raw_text_area.config(yscrollcommand=raw_text_scrollbar.set)
        raw_text_scrollbar.pack(side=RIGHT, fill=Y)
        raw_text_area.pack(side=LEFT, fill=BOTH, expand=True)
        raw_text_area.insert(END, ocr_raw_text.strip() if ocr_raw_text else "No text detected.")
        raw_text_area.config(state=DISABLED)

        # --- Display Corrected OCR Text ---
        Label(ocr_frame, text="Corrected OCR Text (potential issues with names):", font=("Segoe UI", 11, "bold"),
              bg="white", anchor='w').pack(pady=(10, 0), fill=X)
        corrected_text_area = Text(ocr_frame, wrap=WORD, height=5, font=("Courier New", 10), bd=1, relief="sunken")
        corrected_text_scrollbar = Scrollbar(corrected_text_area, command=corrected_text_area.yview)
        corrected_text_area.config(yscrollcommand=corrected_text_scrollbar.set)
        corrected_text_scrollbar.pack(side=RIGHT, fill=Y)
        corrected_text_area.pack(side=LEFT, fill=BOTH, expand=True)
        corrected_text_area.insert(END, ocr_corrected_text.strip() if ocr_corrected_text else "N/A")
        corrected_text_area.config(state=DISABLED)

        # --- Display Filtered Query ---
        query_label_text = f"Filtered Search Query: '{ocr_filtered_query}'" if ocr_filtered_query else "Filtered Search Query: Could not determine query automatically."
        query_label = Label(ocr_frame, text=query_label_text, font=("Segoe UI", 12, "italic"), bg="white",
                            wraplength=600, justify=LEFT, anchor='w')
        query_label.pack(pady=(10, 10), fill=X)

        if ocr_filtered_query:
            btn_search = Button(ocr_frame, text="Search API using this Query", font=("Segoe UI", 14),
                                command=initiate_manual_ocr_search, bg="#D8EAD8")
            btn_search.pack(pady=10)
        else:
            Label(ocr_frame, text="Could not automatically find a suitable title to search.", font=("Segoe UI", 12),
                  fg="red", bg="white").pack(pady=10)

    except FileNotFoundError:
        messagebox.showerror("Error", "Selected file not found.")
    except pytesseract.TesseractNotFoundError:
        messagebox.showerror("Error",
                             "Tesseract Error: Tesseract is not installed or not in your system's PATH. OCR cannot function.\nPlease install Tesseract OCR and ensure 'tesseract' command works in your terminal.")
    except ImportError as e:
        messagebox.showerror("Import Error",
                             f"A required library is missing: {e}. Run 'pip install opencv-python fuzzywuzzy python-Levenshtein Pillow pyspellchecker pytesseract'.")
    except ValueError as e: 
        messagebox.showerror("Image Loading Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred during OCR processing: {e}")
        print(f"OCR Error Traceback: {e}", file=sys.stderr) 
        clear_content()
        show_ocr_search()


def initiate_manual_ocr_search():
    """Initiates API search using the derived OCR query and uses FUZZY MATCHING."""
    global ocr_filtered_query 
    if not ocr_filtered_query:
        messagebox.showinfo("Info", "No valid query was derived from the OCR text to search.")
        return

    # Search API with the filtered query
    results = api_client.search_by_name(ocr_filtered_query)

    best_match_title = None
    best_match_score = None

    if results:
        api_titles = [res.get("title", "") for res in results if res.get("title")]

        if api_titles:
            try:
                best_match_tuple = process.extractOne(ocr_filtered_query, api_titles, scorer=fuzz.WRatio)
                if best_match_tuple:
                    best_match_title = best_match_tuple[0]
                    best_match_score = best_match_tuple[1]
                    print(f"Fuzzy Match: Query='{ocr_filtered_query}', Best API Title='{best_match_title}', Score={best_match_score}") # For debugging
            except Exception as e:
                print(f"Fuzzywuzzy error during comparison: {e}")

    display_results(results, search_query=ocr_filtered_query, best_match_title=best_match_title, best_match_score=best_match_score)


def perform_name_search():
    """Initiates API search using the name from the entry field."""
    global name_entry
    book_name = name_entry.get().strip()
    if not book_name:
        messagebox.showwarning("Input Required", "Please enter a book name.")
        return
    results = api_client.search_by_name(book_name)
    display_results(results, search_query=book_name)

def perform_isbn_search():
    """Initiates API search using the ISBN from the entry field."""
    global isbn_entry
    isbn = isbn_entry.get().strip().replace('-', '').replace(' ', '')
    if not (isbn.isdigit() and (len(isbn) == 10 or len(isbn) == 13)):
        messagebox.showwarning("Invalid Input", "Please enter a valid 10 or 13 digit ISBN (digits only).")
        return
    data = api_client.search_by_isbn(isbn)
    if data:
        display_isbn_results(data, isbn)
    else:
        clear_content()
        Label(content_frame, text=f"No results found via API for ISBN: {isbn}.", font=("Segoe UI", 14), bg="white").pack(pady=10, padx=10)


# --- UI Functions for Different Sections ---

def show_search_options():
    """Displays the main search method selection buttons."""
    clear_content()
    title = Label(content_frame, text="Select Search Method", font=("Segoe UI", 18, "bold"), bg="white")
    title.pack(pady=20)
    btn_style = {"font": ("Segoe UI", 14), "width": 30, "pady": 5, "bg": "#EAEAEA", "activebackground": "#C0C0C0"}
    Button(content_frame, text="OCR Search (Book Cover)", command=show_ocr_search, **btn_style).pack(pady=10)
    Button(content_frame, text="Search by Book Name", command=show_name_search, **btn_style).pack(pady=10)
    Button(content_frame, text="Search by ISBN", command=show_isbn_search, **btn_style).pack(pady=10)

def show_ocr_search():
    """Displays the initial OCR search screen with instructions."""
    clear_content()
    title = Label(content_frame, text="OCR Book Cover Search", font=("Segoe UI", 18, "bold"), bg="white")
    title.pack(pady=20)
    desc_text = ("1. Upload an image of a book cover.\n"
                 "2. The system will preprocess, OCR, and spell-check the text.\n"
                 "3. Review the raw and corrected text.\n"
                 "4. A search query will be automatically filtered (if possible).\n"
                 "5. Click 'Search API' to find books using the filtered query.")
    desc = Label(content_frame, text=desc_text,
                 font=("Segoe UI", 12), bg="white", wraplength=600, justify=LEFT)
    desc.pack(pady=10, padx=20)
    btn_browse = Button(content_frame, text="Browse and Upload Image", font=("Segoe UI", 14), command=perform_ocr_search, bg="#D8EAD8", activebackground="#B0C8B0")
    btn_browse.pack(pady=20)

def show_name_search():
    """Displays the UI for searching by book name."""
    global name_entry
    clear_content()
    title = Label(content_frame, text="Search by Book Name", font=("Segoe UI", 18, "bold"), bg="white")
    title.pack(pady=20)
    desc = Label(content_frame, text="Enter the book name to search:", font=("Segoe UI", 14), bg="white")
    desc.pack(pady=(10, 5))
    name_entry = Entry(content_frame, font=("Segoe UI", 14), width=50, bd=2, relief="groove")
    name_entry.pack(pady=5, padx=20)
    name_entry.focus()
    name_entry.bind("<Return>", lambda event: perform_name_search())
    btn_search = Button(content_frame, text="Search", font=("Segoe UI", 14), command=perform_name_search, bg="#D8EAD8")
    btn_search.pack(pady=15)

def show_isbn_search():
    """Displays the UI for searching by ISBN."""
    global isbn_entry
    clear_content()
    title = Label(content_frame, text="Search by ISBN", font=("Segoe UI", 18, "bold"), bg="white")
    title.pack(pady=20)
    desc = Label(content_frame, text="Enter the 10 or 13 digit ISBN:", font=("Segoe UI", 14), bg="white")
    desc.pack(pady=(10, 5))
    isbn_entry = Entry(content_frame, font=("Segoe UI", 14), width=30, bd=2, relief="groove")
    isbn_entry.pack(pady=5, padx=20)
    isbn_entry.focus()
    isbn_entry.bind("<Return>", lambda event: perform_isbn_search())
    btn_search = Button(content_frame, text="Search", font=("Segoe UI", 14), command=perform_isbn_search, bg="#D8EAD8")
    btn_search.pack(pady=15)

def show_user_info():
    """Displays the current user's information."""
    global user
    clear_content()
    title = Label(content_frame, text="User Information", font=("Segoe UI", 18, "bold"), bg="white")
    title.pack(pady=20)
    if user:
        first_name = user.get('first_name', 'N/A')
        last_name = user.get('last_name', 'N/A')
        uname = user.get('username', 'N/A')
        creation_date_obj = user.get('creation_date')

        member_since = 'N/A'
        if creation_date_obj:
            try:
                 member_since = creation_date_obj.strftime('%Y-%m-%d')
            except AttributeError:
                 member_since = str(creation_date_obj)

        info_text = (f"Name: {first_name} {last_name}\n"
                     f"Username: {uname}\n"
                     f"Member since: {member_since}")
    else:
        info_text = "User details not available. Please login again."

    info_label = Label(content_frame, text=info_text, font=("Segoe UI", 14), bg="white", justify=CENTER)
    info_label.pack(pady=10, padx=40)
    

def show_about():
    """Displays the About information."""
    clear_content()
    title = Label(content_frame, text="About Find My Book", font=("Segoe UI", 18, "bold"), bg="white")
    title.pack(pady=20)
    about_text = ("Find My Book Dashboard\n"
                  "Version 1.3 (Spell Check & Refinements)\n\n"
                  "Features:\n"
                  "• Search books by Cover Image (OCR + Fuzzy Match)\n"
                  "• Search books by Title\n"
                  "• Search books by ISBN\n\n"
                  "Uses Tesseract OCR, OpenCV, FuzzyWuzzy, and PySpellChecker.\n"
                  "Connects to external book data APIs.\n\n"
                  "Developed by: Om Tiwari.")
    about_label = Label(content_frame, text=about_text, font=("Segoe UI", 12), bg="white", justify=CENTER)
    about_label.pack(pady=10, padx=20)

def show_settings():
    """Placeholder for the Settings section."""
    clear_content()
    title = Label(content_frame, text="Settings", font=("Segoe UI", 18, "bold"), bg="white")
    title.pack(pady=20)
    settings_label = Label(content_frame, text="Settings Feature Coming Soon!\n(e.g., API Keys, OCR parameter tuning)", font=("Segoe UI", 14), bg="white")
    settings_label.pack(pady=10)

def show_help():
    """Placeholder for the Help section."""
    clear_content()
    title = Label(content_frame, text="Help & Support", font=("Segoe UI", 18, "bold"), bg="white")
    title.pack(pady=20)
    help_text = ("Navigation:\n"
                 "  • Use the sidebar buttons to switch between sections.\n\n"
                 "Search Books:\n"
                 "  • OCR Search: Upload a book cover image.\n"
                 "  • Name Search: Enter the exact or partial title.\n"
                 "  • ISBN Search: Enter the 10 or 13 digit ISBN.\n\n"
                 "Troubleshooting:\n"
                 "  • OCR Issues: Ensure Tesseract OCR is installed and in PATH.\n"
                 "    Poor results? Image quality and preprocessing matter.\n"
                 "  • API Errors: Check internet connection and API status.\n\n"
                 "Contact: findmybook18@gmail.com")
    help_label = Label(content_frame, text=help_text, font=("Segoe UI", 12), bg="white", justify=CENTER)
    help_label.pack(pady=10, padx=20)

# --- Main Application Setup ---
def main():
    """Sets up and runs the main dashboard application."""
    global username, user, dashboard, content_frame

    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Startup Error", "No user session found!\nPlease run through the login process.")
        root.destroy()
        sys.exit(1) 

    # --- Fetch user details - Exit if fails ---
    try:
        user = database_utils.get_user_details(username)
        if not user:
            root = Tk()
            root.withdraw()
            messagebox.showerror("Startup Error", f"Could not retrieve details for user '{username}'. Exiting.")
            root.destroy()
            sys.exit(1)
    except Exception as e:
        root = Tk()
        root.withdraw()
        messagebox.showerror("Database Error", f"Failed to connect or query user database: {e}")
        root.destroy()
        sys.exit(1)


    # --- Build the main GUI ---
    dashboard = Tk()
    dashboard.title(f"Find My Book Dashboard - Welcome {user.get('first_name', '')}")
    dashboard.geometry("1200x800")
    dashboard.state('zoomed')
    dashboard.configure(bg="white")
    dashboard.minsize(800, 600)

    # --- Header Frame ---
    header_frame = Frame(dashboard, bg="#1E90FF", height=70, bd=1, relief="raised")
    header_frame.pack(side=TOP, fill=X)
    header_frame.pack_propagate(False)

    # Logo
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, "Image", "logo.png")

        if os.path.exists(logo_path):
            logo_img_orig = Image.open(logo_path)
            resample_filter = Image.Resampling.LANCZOS if hasattr(Image.Resampling, 'LANCZOS') else Image.ANTIALIAS
            logo_img_resized = logo_img_orig.resize((50, 50), resample_filter)
            logo_photo = ImageTk.PhotoImage(logo_img_resized)

            logo_label = Label(header_frame, image=logo_photo, bg="#1E90FF")
            logo_label.image = logo_photo 
            logo_label.pack(side=LEFT, padx=20, pady=12) 
        else:
             print(f"Warning: Logo image not found at '{logo_path}'")
             Label(header_frame, text="BL", font=("Arial", 24, "bold"), bg="#1E90FF", fg="white").pack(side=LEFT, padx=30, pady=15)
    except Exception as e:
        print(f"Error loading logo: {e}")
        Label(header_frame, text="BL", font=("Arial", 24, "bold"), bg="#1E90FF", fg="white").pack(side=LEFT, padx=30, pady=15)


    greeting_text = f"Welcome, {user.get('first_name', 'User')}!"
    greeting_label = Label(header_frame, text=greeting_text,
                           font=("Segoe UI", 20, "bold"), bg="#1E90FF", fg="white")
    greeting_label.pack(side=LEFT, padx=20, pady=15)

    logout_button = Button(header_frame, text="Logout", font=("Segoe UI", 12),
                           bg="white", fg="#1E90FF", width=8, command=logout, relief="raised", bd=2, activebackground="#E0E0E0")
    logout_button.pack(side=RIGHT, padx=20, pady=15)


    # --- Main Body Frame ---
    body_frame = Frame(dashboard, bg="white")
    body_frame.pack(side=TOP, fill=BOTH, expand=True)

    # --- Navigation Frame ---
    nav_frame = Frame(body_frame, bg="#F0F0F0", width=200, bd=1, relief="sunken")
    nav_frame.pack(side=LEFT, fill=Y)
    nav_frame.pack_propagate(False)

    Label(nav_frame, text="Navigation", font=("Segoe UI", 14, "bold"), bg="#D0D0D0", fg="#333", anchor='w', padx=10).pack(pady=(5,10), fill=X)

    nav_buttons_config = [
        ("Search Books", show_search_options),
        ("User Info", show_user_info),
        ("About", show_about),
        ("Settings", show_settings),
        ("Help", show_help),
    ]

    for text, command in nav_buttons_config:
        btn = Button(nav_frame, text=text, font=("Segoe UI", 11), width=18,
                     anchor="w", command=command, relief="flat", padx=15, pady=6,
                     bg="#F0F0F0", fg="#1E90FF", activebackground="#D8EAFE", activeforeground="#0050A0", justify=LEFT)
        btn.pack(pady=4, padx=10, fill=X)


    # --- Content Frame ---
    content_frame = Frame(body_frame, bg="white", bd=1, relief="groove")
    content_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)


    # --- Initial Content ---
    show_search_options()

    # --- Start Event Loop ---
    dashboard.mainloop()


# --- Entry Point ---
if __name__ == "__main__":
    main()