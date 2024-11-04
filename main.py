from tkinter import Tk

from ui import OptionCalculatorUI


def on_closing():
    if app.market_data_tab.canvas:  # Check canvas in the MarketDataTab class
        app.market_data_tab.canvas.get_tk_widget().destroy()  # Destroy the canvas widget if it exists
    root.destroy()  # Proceed to close the app


def reset_cache(event=None):
    app.market_data_tab.data_fetcher.clear_cache()


def show_date_input(event=None):
    app.market_data_tab.show_date_input_dialog()


def toggle_projection_line(event=None):
    app.market_data_tab.toggle_projection_line()


def main():
    global root, app
    root = Tk()
    root.title("OptiCal - Option Calculator")

    # Get the screen width and height, and set the window size to match
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}")

    app = OptionCalculatorUI(root)

    # Bind the window close event to the on_closing function
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Bind secret key combination to reset cache (e.g., Command+R)
    root.bind("<Command-r>", reset_cache)

    # Bind Command+D to show date input dialog
    root.bind("<Command-d>", show_date_input)

    # Bind Command+p to show/hide projection
    root.bind("<Command-p>", toggle_projection_line)

    root.mainloop()


if __name__ == "__main__":
    main()
