import requests
from tkinter import messagebox

# --- API Configuration ---
OPEN_LIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"
OPEN_LIBRARY_BOOKS_API_URL = "https://openlibrary.org/api/books"

def search_by_name(book_name):
    """Searches Open Library by book name and returns top results."""
    params = {'q': book_name}
    try:
        response = requests.get(OPEN_LIBRARY_SEARCH_URL, params=params, timeout=10) 
        response.raise_for_status() 
        data = response.json()
        return data.get('docs', [])[:5]  
    except requests.exceptions.RequestException as e:
        messagebox.showerror("API Error", f"Failed to search by name: {e}")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred during name search: {e}")
        return None

def search_by_isbn(isbn):
    """Searches Open Library by ISBN."""
    params = {
        'bibkeys': f"ISBN:{isbn}",
        'format': 'json',
        'jscmd': 'data'
    }
    try:
        response = requests.get(OPEN_LIBRARY_BOOKS_API_URL, params=params, timeout=10) 
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("API Error", f"Failed to search by ISBN: {e}")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred during ISBN search: {e}")
        return None
    